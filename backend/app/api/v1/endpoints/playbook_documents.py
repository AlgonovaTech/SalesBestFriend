from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.middleware.auth import get_current_user
from app.models.database import get_supabase_client
from app.models.schemas import (
    PlaybookDocumentResponse,
    PlaybookDocumentCreate,
    PlaybookDocumentUpdate,
    PlaybookDocumentType,
)
from typing import Optional

router = APIRouter()


def _verify_playbook_access(supabase, playbook_id: str, org_id: str):
    result = (
        supabase.table("playbooks")
        .select("id")
        .eq("id", playbook_id)
        .eq("organization_id", org_id)
        .single()
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Playbook not found")


@router.get("/{playbook_id}/documents", response_model=list[PlaybookDocumentResponse])
async def list_documents(
    playbook_id: str,
    document_type: Optional[PlaybookDocumentType] = Query(None),
    user: dict = Depends(get_current_user),
):
    """List documents for a playbook, optionally filtered by type."""
    supabase = get_supabase_client()
    _verify_playbook_access(supabase, playbook_id, user["organization_id"])

    query = (
        supabase.table("playbook_documents")
        .select("*")
        .eq("playbook_id", playbook_id)
    )
    if document_type:
        query = query.eq("document_type", document_type.value)

    result = query.order("sort_order").order("created_at").execute()
    return result.data or []


@router.post(
    "/{playbook_id}/documents",
    response_model=PlaybookDocumentResponse,
    status_code=201,
)
async def create_document(
    playbook_id: str,
    data: PlaybookDocumentCreate,
    user: dict = Depends(get_current_user),
):
    """Create a new document in a playbook."""
    supabase = get_supabase_client()
    _verify_playbook_access(supabase, playbook_id, user["organization_id"])

    payload = {
        "playbook_id": playbook_id,
        **data.model_dump(),
    }

    result = supabase.table("playbook_documents").insert(payload).execute()
    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to create document")
    return result.data[0]


@router.put(
    "/{playbook_id}/documents/{document_id}",
    response_model=PlaybookDocumentResponse,
)
async def update_document(
    playbook_id: str,
    document_id: str,
    data: PlaybookDocumentUpdate,
    user: dict = Depends(get_current_user),
):
    """Update a playbook document."""
    supabase = get_supabase_client()
    _verify_playbook_access(supabase, playbook_id, user["organization_id"])

    update_data = data.model_dump(exclude_none=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    result = (
        supabase.table("playbook_documents")
        .update(update_data)
        .eq("id", document_id)
        .eq("playbook_id", playbook_id)
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Document not found")
    return result.data[0]


@router.delete("/{playbook_id}/documents/{document_id}", status_code=204)
async def delete_document(
    playbook_id: str,
    document_id: str,
    user: dict = Depends(get_current_user),
):
    """Delete a playbook document."""
    supabase = get_supabase_client()
    _verify_playbook_access(supabase, playbook_id, user["organization_id"])

    supabase.table("playbook_documents").delete().eq("id", document_id).eq(
        "playbook_id", playbook_id
    ).execute()
