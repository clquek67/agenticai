-- One Empire — Supabase Migrations
-- Run these in the Supabase SQL editor at:
-- https://gsqcsyepztcmrvzxevhw.supabase.co

-- ============================================================
-- instagram_tokens
-- ============================================================
create table if not exists instagram_tokens (
  id               uuid primary key default gen_random_uuid(),
  member_email     text unique not null,
  instagram_id     text,
  instagram_name   text,
  access_token     text not null,
  expires_in       integer,
  token_stored_at  text,
  token_expires_at text,
  is_active        boolean default true,
  created_at       timestamptz default now(),
  updated_at       timestamptz default now()
);

-- Auto-update updated_at on every row change
create or replace function update_updated_at_column()
returns trigger language plpgsql as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

create trigger instagram_tokens_updated_at
  before update on instagram_tokens
  for each row execute procedure update_updated_at_column();

-- Row-level security (service key bypasses RLS)
alter table instagram_tokens enable row level security;

-- ============================================================
-- youtube_tokens
-- ============================================================
create table if not exists youtube_tokens (
  id               uuid primary key default gen_random_uuid(),
  member_email     text unique not null,
  youtube_id       text,
  youtube_name     text,
  access_token     text not null,
  refresh_token    text,             -- required for auto-refresh
  expires_in       integer,
  token_stored_at  text,
  token_expires_at text,
  is_active        boolean default true,
  created_at       timestamptz default now(),
  updated_at       timestamptz default now()
);

create trigger youtube_tokens_updated_at
  before update on youtube_tokens
  for each row execute procedure update_updated_at_column();

alter table youtube_tokens enable row level security;

-- ============================================================
-- tiktok_tokens
-- ============================================================
create table if not exists tiktok_tokens (
  id                  uuid primary key default gen_random_uuid(),
  member_email        text unique not null,
  tiktok_open_id      text,
  tiktok_name         text,
  access_token        text not null,
  refresh_token       text,          -- required for auto-refresh (valid 1 year)
  expires_in          integer,       -- access token TTL in seconds (default 86400 = 24h)
  refresh_expires_in  integer,       -- refresh token TTL in seconds (default 31536000 = 1yr)
  token_stored_at     text,
  token_expires_at    text,
  refresh_expires_at  text,
  is_active           boolean default true,
  created_at          timestamptz default now(),
  updated_at          timestamptz default now()
);

create trigger tiktok_tokens_updated_at
  before update on tiktok_tokens
  for each row execute procedure update_updated_at_column();

alter table tiktok_tokens enable row level security;

-- ============================================================
-- content_queue — add platform columns for YouTube and TikTok
-- (Run only if content_queue already exists and lacks these values)
-- ============================================================
-- The existing content_queue table stores platform as a text field.
-- Ensure 'youtube' and 'tiktok' are valid values by updating any
-- check constraint if one exists, e.g.:
--
-- alter table content_queue drop constraint if exists content_queue_platform_check;
-- alter table content_queue add constraint content_queue_platform_check
--   check (platform in ('linkedin', 'facebook', 'instagram', 'youtube', 'tiktok'));
--
-- If no check constraint exists, no change is needed.

-- ============================================================
-- Environment variables to add to docker-compose.yml
-- ============================================================
-- Add these under the n8n service environment section:
--
--   YOUTUBE_CLIENT_ID: <from Google Cloud Console>
--   YOUTUBE_CLIENT_SECRET: <from Google Cloud Console>
--   TIKTOK_CLIENT_KEY: <from TikTok Developer portal>
--   TIKTOK_CLIENT_SECRET: <from TikTok Developer portal>
--
-- YouTube Redirect URI to register in Google Cloud Console:
--   https://brief.one-empire.com/youtube/callback
--
-- TikTok Redirect URI to register in TikTok Developer portal:
--   https://brief.one-empire.com/tiktok/callback
