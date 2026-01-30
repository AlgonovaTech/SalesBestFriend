from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum


# --- Enums ---

class UserRole(str, Enum):
    sales_rep = "sales_rep"
    team_lead = "team_lead"
    admin = "admin"


class CallStatus(str, Enum):
    scheduled = "scheduled"
    live = "live"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class CallSource(str, Enum):
    browser = "browser"
    zoom = "zoom"
    upload = "upload"


class TaskStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"


# --- User ---

class UserProfileResponse(BaseModel):
    id: str
    organization_id: str
    team_id: str
    full_name: str
    avatar_url: Optional[str] = None
    role: UserRole
    language_preference: str = "en"
    timezone: str = "UTC"
    created_at: datetime
    updated_at: datetime


class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    language_preference: Optional[str] = None
    timezone: Optional[str] = None


# --- Organization ---

class OrganizationResponse(BaseModel):
    id: str
    name: str
    slug: str
    created_at: datetime
    updated_at: datetime


class TeamResponse(BaseModel):
    id: str
    organization_id: str
    name: str
    country: str
    language: str
    created_at: datetime
    updated_at: datetime


# --- Playbook ---

class PlaybookResponse(BaseModel):
    id: str
    organization_id: str
    team_id: Optional[str] = None
    name: str
    description: str
    is_active: bool
    created_by: str
    created_at: datetime
    updated_at: datetime


class PlaybookCreate(BaseModel):
    name: str
    description: str = ""
    team_id: Optional[str] = None


class PlaybookUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class PlaybookVersionResponse(BaseModel):
    id: str
    playbook_id: str
    version_number: int
    guidelines_content: Optional[str] = None
    call_structure: Optional[dict] = None
    client_card_fields: Optional[dict] = None
    scoring_criteria: Optional[dict] = None
    published_at: Optional[datetime] = None
    created_by: str
    created_at: datetime


class PlaybookVersionCreate(BaseModel):
    guidelines_content: Optional[str] = None
    call_structure: Optional[dict] = None
    client_card_fields: Optional[dict] = None
    scoring_criteria: Optional[dict] = None


# --- Call ---

class CallResponse(BaseModel):
    id: str
    organization_id: str
    team_id: str
    user_id: str
    playbook_version_id: Optional[str] = None
    title: str
    status: CallStatus
    source: CallSource
    language: str = "en"
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    checklist_progress: Optional[dict] = None
    client_card_data: Optional[dict] = None
    pre_call_data: Optional[dict] = None
    created_at: datetime
    updated_at: datetime


class CallCreate(BaseModel):
    title: str
    source: CallSource = CallSource.browser
    language: str = "en"
    playbook_version_id: Optional[str] = None
    pre_call_data: Optional[dict] = None


class CallUpdate(BaseModel):
    title: Optional[str] = None
    status: Optional[CallStatus] = None
    ended_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    checklist_progress: Optional[dict] = None
    client_card_data: Optional[dict] = None
    pre_call_data: Optional[dict] = None


# --- Transcript ---

class TranscriptSegmentResponse(BaseModel):
    id: str
    call_id: str
    segment_index: int
    start_seconds: float
    end_seconds: float
    text: str
    speaker: str
    confidence: float
    created_at: datetime


# --- Analysis ---

class CallAnalysisResponse(BaseModel):
    id: str
    call_id: str
    summary: str
    what_went_well: Optional[list] = None
    needs_improvement: Optional[list] = None
    goals_identified: Optional[list] = None
    pain_points: Optional[list] = None
    interest_signals: Optional[list] = None
    buyer_profile_summary: Optional[str] = None
    overall_score: Optional[float] = None
    model_used: str
    created_at: datetime
    updated_at: datetime


# --- Score ---

class CallScoreResponse(BaseModel):
    id: str
    call_id: str
    criteria_name: str
    criteria_max_score: int
    score: float
    reasoning: str
    evidence: str
    created_at: datetime


# --- Task ---

class CallTaskResponse(BaseModel):
    id: str
    call_id: str
    user_id: str
    title: str
    status: TaskStatus
    due_date: Optional[str] = None
    priority: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class CallTaskCreate(BaseModel):
    title: str
    due_date: Optional[str] = None
    priority: str = "medium"


class CallTaskUpdate(BaseModel):
    title: Optional[str] = None
    status: Optional[TaskStatus] = None
    due_date: Optional[str] = None
    priority: Optional[str] = None


# --- Tag ---

class TagResponse(BaseModel):
    id: str
    organization_id: str
    name: str
    color: str


class TagCreate(BaseModel):
    name: str
    color: str = "gray"


# --- Analytics ---

class OverviewStatsResponse(BaseModel):
    total_calls: int = 0
    calls_this_week: int = 0
    average_score: float = 0.0
    score_trend: float = 0.0
    total_tasks_pending: int = 0


class UserScoreSummaryResponse(BaseModel):
    user_id: str
    full_name: str
    avatar_url: Optional[str] = None
    total_calls: int = 0
    average_score: float = 0.0
    scores_by_criteria: list[dict] = Field(default_factory=list)


class RadarDataPointResponse(BaseModel):
    criteria: str
    score: float
    max: float


# --- Paginated ---

class PaginatedResponse(BaseModel):
    data: list
    total: int
    page: int
    per_page: int
