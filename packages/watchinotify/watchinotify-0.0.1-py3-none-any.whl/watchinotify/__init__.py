import importlib.metadata

from .inotify import Event, FileEvent, FolderEvent, Watcher


__all__ = ['Event', 'FileEvent', 'FolderEvent', 'Watcher']


__version__ = importlib.metadata.version('watchinotify')
