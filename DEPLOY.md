# BARAKA AI - Public Deployment Guide

## Quick Deploy (3 Steps)

### 1. Make GitHub Repository Public

1. Go to https://github.com/barakadevx-afk/tradingbot/settings
2. Scroll down to "Danger Zone"
3. Click "Change visibility" → "Make public"

### 2. Deploy Frontend to GitHub Pages

1. Go to https://github.com/barakadevx-afk/tradingbot/settings/pages
2. Source: "GitHub Actions"
3. The workflow will automatically deploy to: `https://barakadevx-afk.github.io/tradingbot/`

### 3. Deploy Backend to Supabase

1. Create project at https://supabase.com
2. Run migration: `supabase/migrations/001_initial_schema.sql`
3. Deploy Edge Function: `supabase functions deploy baraka-api`
4. Add secrets in Supabase Dashboard → Edge Functions

## Environment Variables

### GitHub Secrets (Settings → Secrets → Actions)

| Secret | Description |
|--------|-------------|
| SUPABASE_EDGE_FUNCTION_URL | Edge Function URL |
| SUPABASE_PROJECT_REF | Supabase project reference |
| SUPABASE_ACCESS_TOKEN | Supabase personal access token |

### Supabase Edge Function Secrets

| Secret | Description |
|--------|-------------|
| SUPABASE_URL | Project URL |
| SUPABASE_SERVICE_ROLE_KEY | Service role key |
| SUPABASE_ANON_KEY | Anon public key |

## Live URLs

| Service | URL |
|---------|-----|
| Frontend | https://barakadevx-afk.github.io/tradingbot/ |
| Backend API | https://your-project.supabase.co/functions/v1/baraka-api |
| GitHub Repo | https://github.com/barakadevx-afk/tradingbot |

## Verification

After deployment, verify:
- [ ] Frontend loads at GitHub Pages URL
- [ ] API health check returns 200
- [ ] User registration works
- [ ] Paper trading is active
