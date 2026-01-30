-- ============================================
-- Sales Best Friend v2 — Row Level Security
-- Run this AFTER 001_initial_schema.sql
-- ============================================

-- Enable RLS on all tables
ALTER TABLE organizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE teams ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE playbooks ENABLE ROW LEVEL SECURITY;
ALTER TABLE playbook_versions ENABLE ROW LEVEL SECURITY;
ALTER TABLE calls ENABLE ROW LEVEL SECURITY;
ALTER TABLE call_participants ENABLE ROW LEVEL SECURITY;
ALTER TABLE call_transcripts ENABLE ROW LEVEL SECURITY;
ALTER TABLE call_analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE call_scores ENABLE ROW LEVEL SECURITY;
ALTER TABLE call_tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE tags ENABLE ROW LEVEL SECURITY;
ALTER TABLE call_tags ENABLE ROW LEVEL SECURITY;

-- ============================================
-- Helper function: get current user's role & org
-- ============================================
CREATE OR REPLACE FUNCTION auth.user_org_id()
RETURNS UUID AS $$
  SELECT organization_id FROM user_profiles WHERE id = auth.uid()
$$ LANGUAGE sql SECURITY DEFINER STABLE;

CREATE OR REPLACE FUNCTION auth.user_team_id()
RETURNS UUID AS $$
  SELECT team_id FROM user_profiles WHERE id = auth.uid()
$$ LANGUAGE sql SECURITY DEFINER STABLE;

CREATE OR REPLACE FUNCTION auth.user_role()
RETURNS TEXT AS $$
  SELECT role FROM user_profiles WHERE id = auth.uid()
$$ LANGUAGE sql SECURITY DEFINER STABLE;

-- ============================================
-- Organizations: users see their own org
-- ============================================
CREATE POLICY "users_see_own_org" ON organizations
    FOR SELECT USING (id = auth.user_org_id());

-- ============================================
-- Teams: users see teams in their org
-- ============================================
CREATE POLICY "users_see_org_teams" ON teams
    FOR SELECT USING (organization_id = auth.user_org_id());

CREATE POLICY "admins_manage_teams" ON teams
    FOR ALL USING (
        organization_id = auth.user_org_id()
        AND auth.user_role() = 'admin'
    );

-- ============================================
-- User profiles
-- ============================================
CREATE POLICY "users_see_own_profile" ON user_profiles
    FOR SELECT USING (id = auth.uid());

CREATE POLICY "users_update_own_profile" ON user_profiles
    FOR UPDATE USING (id = auth.uid());

CREATE POLICY "leads_see_team_profiles" ON user_profiles
    FOR SELECT USING (
        auth.user_role() = 'team_lead'
        AND team_id = auth.user_team_id()
    );

CREATE POLICY "admins_see_all_profiles" ON user_profiles
    FOR SELECT USING (
        auth.user_role() = 'admin'
        AND organization_id = auth.user_org_id()
    );

CREATE POLICY "admins_manage_profiles" ON user_profiles
    FOR ALL USING (
        auth.user_role() = 'admin'
        AND organization_id = auth.user_org_id()
    );

-- ============================================
-- Playbooks: org-wide read, admin/lead write
-- ============================================
CREATE POLICY "users_see_org_playbooks" ON playbooks
    FOR SELECT USING (organization_id = auth.user_org_id());

CREATE POLICY "admins_leads_manage_playbooks" ON playbooks
    FOR ALL USING (
        organization_id = auth.user_org_id()
        AND auth.user_role() IN ('admin', 'team_lead')
    );

CREATE POLICY "users_see_playbook_versions" ON playbook_versions
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM playbooks
            WHERE playbooks.id = playbook_versions.playbook_id
            AND playbooks.organization_id = auth.user_org_id()
        )
    );

CREATE POLICY "admins_leads_manage_versions" ON playbook_versions
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM playbooks
            WHERE playbooks.id = playbook_versions.playbook_id
            AND playbooks.organization_id = auth.user_org_id()
        )
        AND auth.user_role() IN ('admin', 'team_lead')
    );

-- ============================================
-- Calls: role-based access
-- ============================================

-- Sales rep sees own calls
CREATE POLICY "rep_own_calls_select" ON calls
    FOR SELECT USING (user_id = auth.uid());

CREATE POLICY "rep_own_calls_insert" ON calls
    FOR INSERT WITH CHECK (user_id = auth.uid());

CREATE POLICY "rep_own_calls_update" ON calls
    FOR UPDATE USING (user_id = auth.uid());

-- Team lead sees team calls
CREATE POLICY "lead_team_calls" ON calls
    FOR SELECT USING (
        auth.user_role() = 'team_lead'
        AND team_id = auth.user_team_id()
    );

-- Admin sees all org calls
CREATE POLICY "admin_org_calls" ON calls
    FOR SELECT USING (
        auth.user_role() = 'admin'
        AND organization_id = auth.user_org_id()
    );

-- ============================================
-- Call sub-tables: inherit call access
-- ============================================

-- Transcripts
CREATE POLICY "transcripts_via_call" ON call_transcripts
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM calls WHERE calls.id = call_transcripts.call_id
            AND (
                calls.user_id = auth.uid()
                OR (auth.user_role() = 'team_lead' AND calls.team_id = auth.user_team_id())
                OR (auth.user_role() = 'admin' AND calls.organization_id = auth.user_org_id())
            )
        )
    );

CREATE POLICY "transcripts_insert" ON call_transcripts
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM calls WHERE calls.id = call_transcripts.call_id
            AND calls.user_id = auth.uid()
        )
    );

-- Analyses
CREATE POLICY "analyses_via_call" ON call_analyses
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM calls WHERE calls.id = call_analyses.call_id
            AND (
                calls.user_id = auth.uid()
                OR (auth.user_role() = 'team_lead' AND calls.team_id = auth.user_team_id())
                OR (auth.user_role() = 'admin' AND calls.organization_id = auth.user_org_id())
            )
        )
    );

-- Scores
CREATE POLICY "scores_via_call" ON call_scores
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM calls WHERE calls.id = call_scores.call_id
            AND (
                calls.user_id = auth.uid()
                OR (auth.user_role() = 'team_lead' AND calls.team_id = auth.user_team_id())
                OR (auth.user_role() = 'admin' AND calls.organization_id = auth.user_org_id())
            )
        )
    );

-- Tasks
CREATE POLICY "tasks_via_call" ON call_tasks
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM calls WHERE calls.id = call_tasks.call_id
            AND (
                calls.user_id = auth.uid()
                OR (auth.user_role() = 'team_lead' AND calls.team_id = auth.user_team_id())
                OR (auth.user_role() = 'admin' AND calls.organization_id = auth.user_org_id())
            )
        )
    );

-- Participants
CREATE POLICY "participants_via_call" ON call_participants
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM calls WHERE calls.id = call_participants.call_id
            AND (
                calls.user_id = auth.uid()
                OR (auth.user_role() = 'team_lead' AND calls.team_id = auth.user_team_id())
                OR (auth.user_role() = 'admin' AND calls.organization_id = auth.user_org_id())
            )
        )
    );

-- ============================================
-- Tags: org-scoped
-- ============================================
CREATE POLICY "users_see_org_tags" ON tags
    FOR SELECT USING (organization_id = auth.user_org_id());

CREATE POLICY "admins_manage_tags" ON tags
    FOR ALL USING (
        organization_id = auth.user_org_id()
        AND auth.user_role() IN ('admin', 'team_lead')
    );

CREATE POLICY "call_tags_via_call" ON call_tags
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM calls WHERE calls.id = call_tags.call_id
            AND (
                calls.user_id = auth.uid()
                OR (auth.user_role() = 'team_lead' AND calls.team_id = auth.user_team_id())
                OR (auth.user_role() = 'admin' AND calls.organization_id = auth.user_org_id())
            )
        )
    );

-- ============================================
-- Service role bypass (for backend API)
-- The backend uses service_role key which bypasses RLS
-- These policies only affect client-side Supabase access
-- ============================================
