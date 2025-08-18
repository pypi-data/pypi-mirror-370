"""
File Watcher Service for automatic index rebuilds.

This module provides file system monitoring capabilities that automatically
trigger index rebuilds when relevant files are modified, created, or deleted.
It uses the watchdog library for cross-platform file system event monitoring.
"""
# pylint: disable=missing-function-docstring  # Fallback stub methods don't need docstrings

import logging
import os
import traceback
from threading import Timer
from typing import Optional, Callable
from pathlib import Path

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler, FileSystemEvent
    WATCHDOG_AVAILABLE = True
except ImportError:
    # Fallback classes for when watchdog is not available
    class Observer:
        """Fallback Observer class when watchdog library is not available."""
        def __init__(self):
            pass
        def schedule(self, *args, **kwargs):
            pass
        def start(self):
            pass
        def stop(self):
            pass
        def join(self, *args, **kwargs):
            pass
        def is_alive(self):
            return False

    class FileSystemEventHandler:
        """Fallback FileSystemEventHandler class when watchdog library is not available."""
        def __init__(self):
            pass

    class FileSystemEvent:
        """Fallback FileSystemEvent class when watchdog library is not available."""
        def __init__(self):
            self.is_directory = False
            self.src_path = ""
            self.event_type = ""

    WATCHDOG_AVAILABLE = False

from .base_service import BaseService
from ..constants import SUPPORTED_EXTENSIONS


class FileWatcherService(BaseService):
    """
    Service for monitoring file system changes and triggering index rebuilds.

    This service uses the watchdog library to monitor file system events and
    automatically triggers background index rebuilds when relevant files change.
    It includes intelligent debouncing to batch rapid changes and filtering
    to only monitor relevant file types.
    """
    MAX_RESTART_ATTEMPTS = 3

    def __init__(self, ctx):
        """
        Initialize the file watcher service.

        Args:
            ctx: The MCP Context object
        """
        super().__init__(ctx)
        self.logger = logging.getLogger(__name__)
        self.observer: Optional[Observer] = None
        self.event_handler: Optional[DebounceEventHandler] = None
        self.is_monitoring = False
        self.restart_attempts = 0
        self.rebuild_callback: Optional[Callable] = None

        # Check if watchdog is available
        if not WATCHDOG_AVAILABLE:
            self.logger.warning("Watchdog library not available - file watcher disabled")

    def start_monitoring(self, rebuild_callback: Callable) -> bool:
        """
        Start file system monitoring.

        Args:
            rebuild_callback: Function to call when rebuild is needed

        Returns:
            True if monitoring started successfully, False otherwise
        """
        if not WATCHDOG_AVAILABLE:
            self.logger.warning("Cannot start file watcher - watchdog library not available")
            return False

        if self.is_monitoring:
            self.logger.debug("File watcher already monitoring")
            return True

        # Validate project setup
        error = self._validate_project_setup()
        if error:
            self.logger.error("Cannot start file watcher: %s", error)
            return False

        self.rebuild_callback = rebuild_callback

        # Get debounce seconds from config
        config = self.settings.get_file_watcher_config()
        debounce_seconds = config.get('debounce_seconds', 6.0)

        try:
            self.observer = Observer()
            self.event_handler = DebounceEventHandler(
                debounce_seconds=debounce_seconds,
                rebuild_callback=self.rebuild_callback,
                base_path=Path(self.base_path),
                logger=self.logger
            )

            # Log detailed Observer setup
            watch_path = str(self.base_path)
            self.logger.debug("Scheduling Observer for path: %s", watch_path)

            self.observer.schedule(
                self.event_handler,
                watch_path,
                recursive=True
            )

            # Log Observer start
            self.logger.debug("Starting Observer...")
            self.observer.start()
            self.is_monitoring = True
            self.restart_attempts = 0

            # Log Observer thread info
            if hasattr(self.observer, '_thread'):
                self.logger.debug("Observer thread: %s", self.observer._thread)

            # Verify observer is actually running
            if self.observer.is_alive():
                self.logger.info(
                    "File watcher started successfully",
                    extra={
                        "debounce_seconds": debounce_seconds,
                        "monitored_path": str(self.base_path),
                        "supported_extensions": len(SUPPORTED_EXTENSIONS)
                    }
                )

                # Add diagnostic test - create a test event to verify Observer works
                self.logger.debug("Observer thread is alive: %s", self.observer.is_alive())
                self.logger.debug("Monitored path exists: %s", os.path.exists(str(self.base_path)))
                self.logger.debug("Event handler is set: %s", self.event_handler is not None)

                # Log current directory for comparison
                current_dir = os.getcwd()
                self.logger.debug("Current working directory: %s", current_dir)
                self.logger.debug("Are paths same: %s", os.path.normpath(current_dir) == os.path.normpath(str(self.base_path)))

                return True
            else:
                self.logger.error("File watcher failed to start - Observer not alive")
                return False

        except Exception as e:
            self.logger.warning("Failed to start file watcher: %s", e)
            self.logger.info("Falling back to reactive index refresh")
            return False

    def stop_monitoring(self) -> None:
        """
        Stop file system monitoring and cleanup all resources.

        This method ensures complete cleanup of:
        - Observer thread
        - Event handler
        - Debounce timers
        - Monitoring state
        """
        if not self.observer and not self.is_monitoring:
            # Already stopped or never started
            return

        self.logger.info("Stopping file watcher monitoring...")

        try:
            # Step 1: Stop the observer first
            if self.observer:
                self.logger.debug("Stopping observer...")
                self.observer.stop()

                # Step 2: Cancel any active debounce timer
                if self.event_handler and self.event_handler.debounce_timer:
                    self.logger.debug("Cancelling debounce timer...")
                    self.event_handler.debounce_timer.cancel()

                # Step 3: Wait for observer thread to finish (with timeout)
                self.logger.debug("Waiting for observer thread to finish...")
                self.observer.join(timeout=5.0)

                # Step 4: Check if thread actually finished
                if self.observer.is_alive():
                    self.logger.warning("Observer thread did not stop within timeout")
                else:
                    self.logger.debug("Observer thread stopped successfully")

            # Step 5: Clear all references
            self.observer = None
            self.event_handler = None
            self.rebuild_callback = None
            self.is_monitoring = False

            self.logger.info("File watcher stopped and cleaned up successfully")

        except Exception as e:
            self.logger.error("Error stopping file watcher: %s", e)

            # Force cleanup even if there were errors
            self.observer = None
            self.event_handler = None
            self.rebuild_callback = None
            self.is_monitoring = False

    def is_active(self) -> bool:
        """
        Check if file watcher is actively monitoring.

        Returns:
            True if actively monitoring, False otherwise
        """
        return (self.is_monitoring and
                self.observer and
                self.observer.is_alive())

    def restart_observer(self) -> bool:
        """
        Attempt to restart the file system observer.

        Returns:
            True if restart successful, False otherwise
        """
        if self.restart_attempts >= self.MAX_RESTART_ATTEMPTS:
            self.logger.error("Max restart attempts reached, file watcher disabled")
            return False

        self.logger.info("Attempting to restart file watcher (attempt %d)",
                         self.restart_attempts + 1)
        self.restart_attempts += 1

        # Stop current observer if running
        if self.observer:
            try:
                self.observer.stop()
                self.observer.join(timeout=2.0)
            except Exception as e:
                self.logger.warning("Error stopping observer during restart: %s", e)

        # Start new observer
        try:
            self.observer = Observer()
            self.observer.schedule(
                self.event_handler,
                str(self.base_path),
                recursive=True
            )
            self.observer.start()
            self.is_monitoring = True

            self.logger.info("File watcher restarted successfully")
            return True

        except Exception as e:
            self.logger.error("Failed to restart file watcher: %s", e)
            return False

    def get_status(self) -> dict:
        """
        Get current file watcher status information.

        Returns:
            Dictionary containing status information
        """
        # Get current debounce seconds from config
        config = self.settings.get_file_watcher_config()
        debounce_seconds = config.get('debounce_seconds', 6.0)

        return {
            "available": WATCHDOG_AVAILABLE,
            "active": self.is_active(),
            "monitoring": self.is_monitoring,
            "restart_attempts": self.restart_attempts,
            "debounce_seconds": debounce_seconds,
            "base_path": self.base_path if self.base_path else None,
            "observer_alive": self.observer.is_alive() if self.observer else False
        }


class DebounceEventHandler(FileSystemEventHandler):
    """
    File system event handler with debouncing capability.

    This handler filters file system events to only relevant files and
    implements a debounce mechanism to batch rapid changes into single
    rebuild operations.
    """

    def __init__(self, debounce_seconds: float, rebuild_callback: Callable,
                 base_path: Path, logger: logging.Logger):
        """
        Initialize the debounce event handler.

        Args:
            debounce_seconds: Number of seconds to wait before triggering rebuild
            rebuild_callback: Function to call when rebuild is needed
            base_path: Base project path for filtering
            logger: Logger instance for debug messages
        """
        super().__init__()
        self.debounce_seconds = debounce_seconds
        self.rebuild_callback = rebuild_callback
        self.base_path = base_path
        self.debounce_timer: Optional[Timer] = None
        self.logger = logger

        # Exclusion patterns for directories and files to ignore
        self.exclude_patterns = {
            '.git', '.svn', '.hg',
            'node_modules', '__pycache__', '.venv', 'venv',
            '.DS_Store', 'Thumbs.db',
            'dist', 'build', 'target', '.idea', '.vscode',
            '.pytest_cache', '.coverage', '.tox',
            'bin', 'obj'  # Additional build directories
        }

        # Convert supported extensions to set for faster lookup
        self.supported_extensions = set(SUPPORTED_EXTENSIONS)

    def on_any_event(self, event: FileSystemEvent) -> None:
        """
        Handle any file system event.

        Args:
            event: The file system event
        """
        # Check if event should be processed
        should_process = self.should_process_event(event)

        if should_process:
            self.logger.info("File changed: %s - %s", event.event_type, event.src_path)
            self.reset_debounce_timer()
        else:
            # Only log at debug level for filtered events
            self.logger.debug("Filtered: %s - %s", event.event_type, event.src_path)

    def should_process_event(self, event: FileSystemEvent) -> bool:
        """
        Determine if event should trigger index rebuild.

        Args:
            event: The file system event to evaluate

        Returns:
            True if event should trigger rebuild, False otherwise
        """
        # Skip directory events
        if event.is_directory:
            self.logger.debug("Skipping directory event: %s", event.src_path)
            return False

        # Select path to check: dest_path for moves, src_path for others
        if event.event_type == 'moved':
            if not hasattr(event, 'dest_path'):
                return False
            target_path = event.dest_path
        else:
            target_path = event.src_path

        # Fast path exclusion - check if path is in excluded directory before any processing
        if self._is_path_in_excluded_directory(target_path):
            return False

        # Unified path checking
        try:
            path = Path(target_path)
            return self._should_process_path(path)
        except Exception:
            return False

    def _should_process_path(self, path: Path) -> bool:
        """
        Check if a specific path should trigger index rebuild.

        Args:
            path: The file path to check

        Returns:
            True if path should trigger rebuild, False otherwise
        """
        # Skip excluded paths
        if self.is_excluded_path(path):
            return False

        # Only process supported file types
        if not self.is_supported_file_type(path):
            return False

        # Skip temporary files
        if self.is_temporary_file(path):
            return False

        return True

    def _is_path_in_excluded_directory(self, file_path: str) -> bool:
        """
        Fast check if a file path is within an excluded directory.
        
        This method performs a quick string-based check to avoid expensive
        Path operations for files in excluded directories like .venv.
        
        Args:
            file_path: The file path to check
            
        Returns:
            True if the path is in an excluded directory, False otherwise
        """
        try:
            # Normalize path separators for cross-platform compatibility
            normalized_path = file_path.replace('\\', '/')
            base_path_normalized = str(self.base_path).replace('\\', '/')
            
            # Get relative path string
            if not normalized_path.startswith(base_path_normalized):
                return True  # Path outside project - exclude it
                
            relative_path = normalized_path[len(base_path_normalized):].lstrip('/')
            
            # Quick check: if any excluded pattern appears as a path component
            path_parts = relative_path.split('/')
            for part in path_parts:
                if part in self.exclude_patterns:
                    return True
                    
            return False
        except Exception:
            # If any error occurs, err on the side of exclusion
            return True

    def is_excluded_path(self, path: Path) -> bool:
        """
        Check if path should be excluded from monitoring.

        Args:
            path: The file path to check

        Returns:
            True if path should be excluded, False otherwise
        """
        try:
            relative_path = path.relative_to(self.base_path)
            parts = relative_path.parts

            # Check if any part of the path matches exclusion patterns
            return any(part in self.exclude_patterns for part in parts)
        except ValueError:
            # Path is not relative to base_path - exclude it
            return True
        except Exception:
            # Handle any other path processing issues
            return True

    def is_supported_file_type(self, path: Path) -> bool:
        """
        Check if file type is supported for indexing.

        Args:
            path: The file path to check

        Returns:
            True if file type is supported, False otherwise
        """
        return path.suffix.lower() in self.supported_extensions

    def is_temporary_file(self, path: Path) -> bool:
        """
        Check if file is a temporary file.

        Args:
            path: The file path to check

        Returns:
            True if file appears to be temporary, False otherwise
        """
        name = path.name.lower()

        # Common temporary file patterns
        temp_patterns = ['.tmp', '.swp', '.swo', '~', '.bak', '.orig']

        # Check for temporary file extensions
        if any(name.endswith(pattern) for pattern in temp_patterns):
            return True

        # Check for vim/editor temporary files
        if name.startswith('.') and (name.endswith('.swp') or name.endswith('.swo')):
            return True

        # Check for backup files (e.g., file.py~, file.py.bak)
        if '~' in name or '.bak' in name:
            return True

        return False

    def reset_debounce_timer(self) -> None:
        """Reset the debounce timer, canceling any existing timer."""
        if self.debounce_timer:
            self.debounce_timer.cancel()

        self.debounce_timer = Timer(
            self.debounce_seconds,
            self.trigger_rebuild
        )
        self.debounce_timer.start()

    def trigger_rebuild(self) -> None:
        """Trigger index rebuild after debounce period."""
        self.logger.info("File changes detected, triggering rebuild")

        if self.rebuild_callback:
            try:
                result = self.rebuild_callback()
            except Exception as e:
                self.logger.error("Rebuild callback failed: %s", e)
                traceback_msg = traceback.format_exc()
                self.logger.error("Traceback: %s", traceback_msg)
        else:
            self.logger.warning("No rebuild callback configured")
