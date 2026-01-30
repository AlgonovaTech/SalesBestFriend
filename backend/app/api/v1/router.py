from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, organizations, playbooks, playbook_documents, calls, tags, analytics

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(organizations.router, prefix="/organizations", tags=["organizations"])
api_router.include_router(playbooks.router, prefix="/playbooks", tags=["playbooks"])
api_router.include_router(playbook_documents.router, prefix="/playbooks", tags=["playbook-documents"])
api_router.include_router(calls.router, prefix="/calls", tags=["calls"])
api_router.include_router(tags.router, prefix="/tags", tags=["tags"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
