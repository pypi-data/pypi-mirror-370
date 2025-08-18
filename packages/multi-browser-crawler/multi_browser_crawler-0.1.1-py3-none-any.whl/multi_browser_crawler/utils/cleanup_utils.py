"""
Cleanup Utilities for Multi-Browser Crawler
===========================================

Utilities for resource cleanup and recovery.
"""

import os
import shutil
import psutil
import time
from typing import List, Dict, Any, Optional
import logging

from ..exceptions.errors import ResourceCleanupError

logger = logging.getLogger(__name__)


class ResourceCleaner:
    """Clean up browser resources and temporary files."""
    
    def __init__(self, data_folder: str = None):
        """
        Initialize resource cleaner.
        
        Args:
            data_folder: Base data folder path
        """
        self.data_folder = data_folder or os.path.join(os.getcwd(), "data")
        self.temp_folders = [
            os.path.join(self.data_folder, "browser_sessions"),
            os.path.join(self.data_folder, "temp"),
            os.path.join(self.data_folder, "cache")
        ]
    
    def cleanup_browser_processes(self, force: bool = False) -> Dict[str, Any]:
        """
        Clean up orphaned browser processes.
        
        Args:
            force: If True, forcefully kill processes
            
        Returns:
            Dictionary with cleanup results
        """
        results = {
            'processes_found': 0,
            'processes_terminated': 0,
            'errors': []
        }
        
        try:
            browser_processes = self._find_browser_processes()
            results['processes_found'] = len(browser_processes)
            
            for proc in browser_processes:
                try:
                    if force:
                        proc.kill()
                    else:
                        proc.terminate()
                    
                    # Wait for process to die
                    try:
                        proc.wait(timeout=5)
                        results['processes_terminated'] += 1
                        logger.info(f"Terminated browser process {proc.pid}")
                    except psutil.TimeoutExpired:
                        if force:
                            proc.kill()
                            results['processes_terminated'] += 1
                            logger.info(f"Force killed browser process {proc.pid}")
                        else:
                            results['errors'].append(f"Process {proc.pid} did not terminate")
                
                except psutil.NoSuchProcess:
                    # Process already dead
                    results['processes_terminated'] += 1
                except psutil.AccessDenied:
                    results['errors'].append(f"Access denied for process {proc.pid}")
                except Exception as e:
                    results['errors'].append(f"Error terminating process {proc.pid}: {e}")
            
            logger.info(f"Browser cleanup: {results['processes_terminated']}/{results['processes_found']} processes terminated")
            
        except Exception as e:
            logger.error(f"Error during browser process cleanup: {e}")
            results['errors'].append(str(e))
        
        return results
    
    def _find_browser_processes(self) -> List[psutil.Process]:
        """Find all browser processes."""
        browser_processes = []
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['name'] and 'chrome' in proc.info['name'].lower():
                        cmdline = proc.info.get('cmdline', [])
                        # Look for browser processes with user data dir
                        if any('--user-data-dir' in arg for arg in cmdline):
                            browser_processes.append(psutil.Process(proc.info['pid']))
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            logger.warning(f"Error finding browser processes: {e}")
        
        return browser_processes
    
    def cleanup_temp_files(self, max_age_hours: int = 24) -> Dict[str, Any]:
        """
        Clean up temporary files older than specified age.
        
        Args:
            max_age_hours: Maximum age of files to keep in hours
            
        Returns:
            Dictionary with cleanup results
        """
        results = {
            'folders_processed': 0,
            'files_removed': 0,
            'bytes_freed': 0,
            'errors': []
        }
        
        cutoff_time = time.time() - (max_age_hours * 3600)
        
        for folder in self.temp_folders:
            if not os.path.exists(folder):
                continue
            
            results['folders_processed'] += 1
            
            try:
                for root, dirs, files in os.walk(folder):
                    for file in files:
                        file_path = os.path.join(root, file)
                        try:
                            stat = os.stat(file_path)
                            if stat.st_mtime < cutoff_time:
                                file_size = stat.st_size
                                os.remove(file_path)
                                results['files_removed'] += 1
                                results['bytes_freed'] += file_size
                                logger.debug(f"Removed old temp file: {file_path}")
                        except Exception as e:
                            results['errors'].append(f"Error removing {file_path}: {e}")
                    
                    # Remove empty directories
                    for dir_name in dirs:
                        dir_path = os.path.join(root, dir_name)
                        try:
                            if not os.listdir(dir_path):
                                os.rmdir(dir_path)
                                logger.debug(f"Removed empty directory: {dir_path}")
                        except Exception as e:
                            results['errors'].append(f"Error removing directory {dir_path}: {e}")
            
            except Exception as e:
                results['errors'].append(f"Error processing folder {folder}: {e}")
        
        mb_freed = results['bytes_freed'] / (1024 * 1024)
        logger.info(f"Temp cleanup: {results['files_removed']} files removed, {mb_freed:.1f}MB freed")
        
        return results
    
    def cleanup_session_directories(self, active_sessions: List[str] = None) -> Dict[str, Any]:
        """
        Clean up browser session directories.
        
        Args:
            active_sessions: List of active session IDs to preserve
            
        Returns:
            Dictionary with cleanup results
        """
        results = {
            'sessions_found': 0,
            'sessions_removed': 0,
            'bytes_freed': 0,
            'errors': []
        }
        
        active_sessions = active_sessions or []
        sessions_folder = os.path.join(self.data_folder, "browser_sessions")
        
        if not os.path.exists(sessions_folder):
            return results
        
        try:
            for item in os.listdir(sessions_folder):
                if item.startswith("session_") and item != "session_registry.json":
                    session_path = os.path.join(sessions_folder, item)
                    
                    if os.path.isdir(session_path):
                        results['sessions_found'] += 1
                        
                        # Extract session ID from directory name
                        session_id = item.replace("session_", "")
                        
                        # Skip if session is active
                        if session_id in active_sessions:
                            logger.debug(f"Preserving active session: {session_id}")
                            continue
                        
                        try:
                            # Calculate directory size before removal
                            dir_size = self._get_directory_size(session_path)
                            
                            # Remove session directory
                            shutil.rmtree(session_path)
                            results['sessions_removed'] += 1
                            results['bytes_freed'] += dir_size
                            logger.info(f"Removed session directory: {session_id}")
                            
                        except Exception as e:
                            results['errors'].append(f"Error removing session {session_id}: {e}")
        
        except Exception as e:
            results['errors'].append(f"Error processing sessions folder: {e}")
        
        mb_freed = results['bytes_freed'] / (1024 * 1024)
        logger.info(f"Session cleanup: {results['sessions_removed']}/{results['sessions_found']} sessions removed, {mb_freed:.1f}MB freed")
        
        return results
    
    def _get_directory_size(self, directory: str) -> int:
        """Get total size of directory in bytes."""
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(directory):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    try:
                        total_size += os.path.getsize(filepath)
                    except (OSError, FileNotFoundError):
                        pass
        except Exception:
            pass
        return total_size
    
    def get_disk_usage(self) -> Dict[str, Any]:
        """Get disk usage information for data folder."""
        try:
            usage = shutil.disk_usage(self.data_folder)
            return {
                'total_bytes': usage.total,
                'used_bytes': usage.used,
                'free_bytes': usage.free,
                'total_gb': usage.total / (1024**3),
                'used_gb': usage.used / (1024**3),
                'free_gb': usage.free / (1024**3),
                'usage_percent': (usage.used / usage.total) * 100
            }
        except Exception as e:
            logger.error(f"Error getting disk usage: {e}")
            return {}
    
    def cleanup_all(self, 
                   force_kill_browsers: bool = False,
                   max_file_age_hours: int = 24,
                   active_sessions: List[str] = None) -> Dict[str, Any]:
        """
        Perform comprehensive cleanup.
        
        Args:
            force_kill_browsers: If True, forcefully kill browser processes
            max_file_age_hours: Maximum age of temp files to keep
            active_sessions: List of active session IDs to preserve
            
        Returns:
            Dictionary with comprehensive cleanup results
        """
        logger.info("Starting comprehensive cleanup...")
        
        results = {
            'browser_cleanup': {},
            'temp_cleanup': {},
            'session_cleanup': {},
            'disk_usage_before': self.get_disk_usage(),
            'disk_usage_after': {},
            'total_errors': 0
        }
        
        # Cleanup browser processes
        try:
            results['browser_cleanup'] = self.cleanup_browser_processes(force_kill_browsers)
        except Exception as e:
            results['browser_cleanup'] = {'error': str(e)}
        
        # Cleanup temp files
        try:
            results['temp_cleanup'] = self.cleanup_temp_files(max_file_age_hours)
        except Exception as e:
            results['temp_cleanup'] = {'error': str(e)}
        
        # Cleanup session directories
        try:
            results['session_cleanup'] = self.cleanup_session_directories(active_sessions)
        except Exception as e:
            results['session_cleanup'] = {'error': str(e)}
        
        # Get final disk usage
        results['disk_usage_after'] = self.get_disk_usage()
        
        # Count total errors
        for cleanup_type in ['browser_cleanup', 'temp_cleanup', 'session_cleanup']:
            errors = results[cleanup_type].get('errors', [])
            results['total_errors'] += len(errors)
        
        logger.info(f"Comprehensive cleanup completed with {results['total_errors']} errors")
        
        return results
