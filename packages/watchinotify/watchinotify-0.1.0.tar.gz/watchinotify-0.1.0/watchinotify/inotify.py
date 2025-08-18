from collections.abc import Iterable
import ctypes
from ctypes import c_char_p, c_int, c_uint32
from enum import IntFlag, auto
import errno
import fnmatch
import os
from pathlib import Path
import re
import select
import struct
import threading
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable


# From /usr/include/linux/inotify.h
class InotifyConstants(IntFlag):
    # user-space events
    IN_ACCESS = 0x00000001  # file was accessed
    IN_MODIFY = 0x00000002  # file was modified
    IN_ATTRIB = 0x00000004  # meta-data changed
    IN_CLOSE_WRITE = 0x00000008  # writable file was closed
    IN_CLOSE_NOWRITE = 0x00000010  # unwritable file closed
    IN_OPEN = 0x00000020  # file was opened
    IN_MOVED_FROM = 0x00000040  # file was moved from x
    IN_MOVED_TO = 0x00000080  # file was moved to y
    IN_CREATE = 0x00000100  # subfile was created
    IN_DELETE = 0x00000200  # subfile was deleted
    IN_DELETE_SELF = 0x00000400  # self was deleted
    IN_MOVE_SELF = 0x00000800  # self was moved

    # events sent by the kernel to a watch
    IN_UNMOUNT = 0x00002000  # backing file system was unmounted
    IN_Q_OVERFLOW = 0x00004000  # event queued overflowed
    IN_IGNORED = 0x00008000  # file was ignored

    # helper user-space events
    IN_CLOSE = IN_CLOSE_WRITE | IN_CLOSE_NOWRITE  # close
    IN_MOVE = IN_MOVED_FROM | IN_MOVED_TO  # moves

    # special flags
    IN_ONLYDIR = 0x01000000  # only watch the path if it's a directory
    IN_DONT_FOLLOW = 0x02000000  # do not follow a symbolic link
    IN_EXCL_UNLINK = 0x04000000  # Exclude events on unlinked objects
    IN_MASK_ADD = 0x20000000  # add to the mask of an existing watch
    IN_ISDIR = 0x40000000  # event occurred against directory
    IN_ONESHOT = 0x80000000  # only send event once

    # All of the events - we build the list by hand so that we can add flags in
    # the future and not break backward compatibility.  Apps will get only the
    # events that they originally wanted.  Be sure to add new events here!
    IN_ALL_EVENTS = (IN_ACCESS | IN_MODIFY | IN_ATTRIB | IN_CLOSE_WRITE | IN_CLOSE_NOWRITE | IN_OPEN | IN_MOVED_FROM |
                     IN_MOVED_TO | IN_DELETE | IN_CREATE | IN_DELETE_SELF | IN_MOVE_SELF)


class InotifyInitFlag(IntFlag):
    IN_NONBLOCK = 0x00000800
    IN_CLOEXEC = 0x00080000


class Libc:
    def __init__(self, libc=None):
        self._libc = ctypes.CDLL(None) if libc is None else libc
        if not hasattr(self._libc, 'inotify_init') or not hasattr(self._libc, 'inotify_add_watch') or not hasattr(
                self._libc, 'inotify_rm_watch'):
            raise RuntimeError(f'Unsupported libc found: {self._libc._name}')  # noqa: SLF001
        self.inotify_add_watch = ctypes.CFUNCTYPE(c_int, c_int, c_char_p, c_uint32, use_errno=True)(
            ('inotify_add_watch', self._libc))
        self.inotify_init = ctypes.CFUNCTYPE(c_int, use_errno=True)(('inotify_init', self._libc))
        self.inotify_rm_watch = ctypes.CFUNCTYPE(c_int, c_int, c_uint32, use_errno=True)(
            ('inotify_rm_watch', self._libc))


class InotifyEventStruct(ctypes.Structure):
    _fields_ = (('wd', c_int), ('mask', c_uint32), ('cookie', c_uint32), ('len', c_uint32))


class Event(IntFlag):
    OPENED = auto()
    MODIFIED = auto()
    DELETED = auto()
    MOVED = auto()
    CLOSED = auto()
    SUB_CREATED = auto()
    SUB_DELETED = auto()
    SUB_MOVED = auto()


class FileEvent(IntFlag):
    OPENED = Event.OPENED.value
    MODIFIED = Event.MODIFIED.value
    DELETED = Event.DELETED.value
    MOVED = Event.MOVED.value
    CLOSED = Event.CLOSED.value

    ALL = OPENED | MODIFIED | DELETED | MOVED | CLOSED


class FolderEvent(IntFlag):
    DELETED = Event.DELETED.value
    MOVED = Event.MOVED.value
    SUB_CREATED = Event.SUB_CREATED.value
    SUB_DELETED = Event.SUB_DELETED.value
    SUB_MOVED = Event.SUB_MOVED.value

    ALL = DELETED | MOVED | SUB_CREATED | SUB_DELETED | SUB_MOVED


class Watcher:
    LIBC = Libc()
    EVENT_SIZE = ctypes.sizeof(InotifyEventStruct)
    EVENT_NAME_MAX = 1024
    EVENT_BUFFER_SIZE = EVENT_SIZE + EVENT_NAME_MAX + 1

    def __init__(self, event_type: Event | FileEvent | FolderEvent | None = None,
                 exclude_patterns: Iterable[str] | None = None, recursive=True):
        self.exclude_regexes = None if exclude_patterns is None else [
            re.compile(fnmatch.translate(pattern)) for pattern in exclude_patterns]

        inotify_fd = self.LIBC.inotify_init()
        if inotify_fd == -1:
            Watcher._raise_error()
        self._inotify_fd = inotify_fd
        self._watch_descriptors: dict[Path, int] = {}
        self._watch_paths: dict[int, Path] = {}
        self._move_cache: dict[int, tuple[Path | None, bytes]] = {}

        self._stop_r, self._stop_w = os.pipe()
        self._poll = select.poll()
        self._poll.register(self._inotify_fd, select.POLLIN)
        self._poll.register(self._stop_r, select.POLLIN)

        self._file_event = FileEvent(event_type.value) & FileEvent.ALL if event_type is not None else (
            FileEvent.MODIFIED | FileEvent.DELETED | FileEvent.MOVED)
        self._file_mask = self._create_file_mask(self._file_event)
        self._folder_event = FolderEvent(event_type.value) & FolderEvent.ALL if event_type is not None else (
            FolderEvent.DELETED | FolderEvent.MOVED | FolderEvent.SUB_CREATED | FolderEvent.SUB_DELETED
            | FolderEvent.SUB_MOVED)
        if recursive:
            self._folder_event |= FolderEvent.SUB_CREATED | FolderEvent.SUB_MOVED
        self._folder_mask = self._create_folder_mask(self._folder_event)
        self._recursive = recursive

        self.callback: Callable[[Path | None, Event | FileEvent | FolderEvent, bytes], None] | None = None

        self._thread = threading.Thread(target=self._run)
        self._thread.start()

    def __del__(self):
        self.close()

    def __enter__(self):
        return self

    def __exit__(self, _exc, _value, _tb):
        self.close()

    def close(self):
        if self._inotify_fd > 0:
            os.write(self._stop_w, b' ')
            self._thread.join(timeout=1.0)
            for wd in self._watch_paths:
                self._remove_watch(wd, ignore_error=True)
            self._watch_descriptors.clear()
            self._watch_paths.clear()
            os.close(self._inotify_fd)
            self._inotify_fd = 0

    @staticmethod
    def _raise_error():
        err = ctypes.get_errno()
        if err == errno.ENOSPC:
            raise OSError(errno.ENOSPC, 'inotify watch limit reached')
        if err == errno.EMFILE:
            raise OSError(errno.EMFILE, 'inotify instance limit reached')
        raise OSError(err, os.strerror(err))

    @staticmethod
    def _create_event(mask: InotifyConstants) -> Event:
        event_type = Event(0)
        if InotifyConstants.IN_OPEN in mask:
            event_type |= Event.OPENED
        if InotifyConstants.IN_MODIFY in mask:
            event_type |= Event.MODIFIED
        if InotifyConstants.IN_DELETE_SELF in mask:
            event_type |= Event.DELETED
        if InotifyConstants.IN_MOVE_SELF in mask:
            event_type |= Event.MOVED
        if mask & InotifyConstants.IN_CLOSE:
            event_type |= Event.CLOSED
        if InotifyConstants.IN_CREATE in mask:
            event_type |= Event.SUB_CREATED
        if InotifyConstants.IN_DELETE in mask:
            event_type |= Event.SUB_DELETED
        if InotifyConstants.IN_MOVED_TO in mask:
            event_type |= Event.SUB_MOVED
        return event_type

    @staticmethod
    def _create_folder_mask(folder_event: FolderEvent) -> InotifyConstants:
        mask = InotifyConstants(0)
        if FolderEvent.DELETED in folder_event:
            mask |= InotifyConstants.IN_DELETE_SELF
        if FolderEvent.MOVED in folder_event:
            mask |= InotifyConstants.IN_MOVE_SELF
        if FolderEvent.SUB_CREATED in folder_event:
            mask |= InotifyConstants.IN_CREATE
        if FolderEvent.SUB_DELETED in folder_event:
            mask |= InotifyConstants.IN_DELETE
        if FolderEvent.SUB_MOVED in folder_event:
            mask |= InotifyConstants.IN_MOVE
        return mask

    @staticmethod
    def _create_file_mask(file_event: FileEvent) -> InotifyConstants:
        mask = InotifyConstants(0)
        if FileEvent.OPENED in file_event:
            mask |= InotifyConstants.IN_OPEN
        if FileEvent.MODIFIED in file_event:
            mask |= InotifyConstants.IN_MODIFY
        if FileEvent.DELETED in file_event:
            mask |= InotifyConstants.IN_DELETE_SELF
        if FileEvent.MOVED in file_event:
            mask |= InotifyConstants.IN_MOVE_SELF
        if FileEvent.CLOSED in file_event:
            mask |= InotifyConstants.IN_CLOSE
        return mask

    def _remove_watch(self, wd: int, ignore_error=False):
        if self.LIBC.inotify_rm_watch(self._inotify_fd, wd) == -1 and not ignore_error:
            Watcher._raise_error()

    def _run(self):
        event_buffer = b''

        def parse_buffer():
            nonlocal event_buffer
            while len(event_buffer) >= Watcher.EVENT_SIZE:
                # From /usr/include/linux/inotify.h
                # struct inotify_event {
                #     __s32  wd;     /* watch descriptor */
                #     __u32  mask;   /* watch mask */
                #     __u32  cookie; /* cookie to synchronize two events */
                #     __u32  len;    /* length (including nulls) of name */
                #     char   name[]; /* stub for possible name */
                # };
                # name[] is optional so its size may be 0, also it is null-terminated
                wd, mask_value, cookie, length = struct.unpack_from('iIII', event_buffer)
                if len(event_buffer) < Watcher.EVENT_SIZE + length:
                    break

                name = event_buffer[
                    Watcher.EVENT_SIZE:Watcher.EVENT_SIZE + length].rstrip(b'\0') if length > 0 else b''
                event_buffer = event_buffer[Watcher.EVENT_SIZE + length:]
                path = self._watch_paths.get(wd, None)
                mask = InotifyConstants(mask_value)

                if InotifyConstants.IN_MOVED_FROM in mask:
                    self._move_cache[cookie] = (path, name)
                    continue
                if InotifyConstants.IN_IGNORED in mask and wd in self._watch_paths:
                    self._watch_descriptors.pop(self._watch_paths.pop(wd))
                    continue

                if InotifyConstants.IN_MOVE_SELF in mask:
                    self._watch_descriptors.pop(self._watch_paths.pop(wd))
                    self._remove_watch(wd)
                if InotifyConstants.IN_MOVED_TO in mask and cookie in self._move_cache and path is not None:
                    previous_name = self._move_cache.pop(cookie)[1]
                    if self._recursive:
                        self._move_all_subpath(
                            (path / previous_name.decode()).resolve(), (path / name.decode()).resolve())
                    name = previous_name + b' -> ' + name
                if self._recursive and path is not None and (
                        InotifyConstants.IN_CREATE in mask or InotifyConstants.IN_MOVED_TO & mask):
                    self.watch([path / name.decode()])

                if self.callback is not None and path is not None:
                    self.callback(path, self._create_event(mask), name)

        while self._inotify_fd:
            events = next(zip(*self._poll.poll(), strict=False))
            if self._inotify_fd in events:
                event_buffer += os.read(self._inotify_fd, Watcher.EVENT_BUFFER_SIZE)
                parse_buffer()
            if self._stop_r in events:
                break

    def _move_all_subpath(self, previous_root_path: Path, new_root_path: Path):
        cached_paths = list(self._watch_descriptors.keys())
        for previous_path in cached_paths:
            if str(previous_path).startswith(str(previous_root_path)):
                new_path = new_root_path / previous_path.relative_to(previous_root_path)
                test_wd = self._watch_descriptors.pop(previous_path)
                self._watch_descriptors[new_path] = test_wd
                self._watch_paths[test_wd] = new_path

    def watch(self, paths: Iterable[Path]):
        to_watch_paths = {path.resolve() for path in paths} if self.exclude_regexes is None else {
            path.resolve() for path in paths if not any(reg.match(str(path)) for reg in self.exclude_regexes)}

        if self._recursive:
            path_queue = [path for path in paths if path.is_dir()]
            while path_queue:
                current_path = path_queue.pop()
                for sub_path in current_path.iterdir():
                    if sub_path not in to_watch_paths:
                        resolved_path = sub_path.resolve()
                        if self.exclude_regexes is not None and any(
                                reg.match(str(resolved_path)) for reg in self.exclude_regexes):
                            continue
                        to_watch_paths.add(resolved_path)
                        if resolved_path.is_dir():
                            path_queue.append(resolved_path)

        for current_path in to_watch_paths:
            final_path = current_path.resolve()
            if final_path in self._watch_descriptors:
                continue

            mask = self._folder_mask if final_path.is_dir() else self._file_mask
            if not mask.value:
                continue
            wd = self.LIBC.inotify_add_watch(self._inotify_fd, bytes(final_path), mask.value)
            if wd == -1:
                Watcher._raise_error()
            self._watch_descriptors[final_path] = wd
            self._watch_paths[wd] = final_path

    def unwatch(self, path: Path):
        final_path = path.resolve()
        if final_path not in self._watch_descriptors:
            return
        wd = self._watch_descriptors[final_path]
        self._remove_watch(wd)
        self._watch_descriptors.pop(final_path)
        self._watch_paths.pop(wd)

    def watched_paths(self) -> list[Path]:
        return list(self._watch_descriptors.keys())
