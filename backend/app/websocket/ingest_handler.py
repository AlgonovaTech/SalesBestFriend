"""
Audio ingestion WebSocket handler.
Receives audio chunks, transcribes, runs analysis, broadcasts updates.

Ported from main_trial_class.py /ingest endpoint — now per-call.
"""

import asyncio
import json
import time
import logging
from typing import Dict

from fastapi import WebSocket, WebSocketDisconnect

from app.websocket.manager import manager, CallSession
from app.services.audio.buffer import AudioBuffer
from app.services.transcription import transcribe_audio_buffer
from app.services.llm.checklist_analyzer import check_checklist_item
from app.services.llm.client_extractor import extract_client_card_fields
from app.services.llm.stage_detector import detect_stage, get_stage_timing_status
from app.services.llm.coaching_engine import generate_coaching_tip

logger = logging.getLogger(__name__)


async def handle_ingest(
    websocket: WebSocket,
    call_id: str,
    call_structure: list,
    client_card_fields: list,
    extraction_hints: Dict[str, str],
    pre_call_data: Dict | None = None,
):
    """
    Main ingest loop for a single call.

    ``call_structure`` and ``client_card_fields`` come from the
    playbook associated with the call.
    """
    session = await manager.get_or_create_session(call_id)
    session.call_start_time = time.time()
    session.stage_start_time = time.time()
    session.current_stage_id = (
        call_structure[0]["id"] if call_structure else ""
    )
    session.is_recording = True
    session.language = "id"

    await websocket.accept()
    logger.info("Ingest connected for call %s", call_id)

    audio_buffer = AudioBuffer(interval_seconds=10.0)

    try:
        while True:
            message = await websocket.receive()

            # Text messages (settings / commands)
            if "text" in message:
                try:
                    data = json.loads(message["text"])
                    if data.get("type") == "set_language":
                        session.language = data.get("language", "id")
                    elif data.get("type") == "manual_toggle_item":
                        iid = data.get("item_id")
                        if iid:
                            session.checklist_progress[iid] = not session.checklist_progress.get(iid, False)
                except Exception:
                    pass
                continue

            # Binary audio data
            if "bytes" in message:
                chunk = message["bytes"]
                if not audio_buffer.add_chunk(chunk):
                    continue

                # --- Buffer ready: transcribe + analyse ---
                buffer_data = audio_buffer.get_audio_data()

                loop = asyncio.get_event_loop()
                segments = await loop.run_in_executor(
                    None,
                    transcribe_audio_buffer,
                    buffer_data,
                    session.language,
                )

                if segments:
                    transcript = " ".join(s["text"] for s in segments)
                    session.accumulated_transcript += " " + transcript

                # Trim transcript to last 1000 words
                words = session.accumulated_transcript.split()
                if len(words) > 1000:
                    session.accumulated_transcript = " ".join(words[-1000:])

                if session.call_start_time is None:
                    audio_buffer.clear()
                    continue

                elapsed = time.time() - session.call_start_time

                # Stage detection
                detected = detect_stage(
                    conversation_text=session.accumulated_transcript[-2000:],
                    stages=call_structure,
                    elapsed_seconds=int(elapsed),
                    previous_stage_id=session.current_stage_id or None,
                )
                if detected != session.current_stage_id:
                    session.stage_start_time = time.time()
                session.current_stage_id = detected

                # Checklist analysis
                for stage in call_structure:
                    for item in stage["items"]:
                        iid = item["id"]
                        if session.checklist_progress.get(iid, False):
                            continue
                        last = session.checklist_last_check.get(iid, 0)
                        if time.time() - last < 30:
                            continue
                        session.checklist_last_check[iid] = time.time()

                        completed, _conf, evidence, _dbg = check_checklist_item(
                            item,
                            session.accumulated_transcript[-1500:],
                        )
                        if completed:
                            # Duplicate evidence check
                            if evidence and evidence in session.checklist_evidence.values():
                                continue
                            session.checklist_progress[iid] = True
                            session.checklist_evidence[iid] = evidence

                # Client card extraction
                current_vals = {
                    k: (v.get("value", "") if isinstance(v, dict) else str(v))
                    for k, v in session.client_card_data.items()
                }
                new_fields = extract_client_card_fields(
                    session.accumulated_transcript[-1000:],
                    current_vals,
                    client_card_fields,
                    extraction_hints,
                )
                for fid, fdata in new_fields.items():
                    session.client_card_data[fid] = fdata

                # Coaching tip
                current_stage_def = next(
                    (s for s in call_structure if s["id"] == session.current_stage_id),
                    None,
                )
                tip = generate_coaching_tip(
                    conversation_text=session.accumulated_transcript[-500:],
                    current_stage=current_stage_def,
                    pre_call_data=pre_call_data,
                    checklist_progress=session.checklist_progress,
                    client_card_data=session.client_card_data,
                )

                # Build update payload
                stages_payload = _build_stages_payload(
                    call_structure, session, int(elapsed),
                )
                stage_elapsed = (
                    int(time.time() - session.stage_start_time)
                    if session.stage_start_time else 0
                )

                update = {
                    "type": "update",
                    "callElapsedSeconds": int(elapsed),
                    "stageElapsedSeconds": stage_elapsed,
                    "currentStageId": session.current_stage_id,
                    "stages": stages_payload,
                    "clientCard": session.client_card_data,
                    "transcriptPreview": session.accumulated_transcript[-300:],
                }
                if tip:
                    update["coachingTip"] = tip

                await session.broadcast(update)
                audio_buffer.clear()

    except WebSocketDisconnect:
        logger.info("Ingest disconnected for call %s", call_id)
    except Exception:
        logger.exception("Ingest error for call %s", call_id)
    finally:
        session.is_recording = False


def _build_stages_payload(
    call_structure: list,
    session: CallSession,
    elapsed: int,
) -> list:
    result = []
    for stage in call_structure:
        items = []
        for item in stage["items"]:
            items.append({
                "id": item["id"],
                "type": item.get("type", "discuss"),
                "content": item["content"],
                "completed": session.checklist_progress.get(item["id"], False),
                "evidence": session.checklist_evidence.get(item["id"], ""),
            })

        timing = get_stage_timing_status(
            stage["id"], elapsed, call_structure,
        )

        result.append({
            "id": stage["id"],
            "name": stage["name"],
            "startOffsetSeconds": stage["startOffsetSeconds"],
            "durationSeconds": stage["durationSeconds"],
            "items": items,
            "isCurrent": stage["id"] == session.current_stage_id,
            "timingStatus": timing["status"],
            "timingMessage": timing["message"],
        })
    return result
