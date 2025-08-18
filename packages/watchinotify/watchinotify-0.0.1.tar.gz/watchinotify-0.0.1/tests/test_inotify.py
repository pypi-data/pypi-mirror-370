from pathlib import Path
import shutil
import tempfile
import tomllib
import threading
import time

import pytest

import watchinotify
from watchinotify.inotify import FileEvent, FolderEvent, Libc, Watcher


def test_package_path():
    assert Path(watchinotify.__file__).parent.resolve() == (Path(__file__).parents[1] / 'watchinotify').resolve()


def test_package_version():
    expected_version = tomllib.loads(
        (Path(__file__).parents[1] / 'pyproject.toml').read_text(encoding='utf-8'))['project']['version']
    assert watchinotify.__version__ == expected_version


def test_wrong_libc():
    class FakeLibc:
        _name = 'fake'

    with pytest.raises(RuntimeError):
        Libc(libc=FakeLibc())


def test_watch_file():
    with tempfile.TemporaryDirectory() as temp_root:
        root_path = Path(temp_root)
        with Watcher(recursive=False) as watcher:
            new_file = root_path / 'test.txt'
            new_file.touch()
            watcher.watch([new_file])
            assert watcher.watched_paths() == [new_file.resolve()]


def test_watch_file_recursive():
    with tempfile.TemporaryDirectory() as temp_root:
        root_path = Path(temp_root)
        with Watcher(recursive=True) as watcher:
            new_file = root_path / 'test.txt'
            new_file.touch()
            watcher.watch([new_file])
            assert watcher.watched_paths() == [new_file.resolve()]


def test_watch_file_double():
    with tempfile.TemporaryDirectory() as temp_root:
        root_path = Path(temp_root)
        with Watcher(recursive=False) as watcher:
            new_file = root_path / 'test.txt'
            new_file.touch()
            watcher.watch([new_file])
            watcher.watch([new_file])
            assert watcher.watched_paths() == [new_file.resolve()]


def test_unwatch_file():
    with tempfile.TemporaryDirectory() as temp_root:
        root_path = Path(temp_root)
        with Watcher(recursive=False) as watcher:
            new_file = root_path / 'test.txt'
            new_file.touch()
            watcher.watch([new_file])
            watcher.unwatch(new_file)
            assert len(watcher.watched_paths()) == 0


def test_unwatch_missing():
    with tempfile.TemporaryDirectory() as temp_root:
        root_path = Path(temp_root)
        with Watcher() as watcher:
            new_file = root_path / 'test.txt'
            watcher.unwatch(new_file)


def test_wrong_unwatch_missing():
    with (Watcher() as watcher, pytest.raises(OSError)):
        watcher._remove_watch(666)


def _watch_base(action, event_type, event_count: int, path: Path, exclude_patterns: list[str],
                recursive: bool) -> tuple[list[Path], list[tuple[Path | None, FileEvent, bytes]]]:
    events: list[tuple[Path | None, FileEvent, bytes]] = []
    received = threading.Event()

    def callback(path: Path | None, event, name: bytes):
        nonlocal events, event_count, received
        events.append((path, event, name))
        if len(events) == event_count:
            received.set()

    watched_paths: list[Path] = []
    with Watcher(event_type=event_type, exclude_patterns=exclude_patterns, recursive=recursive) as watcher:
        watcher.watch([path])
        watcher.callback = callback
        action(path)
        if event_count:
            received.wait(timeout=1)
        watched_paths = watcher.watched_paths()
    return watched_paths, events


def _watch_file(action, event_type, event_count: int) -> tuple[list[Path], list[tuple[Path | None, FileEvent, bytes]]]:
    with tempfile.TemporaryDirectory() as temp_root:
        root_path = Path(temp_root)
        path = root_path / 'test.txt'
        path.touch()
        return _watch_base(action, event_type, event_count, path, [], False)


def _watch_folder(action, event_type, event_count: int) -> tuple[
        list[Path], list[tuple[Path | None, FileEvent, bytes]]]:
    with tempfile.TemporaryDirectory() as temp_root:
        root_path = Path(temp_root, 'test')
        root_path.mkdir()
        return _watch_base(action, event_type, event_count, root_path, [], False)


def test_watch_file_open():
    save_path = Path()

    def action(path: Path):
        nonlocal save_path
        save_path = path
        path.read_text(encoding='utf-8')

    watched_paths, events = _watch_file(action, FileEvent.OPENED, 1)
    assert len(events) == 1
    event = events[0]
    assert event[0] == save_path
    assert event[1] == FileEvent.OPENED
    assert event[2] == b''
    assert watched_paths == [save_path]


def test_watch_file_close_nowrite():
    save_path = Path()

    def action(path: Path):
        nonlocal save_path
        save_path = path
        path.read_text(encoding='utf-8')

    watched_paths, events = _watch_file(action, FileEvent.CLOSED, 1)
    assert len(events) == 1
    event = events[0]
    assert event[0] == save_path
    assert event[1] == FileEvent.CLOSED
    assert event[2] == b''
    assert watched_paths == [save_path]


def test_watch_file_close_write():
    save_path = Path()

    def action(path: Path):
        nonlocal save_path
        save_path = path
        path.write_text('test', encoding='utf-8')

    watched_paths, events = _watch_file(action, FileEvent.CLOSED, 1)
    assert len(events) == 1
    event = events[0]
    assert event[0] == save_path
    assert event[1] == FileEvent.CLOSED
    assert event[2] == b''
    assert watched_paths == [save_path]


def test_watch_file_modify():
    save_path = Path()

    def action(path: Path):
        nonlocal save_path
        save_path = path
        with path.open(mode='a', encoding='utf-8') as test_file:
            test_file.write('test!')

    watched_paths, events = _watch_file(action, FileEvent.MODIFIED, 1)
    assert len(events) == 1
    event = events[0]
    assert event[0] == save_path
    assert event[1] == FileEvent.MODIFIED
    assert event[2] == b''
    assert watched_paths == [save_path]


def test_watch_file_delete():
    save_path = Path()

    def action(path: Path):
        nonlocal save_path
        save_path = path
        path.unlink()
        time.sleep(.1)  # IN_IGNORED signal is sent after a delete

    watched_paths, events = _watch_file(action, FileEvent.DELETED, 1)
    assert len(events) == 1
    event = events[0]
    assert event[0] == save_path
    assert event[1] == FileEvent.DELETED
    assert event[2] == b''
    assert len(watched_paths) == 0


def test_watch_file_move():
    save_path = Path()

    def action(path: Path):
        nonlocal save_path
        save_path = path
        path.rename(path.parent / 'test2.txt')

    watched_paths, events = _watch_file(action, FileEvent.MOVED, 1)
    assert len(events) == 1
    event = events[0]
    assert event[0] == save_path
    assert event[1] == FileEvent.MOVED
    assert event[2] == b''
    assert len(watched_paths) == 0


def test_watch_file_default():
    def action(path: Path):
        with path.open(mode='a', encoding='utf-8') as test_file:
            test_file.write('test!')
        path.unlink()

    expected_events = [FileEvent.MODIFIED, FileEvent.DELETED]
    _, events = _watch_file(action, None, len(expected_events))
    assert len(expected_events) == len(events)
    for expected, result in zip(expected_events, events, strict=True):
        assert expected == result[1]


def test_watch_folder_delete():
    save_path = Path()

    def action(path: Path):
        nonlocal save_path
        save_path = path
        path.rmdir()
        time.sleep(.1)  # IN_IGNORED signal is sent after a delete

    watched_paths, events = _watch_folder(action, FolderEvent.DELETED, 1)
    assert len(events) == 1
    event = events[0]
    assert event[0] == save_path
    assert event[1] == FolderEvent.DELETED
    assert event[2] == b''
    assert len(watched_paths) == 0


def test_watch_folder_move():
    save_path = Path()

    def action(path: Path):
        nonlocal save_path
        save_path = path
        path.rename(path.parent / 'test2')

    watched_paths, events = _watch_folder(action, FolderEvent.MOVED, 1)
    assert len(events) == 1
    event = events[0]
    assert event[0] == save_path
    assert event[1] == FolderEvent.MOVED
    assert event[2] == b''
    assert len(watched_paths) == 0


def test_watch_folder_sub_create():
    save_path = Path()
    create_name = 'test.txt'

    def action(path: Path):
        nonlocal save_path
        save_path = path
        (path / create_name).touch()

    watched_paths, events = _watch_folder(action, FolderEvent.SUB_CREATED, 1)
    assert len(events) == 1
    event = events[0]
    assert event[0] == save_path
    assert event[1] == FolderEvent.SUB_CREATED
    assert event[2] == create_name.encode()
    assert watched_paths == [save_path]


def test_watch_folder_sub_delete():
    save_path = Path()
    create_name = 'test.txt'

    def action(path: Path):
        nonlocal save_path
        save_path = path
        (path / create_name).touch()
        (path / create_name).unlink()

    watched_paths, events = _watch_folder(action, FolderEvent.SUB_DELETED, 1)
    assert len(events) == 1
    event = events[0]
    assert event[0] == save_path
    assert event[1] == FolderEvent.SUB_DELETED
    assert event[2] == create_name.encode()
    assert watched_paths == [save_path]


def test_watch_folder_sub_move():
    save_path = Path()
    create_name = 'test.txt'
    rename_name = 'test2.txt'

    def action(path: Path):
        nonlocal save_path
        save_path = path
        new_file = path / create_name
        new_file.touch()
        new_file.rename(path / rename_name)

    watched_paths, events = _watch_folder(action, FolderEvent.SUB_MOVED, 1)
    assert len(events) == 1
    event = events[0]
    assert event[0] == save_path
    assert event[1] == FolderEvent.SUB_MOVED
    assert event[2] == f'{create_name} -> {rename_name}'.encode()
    assert watched_paths == [save_path]


def test_watch_folder_sub_move_long_name():
    save_path = Path()
    create_name = 'test.txt'
    rename_count = 5
    name_length = 120

    def action(path: Path):
        nonlocal create_name, save_path
        save_path = path
        file_path = path / create_name
        file_path.touch()
        for i in range(rename_count):
            rename_name = chr(ord('a') + i) * name_length
            file_path.rename(path / rename_name)
            file_path = path / rename_name

    watched_paths, events = _watch_folder(action, FolderEvent.SUB_MOVED, rename_count)
    assert len(events) == rename_count
    name = create_name
    for i, event in enumerate(events):
        rename = (chr(ord('a') + i) * name_length)
        assert event[0] == save_path
        assert event[1] == FolderEvent.SUB_MOVED
        assert event[2] == f'{name} -> {rename}'.encode()
        name = rename
    assert watched_paths == [save_path]


def test_watch_folder_default():
    create_name = 'test.txt'
    rename_name = 'test2.txt'

    def action(path: Path):
        new_file = path / create_name
        new_file.touch()
        new_file.rename(path / rename_name)
        (path / rename_name).unlink()
        new_path = path.parent / 'new_test'
        path.rename(new_path)

    expected_events = [FolderEvent.SUB_CREATED, FolderEvent.SUB_MOVED, FolderEvent.SUB_DELETED, FolderEvent.MOVED]
    watched_paths, events = _watch_folder(action, None, len(expected_events))
    assert len(expected_events) == len(events)
    for expected, result in zip(expected_events, events, strict=True):
        assert expected == result[1]
    assert len(watched_paths) == 0


def _watch_folder_recursive(action, event_type, event_count: int, exclude_patterns: list[str]) -> tuple[
        list[Path], list[tuple[Path | None, FileEvent, bytes]]]:
    with tempfile.TemporaryDirectory() as temp_root:
        root_path = Path(temp_root)
        tree = {
            'sub_1': {
                'sub_1_1': {},
                'sub_1_2': {},
            },
            'sub_2': {
                'sub_2_1': {},
                'sub_2_2': {},
                'sub_2_3': {},
            },
            'sub_3': {},
            'sub_4': {},
            'sub_5': {
                'sub_5_1': {},
            }
        }
        queue: list[tuple[Path, dict]] = [(root_path.resolve(), tree)]
        while queue:
            current_path, current_dict = queue.pop()
            if current_path != root_path.resolve():
                current_path.mkdir()
            for sub_path, node in current_dict.items():
                queue.append((current_path / sub_path, node))
        (root_path / 'sub_1' / 'sub_1_2' / 'test.txt').touch()

        return _watch_base(action, event_type, event_count, root_path, exclude_patterns, recursive=True)


def test_watch_folder_recursive():
    save_path = Path()
    create_paths = [
        Path('sub_1', 'sub_1_2', 'test_1_2.txt'),
        Path('sub_5', 'sub_5_1', 'test_5_1.txt')
    ]

    def action(path: Path):
        nonlocal create_paths, save_path
        save_path = path

        for sub_path in create_paths:
            (path / sub_path).touch()

    _, events = _watch_folder_recursive(action, FolderEvent.SUB_CREATED, 2, [])
    assert len(events) == len(create_paths)
    for event in events:
        assert event[1] == FolderEvent.SUB_CREATED


def test_watch_folder_recursive_dynamic():
    save_path = Path()
    create_paths = [
        Path('sub_3', 'sub_3_1'),
        Path('sub_3', 'sub_3_1', 'test_3_1_1')
    ]

    def action(path: Path):
        nonlocal create_paths, save_path
        save_path = path

        for sub_path in create_paths:
            (path / sub_path).mkdir()
            time.sleep(.1)  # ensure parent folder is register to get 2nd event

    watched_paths, events = _watch_folder_recursive(action, FolderEvent.SUB_CREATED, len(create_paths), [])
    assert len(events) == len(create_paths)
    for event in events:
        assert event[1] == FolderEvent.SUB_CREATED
    for path in create_paths:
        assert (save_path / path).resolve() in watched_paths


def test_watch_folder_recursive_remove():
    save_path = Path()
    remove_path = 'sub_2'

    def action(path: Path):
        nonlocal remove_path, save_path
        save_path = path
        shutil.rmtree(path / remove_path)
        time.sleep(.1)  # IN_IGNORE event is sent after DELETE so last ignore might be skipped

    watched_paths, events = _watch_folder_recursive(action, FolderEvent.DELETED, 4, [])
    assert len(events) == 4  # noqa: PLR2004
    for path in watched_paths:
        assert remove_path not in str(path)


def test_watch_folder_implicit_remove():
    save_path = Path()
    remove_path = 'sub_2'

    def action(path: Path):
        nonlocal remove_path, save_path
        save_path = path
        shutil.rmtree(path / remove_path)
        time.sleep(.1)

    watched_paths, events = _watch_folder_recursive(action, FolderEvent.SUB_CREATED, 0, [])
    assert len(events) == 0
    for path in watched_paths:
        assert remove_path not in str(path)


def test_watch_folder_recursive_move():
    save_path = Path()

    def action(path: Path):
        nonlocal save_path
        save_path = path

        (path / 'sub_2').rename(path / 'sub_2.2')

    watched_paths, events = _watch_folder_recursive(action, FolderEvent.SUB_MOVED, 1, [])
    assert len(events) == 1
    assert events[0][0] == save_path
    assert events[0][1] == FolderEvent.SUB_MOVED
    assert events[0][2] == b'sub_2 -> sub_2.2'
    for path in [save_path / 'sub_2.2' / f'sub_2_{i}' for i in range(1, 4)]:
        assert path in watched_paths


def test_watch_folder_recursive_modify():
    save_path = Path()

    def action(path: Path):
        nonlocal save_path
        save_path = path

        with (path / 'sub_1' / 'sub_1_2' / 'test.txt').open(mode='a+', encoding='utf-8') as test_file:
            test_file.write('test!')

    watched_paths, events = _watch_folder_recursive(action, FileEvent.MODIFIED, 1, [])
    file_path = save_path / 'sub_1' / 'sub_1_2' / 'test.txt'
    assert len(events) == 1
    assert events[0][0] == file_path
    assert events[0][1] == FileEvent.MODIFIED
    assert events[0][2] == b''
    assert file_path in watched_paths


def test_watch_folder_recursive_modify_new_file():
    save_path = Path()

    def action(path: Path):
        nonlocal save_path
        save_path = path

        with (path / 'sub_4' / 'test.txt').open(mode='w', encoding='utf-8') as test_file:
            time.sleep(.1)  # write will not trigger if the file is not watch yet
            test_file.write('test!')

    watched_paths, events = _watch_folder_recursive(action, FileEvent.MODIFIED, 2, [])
    file_path = save_path / 'sub_4' / 'test.txt'
    expected_events = [
        (file_path.parent, FolderEvent.SUB_CREATED, file_path.name.encode()),
        (file_path, FileEvent.MODIFIED, b'')
    ]
    assert len(events) == len(expected_events)
    for event, (expect_path, expect_event, expect_name) in zip(events, expected_events, strict=True):
        assert event[0] == expect_path
        assert event[1] == expect_event
        assert event[2] == expect_name
    assert file_path in watched_paths


def test_watch_folder_recursive_exclude():
    save_path = Path()

    def action(path: Path):
        nonlocal save_path
        save_path = path

    watched_paths, _events = _watch_folder_recursive(action, FileEvent.MODIFIED, 0, ['*/sub_2'])
    assert all('sub_2' not in str(path) for path in watched_paths)
