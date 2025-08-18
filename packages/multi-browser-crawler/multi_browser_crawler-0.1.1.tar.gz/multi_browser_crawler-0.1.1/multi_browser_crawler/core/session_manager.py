#!/usr/bin/env python3
"""
Browser Session Manager for Multi-Browser Crawler
=================================================

Manages browser sessions with:
- Unique directories per session
- Automatic cleanup of orphaned sessions
- Session reuse and attachment
- Named sessions for multiple crawler instances
- Process detection and cleanup
"""

import os
import time
import json
import psutil
import hashlib
import uuid
import asyncio
import fcntl
import signal
from typing import Dict, List, Optional, Tuple
import logging

from ..exceptions.errors import SessionError, ConfigurationError

logger = logging.getLogger(__name__)


class SessionManager:
    """Manages browser sessions with intelligent cleanup and reuse"""

    # Session limits configuration
    MAX_CONCURRENT_SESSIONS = 10
    SESSION_CLEANUP_RETRY_ATTEMPTS = 3
    SESSION_CLEANUP_RETRY_DELAY = 2  # seconds

    def __init__(self, data_folder: str = None, max_sessions: int = None):
        """
        Initialize session manager.
        
        Args:
            data_folder: Base data folder for sessions (defaults to ./data)
            max_sessions: Maximum concurrent sessions (defaults to 10)
        """
        self.data_folder = data_folder or os.path.join(os.getcwd(), "data")
        self.sessions_folder = os.path.join(self.data_folder, "browser_sessions")
        self.session_registry = os.path.join(self.sessions_folder, "session_registry.json")
        
        if max_sessions is not None:
            self.MAX_CONCURRENT_SESSIONS = max_sessions
        
        # Ensure directories exist
        os.makedirs(self.sessions_folder, exist_ok=True)
        
        # Load or create session registry
        self.registry = self._load_registry()

    def _load_registry(self) -> Dict:
        """Load session registry from disk"""
        if os.path.exists(self.session_registry):
            try:
                with open(self.session_registry, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load session registry: {e}")
        
        return {
            "sessions": {},
            "last_cleanup": 0
        }
    
    def _save_registry(self):
        """Save session registry to disk with file locking"""
        try:
            # Create a temporary file first, then atomic rename
            temp_file = self.session_registry + '.tmp'
            with open(temp_file, 'w') as f:
                json.dump(self.registry, f, indent=2)

            # Atomic rename to prevent race conditions
            import shutil
            shutil.move(temp_file, self.session_registry)
        except Exception as e:
            logger.error(f"Failed to save session registry: {e}")
            # Clean up temp file if it exists
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except:
                pass
    
    def _is_process_running(self, pid: int) -> bool:
        """Check if a process is still running"""
        try:
            return psutil.pid_exists(pid)
        except Exception:
            return False

    def _terminate_browser_process(self, pid: int, retry_attempts: int = 3) -> bool:
        """Forcefully terminate a browser process with retry logic"""
        if not self._is_process_running(pid):
            return True

        for attempt in range(retry_attempts):
            try:
                process = psutil.Process(pid)

                # First try graceful termination
                if attempt == 0:
                    process.terminate()
                    logger.info(f"🔄 Sent SIGTERM to process {pid}")
                else:
                    # Force kill if graceful termination failed
                    process.kill()
                    logger.info(f"💀 Sent SIGKILL to process {pid}")

                # Wait for process to die
                try:
                    process.wait(timeout=5)
                    logger.info(f"✅ Successfully terminated process {pid}")
                    return True
                except psutil.TimeoutExpired:
                    logger.warning(f"⏰ Process {pid} did not terminate within 5 seconds")

            except psutil.NoSuchProcess:
                logger.info(f"✅ Process {pid} already terminated")
                return True
            except psutil.AccessDenied:
                logger.error(f"❌ Access denied when trying to terminate process {pid}")
                return False
            except Exception as e:
                logger.error(f"❌ Error terminating process {pid}: {e}")

            if attempt < retry_attempts - 1:
                time.sleep(self.SESSION_CLEANUP_RETRY_DELAY)

        logger.error(f"❌ Failed to terminate process {pid} after {retry_attempts} attempts")
        return False
    
    def _get_browser_processes(self) -> List[int]:
        """Get all running browser processes"""
        browser_pids = []
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['name'] and 'chrome' in proc.info['name'].lower():
                        cmdline = proc.info.get('cmdline', [])
                        if any('--user-data-dir' in arg for arg in cmdline):
                            browser_pids.append(proc.info['pid'])
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            logger.warning(f"Error getting browser processes: {e}")
        
        return browser_pids

    def cleanup_orphaned_sessions(self):
        """Clean up session directories not associated with active processes"""
        logger.info("🧹 Cleaning up orphaned browser sessions...")

        current_time = time.time()
        active_pids = self._get_browser_processes()
        cleaned_count = 0

        # Clean up registry entries for dead processes
        sessions_to_remove = []
        for session_id, session_info in self.registry["sessions"].items():
            pid = session_info.get("pid")
            if pid:
                if not self._is_process_running(pid):
                    sessions_to_remove.append(session_id)

                    # Remove session directory
                    session_dir = session_info.get("user_data_dir")
                    if session_dir and os.path.exists(session_dir):
                        try:
                            import shutil
                            shutil.rmtree(session_dir)
                            logger.info(f"   Removed orphaned session: {session_id}")
                            cleaned_count += 1
                        except Exception as e:
                            logger.warning(f"   Failed to remove {session_dir}: {e}")
                else:
                    # Process is still running - check if it should be terminated
                    self._check_and_cleanup_long_running_session(session_id, session_info)

        # Update registry
        for session_id in sessions_to_remove:
            del self.registry["sessions"][session_id]

        # Clean up any remaining orphaned directories
        if os.path.exists(self.sessions_folder):
            for item in os.listdir(self.sessions_folder):
                if item.startswith("session_") and item != "session_registry.json":
                    session_dir = os.path.join(self.sessions_folder, item)
                    if os.path.isdir(session_dir):
                        # Check if this directory is in registry
                        found_in_registry = False
                        for session_info in self.registry["sessions"].values():
                            if session_info.get("user_data_dir") == session_dir:
                                found_in_registry = True
                                break

                        if not found_in_registry:
                            try:
                                import shutil
                                shutil.rmtree(session_dir)
                                logger.info(f"   Removed unregistered session dir: {item}")
                                cleaned_count += 1
                            except Exception as e:
                                logger.warning(f"   Failed to remove {session_dir}: {e}")

        self.registry["last_cleanup"] = current_time
        self._save_registry()

        if cleaned_count > 0:
            logger.info(f"✅ Cleaned up {cleaned_count} orphaned sessions")
        else:
            logger.info("✅ No orphaned sessions found")

    def _check_and_cleanup_long_running_session(self, session_id: str, session_info: Dict):
        """Check if a session should be cleaned up due to resource usage or age"""
        try:
            pid = session_info.get("pid")
            if not pid:
                return

            process = psutil.Process(pid)

            # Check memory usage (cleanup if using more than 1GB)
            memory_mb = process.memory_info().rss / 1024 / 1024
            if memory_mb > 1024:
                logger.warning(f"🧠 Session {session_id} using {memory_mb:.1f}MB memory - terminating")
                if self._terminate_browser_process(pid):
                    self._cleanup_session_files(session_id, session_info)
                return

            # Check age (cleanup if older than 24 hours)
            created_at = session_info.get("created_at", time.time())
            age_hours = (time.time() - created_at) / 3600
            if age_hours > 24:
                logger.warning(f"⏰ Session {session_id} is {age_hours:.1f} hours old - terminating")
                if self._terminate_browser_process(pid):
                    self._cleanup_session_files(session_id, session_info)
                return

        except psutil.NoSuchProcess:
            # Process already dead, will be cleaned up in main cleanup loop
            pass
        except Exception as e:
            logger.error(f"Error checking session {session_id}: {e}")

    def _cleanup_session_files(self, session_id: str, session_info: Dict):
        """Clean up session files and remove from registry"""
        session_dir = session_info.get("user_data_dir")
        if session_dir and os.path.exists(session_dir):
            try:
                import shutil
                shutil.rmtree(session_dir)
                logger.info(f"🗑️ Cleaned up session directory: {session_id}")
            except Exception as e:
                logger.warning(f"Failed to cleanup session directory: {e}")

        # Remove from registry
        if session_id in self.registry["sessions"]:
            del self.registry["sessions"][session_id]
            self._save_registry()
            logger.info(f"📝 Unregistered session: {session_id}")

    def _enforce_session_limits(self):
        """Enforce maximum concurrent session limits"""
        active_sessions = []

        # Get all active sessions
        for session_id, session_info in self.registry["sessions"].items():
            pid = session_info.get("pid")
            if pid and self._is_process_running(pid):
                active_sessions.append((session_id, session_info))

        # If we're over the limit, terminate oldest sessions
        if len(active_sessions) > self.MAX_CONCURRENT_SESSIONS:
            # Sort by last_used time (oldest first)
            active_sessions.sort(key=lambda x: x[1].get("last_used", 0))

            sessions_to_terminate = len(active_sessions) - self.MAX_CONCURRENT_SESSIONS
            logger.warning(f"🚫 Too many sessions ({len(active_sessions)}), terminating {sessions_to_terminate} oldest")

            for i in range(sessions_to_terminate):
                session_id, session_info = active_sessions[i]
                pid = session_info.get("pid")
                if pid and self._terminate_browser_process(pid):
                    self._cleanup_session_files(session_id, session_info)
                    logger.info(f"🗑️ Terminated session {session_id} due to limit enforcement")

    def create_session_id(self, session_name: str, force_unique: bool = False) -> str:
        """Create a session ID from session name"""
        if force_unique:
            # Force unique: add random ID for uniqueness
            unique_id = uuid.uuid4().hex[:8]
            return f"named_{session_name}_{unique_id}"
        else:
            # Named session: hash the name for consistency with conflict resolution
            name_hash = hashlib.md5(session_name.encode()).hexdigest()[:8]
            base_id = f"named_{session_name}_{name_hash}"

            # Check if this session ID already exists and is active
            if base_id in self.registry['sessions']:
                session_info = self.registry['sessions'][base_id]
                pid = session_info.get('pid')

                # If PID exists and process is still running, reuse the session
                if pid and self._is_process_running(pid):
                    return base_id
                else:
                    # Process is dead, clean up and reuse the ID
                    logger.info(f"Cleaning up dead session {base_id}")
                    self.unregister_session(base_id, cleanup_directory=True)

            return base_id

    def get_session_directory(self, session_id: str, create: bool = True) -> str:
        """Get the user data directory for a session"""
        session_dir = os.path.join(self.sessions_folder, f"session_{session_id}")

        if create:
            os.makedirs(session_dir, exist_ok=True)

        return session_dir

    def register_session(self, session_id: str, pid: int, session_name: str) -> Dict:
        """Register a new browser session"""
        session_info = {
            "session_id": session_id,
            "session_name": session_name,
            "pid": pid,
            "user_data_dir": self.get_session_directory(session_id),
            "created_at": time.time(),
            "last_used": time.time()
        }

        self.registry["sessions"][session_id] = session_info
        self._save_registry()

        logger.info(f"📝 Registered browser session: {session_id}")
        return session_info

    def find_existing_session(self, session_name: str) -> Optional[Dict]:
        """Find an existing session by name"""
        for session_id, session_info in self.registry["sessions"].items():
            # Check if process is still running
            pid = session_info.get("pid")
            if not pid or not self._is_process_running(pid):
                continue

            # Match by session name (exact match)
            if session_info.get("session_name") == session_name:
                logger.info(f"🔄 Found existing session: {session_name}")
                return session_info

        return None

    def update_session_usage(self, session_id: str):
        """Update last used timestamp for a session"""
        if session_id in self.registry["sessions"]:
            self.registry["sessions"][session_id]["last_used"] = time.time()
            self._save_registry()

    def unregister_session(self, session_id: str, cleanup_directory: bool = True):
        """Unregister a session and optionally clean up its directory"""
        if session_id in self.registry["sessions"]:
            session_info = self.registry["sessions"][session_id]

            if cleanup_directory:
                session_dir = session_info.get("user_data_dir")
                if session_dir and os.path.exists(session_dir):
                    try:
                        import shutil
                        shutil.rmtree(session_dir)
                        logger.info(f"🗑️ Cleaned up session directory: {session_id}")
                    except Exception as e:
                        logger.warning(f"Failed to cleanup session directory: {e}")

            del self.registry["sessions"][session_id]
            self._save_registry()
            logger.info(f"📝 Unregistered session: {session_id}")

    def list_sessions(self) -> List[Dict]:
        """List all registered sessions with their status"""
        sessions = []
        for session_id, session_info in self.registry["sessions"].items():
            pid = session_info.get("pid")
            is_active = pid and self._is_process_running(pid)

            session_status = {
                **session_info,
                "is_active": is_active,
                "age_hours": (time.time() - session_info.get("created_at", 0)) / 3600,
                "last_used_hours": (time.time() - session_info.get("last_used", 0)) / 3600
            }
            sessions.append(session_status)

        return sessions

    def get_session_strategy(self, session_name: str) -> Tuple[str, str, bool]:
        """
        Simple session strategy: reuse existing session by name or create new

        Returns:
            (session_id, user_data_dir, is_new_session)
        """
        # Cleanup orphaned sessions periodically
        if time.time() - self.registry.get("last_cleanup", 0) > 3600:  # Every hour
            self.cleanup_orphaned_sessions()

        # Enforce session limits before creating new sessions
        self._enforce_session_limits()

        # Try to find existing session by name
        existing_session = self.find_existing_session(session_name)
        if existing_session:
            self.update_session_usage(existing_session["session_id"])
            return (existing_session["session_id"],
                   existing_session["user_data_dir"],
                   False)

        # Check if we can create a new session (after cleanup)
        active_session_count = len([s for s in self.registry["sessions"].values()
                                   if s.get("pid") and self._is_process_running(s["pid"])])

        if active_session_count >= self.MAX_CONCURRENT_SESSIONS:
            logger.error(f"🚫 Cannot create new session: limit of {self.MAX_CONCURRENT_SESSIONS} reached")
            raise SessionError(f"Maximum concurrent sessions ({self.MAX_CONCURRENT_SESSIONS}) reached")

        # Create new session
        session_id = self.create_session_id(session_name)
        user_data_dir = self.get_session_directory(session_id)
        return session_id, user_data_dir, True
