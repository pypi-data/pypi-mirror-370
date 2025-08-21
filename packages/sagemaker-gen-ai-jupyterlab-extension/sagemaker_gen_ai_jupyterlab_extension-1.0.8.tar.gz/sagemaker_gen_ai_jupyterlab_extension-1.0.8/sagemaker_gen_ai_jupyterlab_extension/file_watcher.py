import os
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

logger = logging.getLogger(__name__)


class GenericFileHandler(FileSystemEventHandler):
    def __init__(self, file_pattern, callback):
        self.file_pattern = file_pattern
        self.callback = callback
        
    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith(self.file_pattern):
            self.callback()
            
    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith(self.file_pattern):
            self.callback()


class FileWatcher:
    """Generic file watcher that can monitor any directory for specific file changes"""
    
    def __init__(self):
        self.observer = None
        
    def start_watching(self, directory, file_pattern, callback, recursive=False):
        """Start watching a directory for file changes
        
        Args:
            directory: Directory to watch
            file_pattern: File pattern to match (e.g., 'customization_arn.json')
            callback: Function to call when file changes
            recursive: Whether to watch subdirectories
        """
        event_handler = GenericFileHandler(file_pattern, callback)
        self.observer = Observer()
        self.observer.schedule(event_handler, directory, recursive=recursive)
        self.observer.start()
        logger.info(f"Started file watcher for {directory}")
        
    def stop_watching(self):
        """Stop the file watcher"""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            logger.info("File watcher stopped")