-- ============================================
-- Sales Best Friend v2 — Initial Schema
-- Run this in Supabase SQL Editor
-- ============================================

-- Organizations
CREATE TABLE IF NOT EXISTS organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    logo_url TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Teams (Indonesia, Mexico, Malaysia)
CREATE TABLE IF NOT EXISTS teams (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    country TEXT NOT NULL,
    language TEXT NOT NULL DEFAULT 'en',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_teams_org ON teams(organization_id);

-- User profiles (extends Supabase Auth)
CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    organization_id UUID NOT NULL REFERENCES organizations(id),
    team_id UUID REFERENCES teams(id),
    full_name TEXT NOT NULL,
    avatar_url TEXT,
    role TEXT NOT NULL DEFAULT 'sales_rep' CHECK (role IN ('sales_rep', 'team_lead', 'admin')),
    language_preference TEXT DEFAULT 'en',
    timezone TEXT DEFAULT 'UTC',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_user_profiles_org ON user_profiles(organization_id);
CREATE INDEX IF NOT EXISTS idx_user_profiles_team ON user_profiles(team_id);

-- Playbooks (methodology documents)
CREATE TABLE IF NOT EXISTS playbooks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    team_id UUID REFERENCES teams(id),
    name TEXT NOT NULL,
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_by UUID REFERENCES user_profiles(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_playbooks_org ON playbooks(organization_id);
CREATE INDEX IF NOT EXISTS idx_playbooks_team ON playbooks(team_id);

-- Playbook versions (versioned content)
CREATE TABLE IF NOT EXISTS playbook_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    playbook_id UUID NOT NULL REFERENCES playbooks(id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL,
    guidelines_content JSONB NOT NULL DEFAULT '{}',
    call_structure JSONB NOT NULL DEFAULT '[]',
    client_card_fields JSONB NOT NULL DEFAULT '[]',
    scoring_criteria JSONB NOT NULL DEFAULT '[]',
    intent_triggers JSONB NOT NULL DEFAULT '[]',
    published_at TIMESTAMPTZ,
    created_by UUID REFERENCES user_profiles(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(playbook_id, version_number)
);
CREATE INDEX IF NOT EXISTS idx_playbook_versions_playbook ON playbook_versions(playbook_id);

-- Calls
CREATE TABLE IF NOT EXISTS calls (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id),
    team_id UUID REFERENCES teams(id),
    user_id UUID NOT NULL REFERENCES user_profiles(id),
    playbook_version_id UUID REFERENCES playbook_versions(id),
    title TEXT,
    status TEXT NOT NULL DEFAULT 'scheduled' CHECK (status IN ('scheduled', 'live', 'processing', 'completed', 'failed')),
    source TEXT NOT NULL DEFAULT 'browser' CHECK (source IN ('browser', 'zoom', 'upload')),
    language TEXT NOT NULL DEFAULT 'en',
    started_at TIMESTAMPTZ,
    ended_at TIMESTAMPTZ,
    duration_seconds INTEGER,
    recording_storage_path TEXT,
    recording_size_bytes BIGINT,
    checklist_progress JSONB DEFAULT '{}',
    client_card_data JSONB DEFAULT '{}',
    pre_call_data JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_calls_user ON calls(user_id);
CREATE INDEX IF NOT EXISTS idx_calls_team ON calls(team_id);
CREATE INDEX IF NOT EXISTS idx_calls_org ON calls(organization_id);
CREATE INDEX IF NOT EXISTS idx_calls_status ON calls(status);
CREATE INDEX IF NOT EXISTS idx_calls_started_at ON calls(started_at DESC);

-- Call participants
CREATE TABLE IF NOT EXISTS call_participants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    call_id UUID NOT NULL REFERENCES calls(id) ON DELETE CASCADE,
    name TEXT,
    role TEXT CHECK (role IN ('sales_rep', 'prospect', 'decision_maker', 'observer')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_call_participants_call ON call_participants(call_id);

-- Call transcript segments
CREATE TABLE IF NOT EXISTS call_transcripts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    call_id UUID NOT NULL REFERENCES calls(id) ON DELETE CASCADE,
    segment_index INTEGER NOT NULL,
    start_seconds FLOAT NOT NULL,
    end_seconds FLOAT NOT NULL,
    text TEXT NOT NULL,
    speaker TEXT,
    confidence FLOAT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_call_transcripts_call ON call_transcripts(call_id);
CREATE INDEX IF NOT EXISTS idx_call_transcripts_call_index ON call_transcripts(call_id, segment_index);

-- Call analyses (AI-generated post-call)
CREATE TABLE IF NOT EXISTS call_analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    call_id UUID NOT NULL REFERENCES calls(id) ON DELETE CASCADE,
    summary TEXT,
    what_went_well JSONB DEFAULT '[]',
    needs_improvement JSONB DEFAULT '[]',
    goals_identified JSONB DEFAULT '[]',
    pain_points JSONB DEFAULT '[]',
    interest_signals JSONB DEFAULT '[]',
    buyer_profile_summary TEXT,
    overall_score FLOAT,
    model_used TEXT,
    analysis_duration_ms INTEGER,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_call_analyses_call ON call_analyses(call_id);

-- Call scores (per-criteria)
CREATE TABLE IF NOT EXISTS call_scores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    call_id UUID NOT NULL REFERENCES calls(id) ON DELETE CASCADE,
    criteria_name TEXT NOT NULL,
    criteria_max_score INTEGER NOT NULL DEFAULT 5,
    score FLOAT NOT NULL,
    reasoning TEXT,
    evidence TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_call_scores_call ON call_scores(call_id);
CREATE UNIQUE INDEX IF NOT EXISTS idx_call_scores_unique ON call_scores(call_id, criteria_name);

-- Call tasks (action items)
CREATE TABLE IF NOT EXISTS call_tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    call_id UUID NOT NULL REFERENCES calls(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES user_profiles(id),
    title TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'completed')),
    due_date DATE,
    priority TEXT DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high')),
    timestamp_seconds FLOAT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_call_tasks_call ON call_tasks(call_id);
CREATE INDEX IF NOT EXISTS idx_call_tasks_user ON call_tasks(user_id);

-- Tags
CREATE TABLE IF NOT EXISTS tags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    color TEXT DEFAULT '#2563EB',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(organization_id, name)
);

CREATE TABLE IF NOT EXISTS call_tags (
    call_id UUID NOT NULL REFERENCES calls(id) ON DELETE CASCADE,
    tag_id UUID NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (call_id, tag_id)
);

-- Updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply updated_at triggers
CREATE TRIGGER update_organizations_updated_at BEFORE UPDATE ON organizations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_teams_updated_at BEFORE UPDATE ON teams FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_user_profiles_updated_at BEFORE UPDATE ON user_profiles FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_playbooks_updated_at BEFORE UPDATE ON playbooks FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_calls_updated_at BEFORE UPDATE ON calls FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_call_analyses_updated_at BEFORE UPDATE ON call_analyses FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_call_tasks_updated_at BEFORE UPDATE ON call_tasks FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
