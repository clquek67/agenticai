# AI Compliance Navigator

Guided assessments of enterprise AI systems against major compliance
frameworks — NIST AI RMF, ISO/IEC 42001, OWASP LLM Top-10, EU AI Act
(high-risk obligations, effective Aug 2, 2026) — plus regional and sector
modules. Produces per-framework compliance scores, prioritized gaps, and
client-ready reports with AI-generated remediation guidance.

## Tech stack

- Next.js 14 (App Router, TypeScript, `src/` directory)
- Tailwind CSS
- **Self-hosted Supabase — dedicated instance** (Postgres + Auth) on a VPS,
  second Docker Compose stack with its own `auth.users`, JWT secret, and
  Kong gateway port/subdomain
- Anthropic Claude API (`claude-sonnet-4-6`) for gap analysis (Phase 4)
- Deploy: Vercel (auto-deploy from `main`, previews from branches)

## Environment variables

Copy `.env.example` to `.env.local` and fill in values from the **dedicated**
Supabase instance:

| Variable | Where used | Notes |
| --- | --- | --- |
| `NEXT_PUBLIC_SUPABASE_URL` | client + server | Kong gateway URL of the dedicated instance |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | client + server | anon key signed with this instance's JWT secret |
| `SUPABASE_SERVICE_ROLE_KEY` | server only | bypasses RLS; never exposed to the client |
| `ANTHROPIC_API_KEY` | server only | Claude API for gap analysis (Phase 4) |

`.env*` is gitignored (only `.env.example` is committed). Never hardcode
secrets.

Any direct Postgres connections from Vercel serverless functions must go
through the Supabase connection pooler in **transaction mode (port 6543)**,
not the direct Postgres port. (The app currently talks to Postgres only via
the Supabase HTTP API, so this applies to future direct-SQL usage.)

## Database setup (Phase 1)

Run `supabase/migrations/0001_init.sql` once in the SQL editor of the
dedicated instance's Supabase Studio. It creates:

- **Enums**: 21 industries, 5 regions, 14 frameworks/modules (4 core + 10
  regional/sector modules used by the scope selector), assessment status,
  answer values, applicability types.
- **Tables**: `organizations`, `assessments`, `responses`, `controls`,
  `reports`, `framework_applicability`.
- **RLS on every table.** User-data tables are owner-scoped through
  `organizations.user_id` (`auth.uid() = user_id` or membership lookups —
  no `true` policies). `controls` and `framework_applicability` are global
  reference tables: RLS enabled with **no** policies (deny-by-default), read
  server-side via the service-role client only. `reports` is insert-only via
  `service_role` (the analyze API route); owners can read/delete.
- **Least-privilege grants**: `TRUNCATE` revoked from `anon` and
  `authenticated`; all writes revoked from `anon`; matching
  `ALTER DEFAULT PRIVILEGES` so future tables inherit the same posture.

Note: the migration uses `UNIQUE NULLS NOT DISTINCT` on
`framework_applicability`, which requires Postgres 15+ (current self-hosted
Supabase images ship 15+).

Seed data for `controls` and `framework_applicability` ships in Phase 2
(`supabase/seed.sql`).

## Supabase clients (`src/lib/supabase/`)

- `client.ts` — browser client (anon key, RLS enforced)
- `server.ts` — server components / route handlers (anon key + session
  cookies via `@supabase/ssr`, RLS enforced)
- `admin.ts` — service-role client, guarded by `server-only`; used for
  reference-data reads and server-owned writes

## Development

```bash
npm install
npm run dev   # http://localhost:3000
```

### Corporate proxy note (Windows + WSL2)

If `npm install` fails with self-signed-certificate errors behind an
SSL-inspection proxy, do **not** disable TLS globally. Point npm at the
corporate CA bundle instead:

```bash
npm config set cafile /path/to/corporate-ca-bundle.pem
```

## Roadmap

- [x] Phase 1 — scaffold + database schema/RLS
- [ ] Phase 2 — control library seed data
- [ ] Phase 3 — assessment flow (scope selector, runner, completion screen)
- [ ] Phase 4 — AI gap analysis via Claude API
- [ ] Phase 5 — landing page, auth middleware, deploy checklist
