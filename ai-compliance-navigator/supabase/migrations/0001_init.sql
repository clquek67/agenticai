-- ============================================================================
-- AI Compliance Navigator — Phase 1 migration
-- Run this whole file once in the Supabase SQL editor (dedicated instance).
-- Creates: enums, tables, indexes, RLS policies, least-privilege grants.
-- ============================================================================

-- ---------------------------------------------------------------------------
-- 1. Enums
-- ---------------------------------------------------------------------------

create type industry_type as enum (
  'healthcare',
  'government',
  'aviation',
  'financial_services',
  'technology',
  'manufacturing',
  'energy_utilities',
  'telecommunications',
  'retail_ecommerce',
  'logistics_transport',
  'education',
  'insurance',
  'pharma_biotech',
  'media_entertainment',
  'real_estate_construction',
  'agriculture',
  'hospitality_travel',
  'legal_professional_services',
  'defense',
  'maritime',
  'other'
);

create type region_type as enum ('asean', 'korea', 'eu', 'us', 'global');

-- Full framework/module list up front (core frameworks + regional/sector
-- modules used by the Phase 3 scope selector). Extending a Postgres enum
-- later is possible but awkward, so we define everything now.
create type framework_type as enum (
  -- core frameworks
  'nist_ai_rmf',
  'iso_42001',
  'owasp_llm',
  'eu_ai_act',
  -- regional / sector modules
  'gdpr_ai',
  'mas_trm',
  'imda_model_ai',
  'korea_ai_act',
  'pdpa',
  'pipa',
  'us_state_ai',
  'hipaa_ai',
  'critical_infra',
  'gxp_ai'
);

create type assessment_status as enum ('draft', 'in_progress', 'completed');

create type answer_type as enum ('yes', 'partial', 'no', 'not_applicable');

create type applicability_type as enum ('core', 'regulatory', 'sector', 'certification');

-- ---------------------------------------------------------------------------
-- 2. Tables
-- ---------------------------------------------------------------------------

create table organizations (
  id          uuid primary key default gen_random_uuid(),
  name        text not null check (char_length(name) between 1 and 200),
  industry    industry_type not null,
  region      region_type not null,
  created_at  timestamptz not null default now(),
  user_id     uuid not null references auth.users (id) on delete cascade
);

create index organizations_user_id_idx on organizations (user_id);

create table assessments (
  id              uuid primary key default gen_random_uuid(),
  organization_id uuid not null references organizations (id) on delete cascade,
  framework       framework_type not null,
  status          assessment_status not null default 'draft',
  overall_score   numeric check (overall_score is null or (overall_score >= 0 and overall_score <= 100)),
  started_at      timestamptz not null default now(),
  completed_at    timestamptz
);

create index assessments_organization_id_idx on assessments (organization_id);

-- Global control library (reference data, seeded in Phase 2).
create table controls (
  id                   text primary key,
  framework            framework_type not null,
  category             text not null,
  title                text not null,
  description          text not null,
  weight               numeric not null default 1 check (weight > 0),
  -- Only holds entries where a control deviates from the "medium" default,
  -- e.g. {"healthcare": "high", "aviation": "critical"}.
  industry_criticality jsonb not null default '{}'::jsonb
);

create index controls_framework_idx on controls (framework);

create table responses (
  id             uuid primary key default gen_random_uuid(),
  assessment_id  uuid not null references assessments (id) on delete cascade,
  control_id     text not null references controls (id),
  answer         answer_type not null,
  evidence_notes text,
  updated_at     timestamptz not null default now(),
  -- One answer per control per assessment; enables idempotent upserts
  -- from the auto-saving assessment runner.
  unique (assessment_id, control_id)
);

create index responses_assessment_id_idx on responses (assessment_id);

create table reports (
  id                 uuid primary key default gen_random_uuid(),
  assessment_id      uuid not null references assessments (id) on delete cascade,
  generated_markdown text,
  ai_summary         text,
  created_at         timestamptz not null default now()
);

create index reports_assessment_id_idx on reports (assessment_id);

-- Mapping table driving scope recommendations (reference data, seeded in
-- Phase 2). NULL industry or region = applies to all.
create table framework_applicability (
  id            uuid primary key default gen_random_uuid(),
  framework     framework_type not null,
  industry      text,
  region        text,
  applicability applicability_type not null,
  rationale     text not null,
  unique nulls not distinct (framework, industry, region)
);

create index framework_applicability_framework_idx on framework_applicability (framework);

-- ---------------------------------------------------------------------------
-- 3. Keep responses.updated_at accurate on every save
-- ---------------------------------------------------------------------------

create or replace function set_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at := now();
  return new;
end;
$$;

create trigger responses_set_updated_at
  before update on responses
  for each row
  execute function set_updated_at();

-- ---------------------------------------------------------------------------
-- 4. Row Level Security
--
-- Ownership model: organizations.user_id is the root of ownership; every
-- other user-data table is scoped through it. All policies are owner-scoped
-- (auth.uid() = user_id or a membership lookup) — no `true` /
-- `auth.uid() IS NOT NULL` policies anywhere.
--
-- controls and framework_applicability are global reference tables with no
-- owner, so they get RLS enabled with NO policies: deny-by-default for anon
-- and authenticated. The app reads them server-side with the service-role
-- client (they contain no user data).
-- ---------------------------------------------------------------------------

alter table organizations           enable row level security;
alter table assessments             enable row level security;
alter table responses               enable row level security;
alter table reports                 enable row level security;
alter table controls                enable row level security;
alter table framework_applicability enable row level security;

-- organizations ------------------------------------------------------------

create policy "organizations_select_own"
  on organizations for select
  to authenticated
  using (auth.uid() = user_id);

create policy "organizations_insert_own"
  on organizations for insert
  to authenticated
  with check (auth.uid() = user_id);

create policy "organizations_update_own"
  on organizations for update
  to authenticated
  using (auth.uid() = user_id)
  with check (auth.uid() = user_id);

create policy "organizations_delete_own"
  on organizations for delete
  to authenticated
  using (auth.uid() = user_id);

-- assessments (scoped through owning organization) ---------------------------

create policy "assessments_select_own"
  on assessments for select
  to authenticated
  using (
    exists (
      select 1 from organizations o
      where o.id = assessments.organization_id
        and o.user_id = auth.uid()
    )
  );

create policy "assessments_insert_own"
  on assessments for insert
  to authenticated
  with check (
    exists (
      select 1 from organizations o
      where o.id = assessments.organization_id
        and o.user_id = auth.uid()
    )
  );

create policy "assessments_update_own"
  on assessments for update
  to authenticated
  using (
    exists (
      select 1 from organizations o
      where o.id = assessments.organization_id
        and o.user_id = auth.uid()
    )
  )
  with check (
    exists (
      select 1 from organizations o
      where o.id = assessments.organization_id
        and o.user_id = auth.uid()
    )
  );

create policy "assessments_delete_own"
  on assessments for delete
  to authenticated
  using (
    exists (
      select 1 from organizations o
      where o.id = assessments.organization_id
        and o.user_id = auth.uid()
    )
  );

-- responses (scoped through assessment -> organization) ----------------------

create policy "responses_select_own"
  on responses for select
  to authenticated
  using (
    exists (
      select 1
      from assessments a
      join organizations o on o.id = a.organization_id
      where a.id = responses.assessment_id
        and o.user_id = auth.uid()
    )
  );

create policy "responses_insert_own"
  on responses for insert
  to authenticated
  with check (
    exists (
      select 1
      from assessments a
      join organizations o on o.id = a.organization_id
      where a.id = responses.assessment_id
        and o.user_id = auth.uid()
    )
  );

create policy "responses_update_own"
  on responses for update
  to authenticated
  using (
    exists (
      select 1
      from assessments a
      join organizations o on o.id = a.organization_id
      where a.id = responses.assessment_id
        and o.user_id = auth.uid()
    )
  )
  with check (
    exists (
      select 1
      from assessments a
      join organizations o on o.id = a.organization_id
      where a.id = responses.assessment_id
        and o.user_id = auth.uid()
    )
  );

create policy "responses_delete_own"
  on responses for delete
  to authenticated
  using (
    exists (
      select 1
      from assessments a
      join organizations o on o.id = a.organization_id
      where a.id = responses.assessment_id
        and o.user_id = auth.uid()
    )
  );

-- reports (read-only for owners; written only by service_role in /api/analyze)

create policy "reports_select_own"
  on reports for select
  to authenticated
  using (
    exists (
      select 1
      from assessments a
      join organizations o on o.id = a.organization_id
      where a.id = reports.assessment_id
        and o.user_id = auth.uid()
    )
  );

create policy "reports_delete_own"
  on reports for delete
  to authenticated
  using (
    exists (
      select 1
      from assessments a
      join organizations o on o.id = a.organization_id
      where a.id = reports.assessment_id
        and o.user_id = auth.uid()
    )
  );

-- controls / framework_applicability: RLS enabled, no policies (deny all for
-- anon + authenticated). Read server-side via service_role only.

-- ---------------------------------------------------------------------------
-- 5. Least-privilege grants (dedicated instance, but locked down from day one)
-- ---------------------------------------------------------------------------

revoke truncate on all tables in schema public from anon, authenticated;
revoke insert, update, delete on all tables in schema public from anon;

-- Make the same restrictions apply to tables created in future migrations.
alter default privileges in schema public
  revoke truncate on tables from anon, authenticated;
alter default privileges in schema public
  revoke insert, update, delete on tables from anon;
