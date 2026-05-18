"""File system watcher for monitoring .ets file changes."""

import time
from pathlib import Path
from typing import Callable, Optional
from dataclasses import dataclass, field
from enum import Enum
import threading
import queue


class ChangeType(Enum):
    """Type of file change."""
    CREATED = "created"
    MODIFIED = "modified"
    DELETED = "deleted"
    MOVED = "moved"


@dataclass
class FileChange:
    """Represents a file change event."""
    path: str
    change_type: ChangeType
    timestamp: float = field(default_factory=time.time)


class FileWatcher:
    """Watches file system for .ets file changes with hash-based detection."""
    
    def __init__(self, project_path: str, debounce_seconds: float = 1.0):
        self.project_path = Path(project_path).resolve()
        self.debounce_seconds = debounce_seconds
        self.change_queue: queue.Queue[FileChange] = queue.Queue()
        self._running = False
        self._watcher_thread: Optional[threading.Thread] = None
        self._pending_changes: dict[str, FileChange] = {}
        self._pending_lock = threading.Lock()
        self._observed_files: set[str] = set()
        self._observer = None
    
    def start(self):
        """Start watching for file changes."""
        if self._running:
            return
        
        self._running = True
        self._scan_existing_files()
        self._watcher_thread = threading.Thread(target=self._watch_loop, daemon=True)
        self._watcher_thread.start()
    
    def stop(self):
        """Stop watching for file changes."""
        self._running = False
        if self._observer:
            self._observer.stop()
            self._observer = None
    
    def _scan_existing_files(self):
        """Scan for existing .ets files in the project."""
        for ets_file in self.project_path.rglob("*.ets"):
            self._observed_files.add(str(ets_file))
    
    def _watch_loop(self):
        """Main watch loop that processes file system events."""
        try:
            from watchdog.observers import Observer
            from watchdog.events import FileSystemEventHandler, FileSystemEvent
            
            class ETSHandler(FileSystemEventHandler):
                def __init__(self, watcher: 'FileWatcher'):
                    self.watcher = watcher
                
                def on_any_event(self, event: FileSystemEvent):
                    if event.is_directory:
                        return
                    
                    if not event.src_path.endswith('.ets'):
                        return
                    
                    if event.event_type == 'created':
                        self.watcher._handle_change(event.src_path, ChangeType.CREATED)
                    elif event.event_type == 'modified':
                        self.watcher._handle_change(event.src_path, ChangeType.MODIFIED)
                    elif event.event_type == 'deleted':
                        self.watcher._handle_change(event.src_path, ChangeType.DELETED)
                    elif event.event_type == 'moved':
                        self.watcher._handle_change(event.dest_path, ChangeType.CREATED)
                        self.watcher._handle_change(event.src_path, ChangeType.DELETED)
            
            self._observer = Observer()
            handler = ETSHandler(self)
            self._observer.schedule(handler, str(self.project_path), recursive=True)
            self._observer.start()
            
            while self._running:
                time.sleep(0.1)
                self._process_pending_changes()
            
            self._observer.stop()
            self._observer.join()
            
        except ImportError:
            self._fallback_watch_loop()
    
    def _fallback_watch_loop(self):
        """Fallback watch loop using polling when watchdog is not available."""
        import os
        last_mtimes = {}
        
        while self._running:
            current_files = set()
            
            for ets_file in self.project_path.rglob("*.ets"):
                path = str(ets_file)
                current_files.add(path)
                
                try:
                    mtime = os.path.getmtime(path)
                    if path not in last_mtimes:
                        self._handle_change(path, ChangeType.CREATED)
                    elif mtime > last_mtimes[path]:
                        self._handle_change(path, ChangeType.MODIFIED)
                except OSError:
                    pass
            
            for old_path in last_mtimes:
                if old_path not in current_files:
                    self._handle_change(old_path, ChangeType.DELETED)
            
            last_mtimes = {f: os.path.getmtime(f) for f in current_files if os.path.exists(f)}
            
            time.sleep(1.0)
            self._process_pending_changes()
    
    def _handle_change(self, path: str, change_type: ChangeType):
        """Handle a file change event."""
        with self._pending_lock:
            self._pending_changes[path] = FileChange(
                path=path,
                change_type=change_type,
                timestamp=time.time()
            )
    
    def _process_pending_changes(self):
        """Process pending changes after debounce period."""
        with self._pending_lock:
            if not self._pending_changes:
                return
            
            now = time.time()
            ready_changes = []
            
            for path, change in list(self._pending_changes.items()):
                if now - change.timestamp >= self.debounce_seconds:
                    ready_changes.append(change)
                    del self._pending_changes[path]
            
            if ready_changes:
                merged_changes = self._merge_changes(ready_changes)
                for change in merged_changes:
                    try:
                        self.change_queue.put_nowait(change)
                    except queue.Full:
                        pass
    
    def _merge_changes(self, changes: list[FileChange]) -> list[FileChange]:
        """Merge multiple changes to the same file."""
        path_map = {}
        
        for change in changes:
            if change.path not in path_map:
                path_map[change.path] = change
            else:
                existing = path_map[change.path]
                if change.change_type == ChangeType.DELETED:
                    path_map[change.path] = change
                elif existing.change_type == ChangeType.CREATED:
                    pass
                else:
                    path_map[change.path] = change
        
        return list(path_map.values())
    
    def get_changes(self, timeout: float = 0.1) -> list[FileChange]:
        """Get all pending changes from the queue."""
        changes = []
        while True:
            try:
                change = self.change_queue.get_nowait()
                changes.append(change)
            except queue.Empty:
                break
        
        self._process_pending_changes()
        
        return changes
    
    def get_and_wait_for_changes(self, timeout: float = 1.0) -> list[FileChange]:
        """Wait for changes and return them."""
        try:
            change = self.change_queue.get(timeout=timeout)
            changes = [change]
            
            while True:
                try:
                    change = self.change_queue.get_nowait()
                    changes.append(change)
                except queue.Empty:
                    break
            
            return changes
        except queue.Empty:
            self._process_pending_changes()
            return []
    
    def scan_project(self) -> list[str]:
        """Scan project for all .ets files."""
        files = []
        for ets_file in self.project_path.rglob("*.ets"):
            files.append(str(ets_file))
        return files
