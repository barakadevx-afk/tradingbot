# BARAKA AI - Supabase Deployment Guide

This guide explains how to deploy BARAKA AI to Supabase.

## Prerequisites

1. [Supabase Account](https://supabase.com) - Free tier available
2. [Supabase CLI](https://supabase.com/docs/guides/cli) - Install with: `npm install -g supabase`
3. [Vercel](https://vercel.com) or [Netlify](https://netlify.com) - For frontend hosting

## Step 1: Create Supabase Project

1. Go to https://supabase.com and sign in
2. Click "New Project"
3. Enter project name: `baraka-ai`
4. Set database password (save this!)
5. Select region closest to you
6. Click "Create new project" (takes ~2 minutes)

## Step 2: Run Database Migration

1. In Supabase dashboard, go to **SQL Editor**
2. Click "New Query"
3. Copy contents of `supabase/migrations/001_initial_schema.sql`
4. Paste and click "Run"
5. Verify tables created in **Table Editor**

## Step 3: Configure Environment Variables

1. Go to **Settings > Edge Functions**
2. Add secrets:
   ```
   SUPABASE_URL=https://your-project-id.supabase.co
   SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
   SUPABASE_ANON_KEY=your-anon-key
   ```
3. Get keys from **Settings > API**

## Step 4: Deploy Edge Function

```bash
# Login to Supabase
supabase login

# Link to your project
supabase link --project-ref your-project-id

# Deploy the Edge Function
supabase functions deploy baraka-api
```

## Step 5: Deploy Frontend

### Option A: Vercel (Recommended)

```bash
cd frontend
npm install -g vercel
vercel --prod
```

### Option B: Netlify

```bash
cd frontend
npm install -g netlify-cli
netlify deploy --prod
```

## Step 6: Update Frontend API URL

Update `frontend/vite.config.ts` proxy target to your Supabase Edge Function URL:

```typescript
proxy: {
  '/api': {
    target: 'https://your-project-id.supabase.co/functions/v1/baraka-api',
    changeOrigin: true,
    rewrite: (path) => path.replace(/^\/api/, ''),
  },
}
```

## Step 7: Verify Deployment

1. Visit your frontend URL
2. Check browser console for API connection
3. Verify Supabase Edge Function: `https://your-project-id.supabase.co/functions/v1/baraka-api/health`

## Architecture

```
Frontend (Vercel/Netlify)
    ↓
Supabase Edge Functions (API)
    ↓
Supabase PostgreSQL (Database)
    ↓
Supabase Auth (Authentication)
    ↓
Supabase Storage (File Storage)
```

## Environment Variables

| Variable | Description | Location |
|----------|-------------|----------|
| SUPABASE_URL | Project URL | Settings > API |
| SUPABASE_ANON_KEY | Public anon key | Settings > API |
| SUPABASE_SERVICE_ROLE_KEY | Service role key | Settings > API |
| SUPABASE_DB_URL | Database connection | Settings > Database |
| JWT_SECRET | JWT signing secret | Edge Functions |

## Monitoring

- Supabase Dashboard: Database health, API logs, function logs
- Vercel/Netlify: Frontend analytics, deployment status
- UptimeRobot: External monitoring (optional)

## Cost Estimation

| Service | Free Tier | Estimated Monthly |
|---------|-----------|-------------------|
| Supabase | 500MB DB, 1GB storage | $0 |
| Vercel | 100GB bandwidth | $0 |
| Netlify | 100GB bandwidth | $0 |
| **Total** | | **$0** |

## Support

- [Supabase Docs](https://supabase.com/docs)
- [BARAKA AI README](../README.md)
- [GitHub Issues](https://github.com/barakadevx-afk/tradingbot/issues)
