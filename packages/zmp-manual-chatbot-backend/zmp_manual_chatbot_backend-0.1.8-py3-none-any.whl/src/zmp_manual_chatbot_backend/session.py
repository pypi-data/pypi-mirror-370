import asyncio
import uuid
import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta

class SessionManager:
    """
    Manages per-session state and streaming queues for chatbot sessions.
    Enhanced with queue isolation, session task management, and proper cleanup.
    """
    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.queues: Dict[str, asyncio.Queue] = {}
        self.queue_locks: Dict[str, asyncio.Lock] = {}
        self.session_tasks: Dict[str, Optional[asyncio.Task]] = {}
        self.session_timestamps: Dict[str, datetime] = {}
        self.cleanup_task: Optional[asyncio.Task] = None
        self._cleanup_interval = 3600  # 1 hour
        self._session_timeout = 3600  # 1 hour

    async def get_or_create_session(self, session_id: str) -> Tuple[asyncio.Queue, asyncio.Lock, Optional[asyncio.Task]]:
        """
        Get or create a session with proper queue isolation and task management.
        Returns (queue, lock, session_task) tuple.
        """
        if session_id not in self.sessions:
            # Create new session
            self.sessions[session_id] = {}
            self.queues[session_id] = asyncio.Queue()
            self.queue_locks[session_id] = asyncio.Lock()
            self.session_tasks[session_id] = None
            self.session_timestamps[session_id] = datetime.now()
            logging.info(f"Created new session: {session_id}")
        else:
            # Update timestamp for existing session
            self.session_timestamps[session_id] = datetime.now()
            logging.info(f"Retrieved existing session: {session_id}")

        return (
            self.queues[session_id],
            self.queue_locks[session_id],
            self.session_tasks[session_id]
        )

    def get_session(self, session_id: str) -> Dict[str, Any]:
        """
        Get the state dict for a session.
        """
        return self.sessions.get(session_id, {})

    def get_queue(self, session_id: str) -> asyncio.Queue:
        """
        Get the streaming queue for a session.
        """
        return self.queues.get(session_id)

    def get_queue_lock(self, session_id: str) -> asyncio.Lock:
        """
        Get the queue lock for a session.
        """
        return self.queue_locks.get(session_id)

    def get_session_task(self, session_id: str) -> Optional[asyncio.Task]:
        """
        Get the current session task.
        """
        return self.session_tasks.get(session_id)

    async def set_session_task(self, session_id: str, task: asyncio.Task):
        """
        Set the session task for tracking workflow execution.
        """
        self.session_tasks[session_id] = task
        logging.info(f"Set session task for {session_id}")

    async def delete_session(self, session_id: str):
        """
        Remove a session and its associated resources including session state files.
        """
        # Cancel any running task
        task = self.session_tasks.get(session_id)
        if task and not task.done():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

        # Remove session state file from disk
        try:
            from .utils import delete_session_file
            await delete_session_file(session_id)
        except Exception as e:
            logging.error(f"Failed to delete session file for {session_id}: {e}")

        # Remove session resources
        self.sessions.pop(session_id, None)
        self.queues.pop(session_id, None) 
        self.queue_locks.pop(session_id, None)
        self.session_tasks.pop(session_id, None)
        self.session_timestamps.pop(session_id, None)
        
        logging.info(f"Deleted session: {session_id}")

    async def cleanup_expired_sessions(self):
        """
        Clean up sessions that have exceeded the timeout period and remove orphaned session files.
        """
        current_time = datetime.now()
        expired_sessions = []

        for session_id, timestamp in self.session_timestamps.items():
            if current_time - timestamp > timedelta(seconds=self._session_timeout):
                expired_sessions.append(session_id)

        for session_id in expired_sessions:
            logging.info(f"Cleaning up expired session: {session_id}")
            await self.delete_session(session_id)

        # Also clean up any orphaned session files that don't correspond to active sessions
        try:
            from .utils import cleanup_expired_session_files
            # Clean up files older than session timeout period (convert seconds to hours)
            max_age_hours = max(1, self._session_timeout // 3600)  # At least 1 hour
            deleted_files = await cleanup_expired_session_files(max_age_hours)
            if deleted_files > 0:
                logging.info(f"Cleaned up {deleted_files} orphaned session files")
        except Exception as e:
            logging.error(f"Error during session file cleanup: {e}")

    async def start_cleanup_task(self):
        """
        Start the background cleanup task.
        """
        if self.cleanup_task is None or self.cleanup_task.done():
            self.cleanup_task = asyncio.create_task(self._cleanup_loop())
            logging.info("Started session cleanup task")

    async def stop_cleanup_task(self):
        """
        Stop the background cleanup task.
        """
        if self.cleanup_task and not self.cleanup_task.done():
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass
            logging.info("Stopped session cleanup task")

    async def _cleanup_loop(self):
        """
        Background loop for cleaning up expired sessions.
        """
        while True:
            try:
                await asyncio.sleep(self._cleanup_interval)
                await self.cleanup_expired_sessions()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logging.error(f"Error in cleanup loop: {e}")

    def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """
        Get information about a session.
        """
        if session_id not in self.sessions:
            return {"exists": False}

        task = self.session_tasks.get(session_id)
        timestamp = self.session_timestamps.get(session_id)
        
        return {
            "exists": True,
            "has_task": task is not None,
            "task_done": task.done() if task else None,
            "task_cancelled": task.cancelled() if task else None,
            "created_at": timestamp.isoformat() if timestamp else None,
            "age_seconds": (datetime.now() - timestamp).total_seconds() if timestamp else None
        }

    def get_all_sessions_info(self) -> Dict[str, Dict[str, Any]]:
        """
        Get information about all sessions.
        """
        return {
            session_id: self.get_session_info(session_id)
            for session_id in self.sessions.keys()
        } 