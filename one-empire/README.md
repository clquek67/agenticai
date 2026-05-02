# One Empire — Setup & Deployment Reference

Content automation platform for solo founders, coaches, and consultants.  
Built by Shine Quek. Infrastructure: Hostinger VPS · n8n · Supabase · Netlify.

---

## Deliverables in This Folder

```
one-empire/
├── netlify/
│   ├── privacy.html            → deploy to one-empire.com/privacy
│   ├── terms.html              → deploy to one-empire.com/terms
│   ├── instagram-callback.html → brief.one-empire.com/instagram/callback
│   ├── youtube-callback.html   → brief.one-empire.com/youtube/callback
│   ├── tiktok-callback.html    → brief.one-empire.com/tiktok/callback
│   └── _redirects              → updated Netlify redirect rules
├── n8n/
│   ├── instagram-oauth.json    → import into n8n
│   ├── youtube-oauth.json      → import into n8n
│   ├── tiktok-oauth.json       → import into n8n
│   └── token-refresh.json      → import into n8n (runs daily at 06:00)
└── supabase/
    └── migrations.sql          → run in Supabase SQL editor
```

---

## Priority 1 — Meta App Review (unblocks Facebook + Instagram)

### Step 1: Deploy Privacy & Terms pages to one-empire.com

Upload `privacy.html` and `terms.html` to the root of one-empire.com so they are live at:
- https://one-empire.com/privacy
- https://one-empire.com/terms

If one-empire.com is on Netlify, add to its `_redirects`:
```
/privacy  /privacy.html  200
/terms    /terms.html    200
```

### Step 2: Submit Meta App Review

Go to https://developers.facebook.com/apps/1278647270579382/app-review/

Permissions to request:
- `instagram_content_publish`
- `pages_manage_posts`
- `pages_read_engagement`
- `pages_show_list`

In the review form, set:
- **Privacy Policy URL:** https://one-empire.com/privacy
- **Terms of Service URL:** https://one-empire.com/terms
- **App description:** Content automation platform that auto-publishes AI-generated social media content for solo founders on behalf of authenticated users.

---

## Priority 2 — Supabase: Create New Token Tables

Run `supabase/migrations.sql` in the Supabase SQL editor:
- https://gsqcsyepztcmrvzxevhw.supabase.co → SQL Editor

Creates: `instagram_tokens`, `youtube_tokens`, `tiktok_tokens`

---

## Priority 3 — YouTube OAuth Setup

### Google Cloud Console setup
1. Go to https://console.cloud.google.com
2. Create a new project (or use existing) named "One Empire"
3. Enable **YouTube Data API v3**
4. Create OAuth 2.0 credentials (Web application type)
5. Add authorised redirect URI: `https://brief.one-empire.com/youtube/callback`
6. Copy Client ID → `YOUTUBE_CLIENT_ID`
7. Copy Client Secret → `YOUTUBE_CLIENT_SECRET`

### Add env vars to docker-compose.yml
```yaml
YOUTUBE_CLIENT_ID: your_client_id_here
YOUTUBE_CLIENT_SECRET: your_client_secret_here
```

### Import n8n workflow
Import `n8n/youtube-oauth.json` → activates webhook at `/webhook/one-empire-youtube-oauth`

### Deploy callback page
Add `youtube-callback.html` to brief.one-empire.com Netlify site.

### Build the OAuth link (add to member portal index.html)
```
https://accounts.google.com/o/oauth2/v2/auth
  ?client_id=YOUTUBE_CLIENT_ID
  &redirect_uri=https://brief.one-empire.com/youtube/callback
  &response_type=code
  &scope=https://www.googleapis.com/auth/youtube.upload https://www.googleapis.com/auth/youtube.readonly
  &access_type=offline
  &prompt=consent
  &state=MEMBER_EMAIL_URL_ENCODED
```

---

## Priority 4 — TikTok OAuth Setup

### TikTok Developer portal setup
1. Go to https://developers.tiktok.com
2. Create app → "One Empire"
3. Add product: **Login Kit** + **Content Posting API**
4. Add redirect URI: `https://brief.one-empire.com/tiktok/callback`
5. Copy Client Key → `TIKTOK_CLIENT_KEY`
6. Copy Client Secret → `TIKTOK_CLIENT_SECRET`

### Add env vars to docker-compose.yml
```yaml
TIKTOK_CLIENT_KEY: your_client_key_here
TIKTOK_CLIENT_SECRET: your_client_secret_here
```

### Import n8n workflow
Import `n8n/tiktok-oauth.json` → activates webhook at `/webhook/one-empire-tiktok-oauth`

### Build the OAuth link
```
https://www.tiktok.com/v2/auth/authorize/
  ?client_key=TIKTOK_CLIENT_KEY
  &redirect_uri=https://brief.one-empire.com/tiktok/callback
  &response_type=code
  &scope=user.info.basic,video.publish
  &state=MEMBER_EMAIL_URL_ENCODED
```

---

## Priority 5 — Instagram OAuth Setup (post Meta App Review)

The Instagram app is already created (ID: 1278647270579382).  
After Meta App Review approves `instagram_content_publish`:

### Import n8n workflow
Import `n8n/instagram-oauth.json` → activates webhook at `/webhook/one-empire-instagram-oauth`

### Build the OAuth link
```
https://www.facebook.com/v18.0/dialog/oauth
  ?client_id=1278647270579382
  &redirect_uri=https://brief.one-empire.com/instagram/callback
  &scope=instagram_content_publish,instagram_manage_comments,pages_show_list,pages_read_engagement
  &response_type=code
  &state=MEMBER_EMAIL_URL_ENCODED
```

---

## Priority 6 — Token Refresh (daily automation)

Import `n8n/token-refresh.json`. Runs daily at 06:00 UTC.

**Platform refresh behaviour:**
| Platform  | Method | TTL |
|-----------|--------|-----|
| LinkedIn  | Cannot auto-refresh — member must re-auth | 60 days |
| Facebook  | `fb_exchange_token` grant | 60 days |
| Instagram | `fb_exchange_token` grant | 60 days |
| YouTube   | `refresh_token` grant | 1 hour (access) / permanent (refresh) |
| TikTok    | `refresh_token` grant | 24 hours (access) / 1 year (refresh) |

LinkedIn tokens cannot be refreshed programmatically. The workflow flags them as `needs_reauth` — add a Gmail node to email members 7 days before expiry.

---

## Critical n8n Rules

- **NEVER** use `this.getCredentials()` — blocked by task runner
- **ALWAYS** use `$env.VARIABLE_NAME` for secrets
- `N8N_BLOCK_ENV_ACCESS_IN_NODE=false` — already set in docker-compose.yml
- `N8N_RUNNERS_ENABLED=false` — already set

## Supabase URL
```
https://gsqcsyepztcmrvzxevhw.supabase.co
```

## Webhook base URL
```
https://n8n.one-empire.com/webhook/
```
