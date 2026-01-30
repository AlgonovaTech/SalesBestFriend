from fastapi import FastAPI, WebSocket, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.api.v1.router import api_router
from app.websocket.manager import manager
from app.websocket.ingest_handler import handle_ingest
from app.websocket.coach_handler import handle_coach
from app.models.database import get_supabase_client

settings = get_settings()

app = FastAPI(
    title="Sales Best Friend API",
    version="2.0.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# REST Routes
app.include_router(api_router)


# ---------------------------------------------------------------------------
# WebSocket Routes (per-call)
# ---------------------------------------------------------------------------

def _get_call_config(call_id: str) -> dict:
    """
    Load call structure and client card fields for a call.
    Falls back to defaults if no playbook is attached.
    """
    from call_structure_config import get_default_call_structure
    from client_card_config import get_default_client_card_fields, LLM_EXTRACTION_HINTS

    # Try to load playbook from call record
    supabase = get_supabase_client()
    call_result = supabase.table("calls").select(
        "playbook_version_id, pre_call_data"
    ).eq("id", call_id).execute()

    call_data = call_result.data[0] if call_result.data else {}
    version_id = call_data.get("playbook_version_id")
    pre_call_data = call_data.get("pre_call_data")

    if version_id:
        version_result = supabase.table("playbook_versions").select(
            "call_structure, client_card_fields, scoring_criteria"
        ).eq("id", version_id).single().execute()

        if version_result.data:
            v = version_result.data
            return {
                "call_structure": v.get("call_structure") or get_default_call_structure(),
                "client_card_fields": v.get("client_card_fields") or get_default_client_card_fields(),
                "extraction_hints": LLM_EXTRACTION_HINTS,
                "pre_call_data": pre_call_data,
            }

    # Defaults
    return {
        "call_structure": get_default_call_structure(),
        "client_card_fields": get_default_client_card_fields(),
        "extraction_hints": LLM_EXTRACTION_HINTS,
        "pre_call_data": pre_call_data,
    }


@app.websocket("/ws/call/{call_id}/ingest")
async def ws_ingest(websocket: WebSocket, call_id: str):
    cfg = _get_call_config(call_id)
    await handle_ingest(
        websocket=websocket,
        call_id=call_id,
        call_structure=cfg["call_structure"],
        client_card_fields=cfg["client_card_fields"],
        extraction_hints=cfg["extraction_hints"],
        pre_call_data=cfg["pre_call_data"],
    )


@app.websocket("/ws/call/{call_id}/coach")
async def ws_coach(websocket: WebSocket, call_id: str):
    cfg = _get_call_config(call_id)
    await handle_coach(
        websocket=websocket,
        call_id=call_id,
        call_structure=cfg["call_structure"],
    )


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

@app.get("/health")
async def root_health():
    return {
        "status": "ok",
        "version": "2.0.0",
        "active_sessions": manager.active_sessions(),
    }
