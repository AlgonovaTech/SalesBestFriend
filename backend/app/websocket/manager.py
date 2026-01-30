"""
Per-call WebSocket connection manager.
Replaces the global connection sets from main_trial_class.py
with per-call isolation.
"""

import asyncio
import json
import logging
from typing import Dict, Set, Optional

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class CallSession:
    """State for a single live call."""

    def __init__(self, call_id: str):
        self.call_id = call_id
        self.coach_connections: Set[WebSocket] = set()
        self.accumulated_transcript: str = ""
        self.checklist_progress: Dict[str, bool] = {}
        self.checklist_evidence: Dict[str, str] = {}
        self.checklist_last_check: Dict[str, float] = {}
        self.client_card_data: Dict[str, Dict] = {}
        self.current_stage_id: str = ""
        self.stage_start_time: Optional[float] = None
        self.call_start_time: Optional[float] = None
        self.language: str = "id"
        self.is_recording: bool = False

    async def broadcast(self, data: dict):
        """Send JSON message to all connected coach clients."""
        msg = json.dumps(data)
        disconnected: Set[WebSocket] = set()
        for ws in self.coach_connections:
            try:
                await ws.send_text(msg)
            except Exception:
                disconnected.add(ws)
        self.coach_connections -= disconnected
        if disconnected:
            logger.info(
                "Removed %d dead coach connections for call %s",
                len(disconnected), self.call_id,
            )


class ConnectionManager:
    """Manages per-call WebSocket sessions."""

    def __init__(self):
        self._sessions: Dict[str, CallSession] = {}
        self._lock = asyncio.Lock()

    async def get_or_create_session(self, call_id: str) -> CallSession:
        async with self._lock:
            if call_id not in self._sessions:
                self._sessions[call_id] = CallSession(call_id)
                logger.info("Created session for call %s", call_id)
            return self._sessions[call_id]

    async def get_session(self, call_id: str) -> Optional[CallSession]:
        return self._sessions.get(call_id)

    async def remove_session(self, call_id: str):
        async with self._lock:
            session = self._sessions.pop(call_id, None)
            if session:
                # Close remaining coach connections
                for ws in session.coach_connections:
                    try:
                        await ws.close()
                    except Exception:
                        pass
                logger.info("Removed session for call %s", call_id)

    def active_sessions(self) -> int:
        return len(self._sessions)


# Singleton
manager = ConnectionManager()
