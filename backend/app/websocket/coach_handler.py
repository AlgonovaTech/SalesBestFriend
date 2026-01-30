"""
Coach WebSocket handler.
Sends real-time coaching data to the frontend.

Ported from main_trial_class.py /coach endpoint — now per-call.
"""

import json
import logging

from fastapi import WebSocket, WebSocketDisconnect

from app.websocket.manager import manager

logger = logging.getLogger(__name__)


async def handle_coach(
    websocket: WebSocket,
    call_id: str,
    call_structure: list,
):
    """
    Coach connection: receives commands and forwards live updates.
    Updates are broadcast from the ingest handler via ``session.broadcast()``.
    """
    session = await manager.get_or_create_session(call_id)
    await websocket.accept()
    session.coach_connections.add(websocket)
    logger.info(
        "Coach connected for call %s (total: %d)",
        call_id, len(session.coach_connections),
    )

    # Send initial state
    initial = {
        "type": "initial",
        "callElapsedSeconds": 0,
        "currentStageId": call_structure[0]["id"] if call_structure else None,
        "stages": [
            {
                "id": s["id"],
                "name": s["name"],
                "startOffsetSeconds": s["startOffsetSeconds"],
                "durationSeconds": s["durationSeconds"],
                "items": [
                    {
                        "id": it["id"],
                        "type": it.get("type", "discuss"),
                        "content": it["content"],
                        "completed": session.checklist_progress.get(it["id"], False),
                        "evidence": session.checklist_evidence.get(it["id"], ""),
                    }
                    for it in s["items"]
                ],
                "isCurrent": False,
                "timingStatus": "not_started",
                "timingMessage": "Not started",
            }
            for s in call_structure
        ],
        "clientCard": session.client_card_data,
        "transcriptPreview": session.accumulated_transcript[-300:] if session.accumulated_transcript else "",
    }
    await websocket.send_text(json.dumps(initial))

    try:
        while True:
            text_data = await websocket.receive_text()
            msg = json.loads(text_data)

            if msg.get("type") == "set_language":
                session.language = msg.get("language", "id")

            elif msg.get("type") == "manual_toggle_item":
                item_id = msg.get("item_id")
                if item_id:
                    session.checklist_progress[item_id] = not session.checklist_progress.get(item_id, False)

            elif msg.get("type") == "update_client_card":
                field_id = msg.get("field_id")
                value = msg.get("value")
                if field_id:
                    session.client_card_data[field_id] = value

    except WebSocketDisconnect:
        session.coach_connections.discard(websocket)
        logger.info(
            "Coach disconnected for call %s (remaining: %d)",
            call_id, len(session.coach_connections),
        )
    except Exception:
        session.coach_connections.discard(websocket)
        logger.exception("Coach error for call %s", call_id)
