// ============================================
// Sales Best Friend v2 — TypeScript Types
// ============================================

// --- Auth & Users ---

export type UserRole = 'sales_rep' | 'team_lead' | 'admin'

export interface Organization {
  id: string
  name: string
  slug: string
  created_at: string
  updated_at: string
}

export interface Team {
  id: string
  organization_id: string
  name: string
  country: string
  language: string
  created_at: string
  updated_at: string
}

export interface UserProfile {
  id: string
  organization_id: string
  team_id: string
  full_name: string
  avatar_url: string | null
  role: UserRole
  language_preference: string
  timezone: string
  created_at: string
  updated_at: string
}

// --- Playbooks ---

export interface Playbook {
  id: string
  organization_id: string
  team_id: string | null
  name: string
  description: string
  is_active: boolean
  created_by: string
  created_at: string
  updated_at: string
}

export interface ChecklistItem {
  id: string
  label: string
  description: string
  keywords_required: string[]
  keywords_forbidden: string[]
}

export interface CallStage {
  id: string
  name: string
  order: number
  duration_minutes: number | null
  items: ChecklistItem[]
}

export interface ScoringCriterion {
  name: string
  max_score: number
  description: string
  weight: number
}

export interface ClientCardField {
  id: string
  label: string
  category: string
  type: 'text' | 'textarea' | 'select' | 'multi-select'
  extraction_hint: string
  options?: string[]
}

export interface PlaybookVersionContent {
  guidelines_content: string
  call_structure: CallStage[]
  client_card_fields: ClientCardField[]
  scoring_criteria: ScoringCriterion[]
}

export interface PlaybookVersion {
  id: string
  playbook_id: string
  version_number: number
  guidelines_content: string
  call_structure: CallStage[]
  client_card_fields: ClientCardField[]
  scoring_criteria: ScoringCriterion[]
  published_at: string | null
  created_by: string
  created_at: string
}

// --- Playbook Documents ---

export type PlaybookDocumentType = 'call' | 'analysis' | 'analytics'

export interface PlaybookDocument {
  id: string
  playbook_id: string
  document_type: PlaybookDocumentType
  title: string
  description: string
  content: string
  file_storage_path: string | null
  sort_order: number
  created_at: string
  updated_at: string
}

// --- Calls ---

export type CallStatus = 'scheduled' | 'live' | 'processing' | 'completed' | 'failed'
export type CallSource = 'browser' | 'zoom' | 'upload'

export interface PreCallData {
  client_name?: string
  client_phone?: string
  client_email?: string
  child_name?: string
  child_age?: number
  recommended_course?: string
  recommended_reason?: string
  source_channel?: string
  lead_source?: string
  school_level?: string
  interests?: string[]
  scheduled_at?: string
  company?: string
  context?: string
  previous_interactions?: string
  goals?: string
  notes?: string
  [key: string]: unknown
}

export interface ChecklistProgress {
  stages: {
    stage_id: string
    stage_name: string
    items: {
      item_id: string
      label: string
      completed: boolean
      confidence: number
      evidence: string | null
      completed_at: string | null
    }[]
  }[]
}

export interface ClientCardData {
  [field_id: string]: {
    value: string
    confidence: number
    evidence: string | null
    extracted_at: string | null
  }
}

export interface Call {
  id: string
  organization_id: string
  team_id: string
  user_id: string
  playbook_version_id: string | null
  title: string
  status: CallStatus
  source: CallSource
  language: string
  started_at: string | null
  ended_at: string | null
  duration_seconds: number | null
  recording_storage_path: string | null
  checklist_progress: ChecklistProgress | null
  client_card_data: ClientCardData | null
  pre_call_data: PreCallData | null
  audio_storage_path: string | null
  youtube_url: string | null
  processing_step: string | null
  created_at: string
  updated_at: string
  // Joined fields
  user?: UserProfile
  tags?: Tag[]
  participants?: CallParticipant[]
}

export interface CallParticipant {
  id: string
  call_id: string
  name: string
  role: string
}

export interface TranscriptSegment {
  id: string
  call_id: string
  segment_index: number
  start_seconds: number
  end_seconds: number
  text: string
  speaker: string
  confidence: number
  created_at: string
}

export interface CallAnalysis {
  id: string
  call_id: string
  summary: string
  what_went_well: string[]
  needs_improvement: string[]
  goals_identified: string[]
  pain_points: string[]
  interest_signals: string[]
  buyer_profile_summary: string
  overall_score: number
  model_used: string
  created_at: string
  updated_at: string
}

export interface CallScore {
  id: string
  call_id: string
  criteria_name: string
  criteria_max_score: number
  score: number
  reasoning: string
  evidence: string
  created_at: string
}

export interface CallTask {
  id: string
  call_id: string
  user_id: string
  title: string
  status: 'pending' | 'in_progress' | 'completed'
  due_date: string | null
  priority: string
  created_at: string
  updated_at: string
}

export interface Tag {
  id: string
  organization_id: string
  name: string
  color: string
}

// --- Analytics ---

export interface OverviewStats {
  total_calls: number
  calls_this_week: number
  average_score: number
  score_trend: number
  total_tasks_pending: number
}

export interface UserScoreSummary {
  user_id: string
  full_name: string
  avatar_url: string | null
  total_calls: number
  average_score: number
  scores_by_criteria: {
    criteria_name: string
    average_score: number
    max_score: number
  }[]
}

export interface RadarDataPoint {
  criteria: string
  score: number
  max: number
}

// --- WebSocket Messages ---

export interface WSTranscriptUpdate {
  type: 'transcript'
  segment: TranscriptSegment
}

export interface WSChecklistUpdate {
  type: 'checklist'
  stage_id: string
  item_id: string
  completed: boolean
  confidence: number
  evidence: string
}

export interface WSClientCardUpdate {
  type: 'client_card'
  field_id: string
  value: string
  confidence: number
  evidence: string
}

export interface WSStageUpdate {
  type: 'stage_change'
  stage_id: string
  stage_name: string
}

export interface WSCoachingTip {
  type: 'coaching_tip'
  tip: string
  category: string
}

export type WSCoachMessage =
  | WSTranscriptUpdate
  | WSChecklistUpdate
  | WSClientCardUpdate
  | WSStageUpdate
  | WSCoachingTip

// --- API Response wrappers ---

export interface PaginatedResponse<T> {
  data: T[]
  total: number
  page: number
  per_page: number
}
