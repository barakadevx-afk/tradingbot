# BARAKA AI - Vercel Full Stack Deployment

## Deploy Full Stack to Vercel

### Prerequisites
- [Vercel Account](https://vercel.com) (Free tier available)
- [GitHub Account](https://github.com) with the repository

### Step 1: Import Repository to Vercel

1. Go to https://vercel.com
2. Click **"Add New"** → **"Project"**
3. Select **GitHub** as Git provider
4. Find and import `barakadevx-afk/tradingbot`

### Step 2: Configure Build Settings

| Setting | Value |
|---------|-------|
| Framework Preset | Vite |
| Root Directory | `frontend` |
| Build Command | `npm run build` |
| Output Directory | `dist` |
| Install Command | `npm install` |

### Step 3: Add Environment Variables

| Variable | Value | Description |
|----------|-------|-------------|
| `VITE_API_URL` | `/api/v1` | API base URL |
| `SECRET_KEY` | `baraka-ai-secret-key-change-in-production-32chars` | App secret |
| `JWT_SECRET_KEY` | `baraka-ai-jwt-secret-key-change-in-production` | JWT secret |
| `DATABASE_URL` | `sqlite:///./baraka.db` | Database URL |
| `DEBUG` | `false` | Debug mode |
| `ENVIRONMENT` | `production` | Environment |

### Step 4: Deploy

Click **"Deploy"** and wait for build to complete.

### Step 5: Access Your App

After deployment, Vercel provides a public URL:
- **https://tradingbot.vercel.app** (or similar)

## Architecture

```
Vercel Frontend (React + Vite)
    ↓
Vercel Serverless Functions (FastAPI)
    ↓
SQLite Database (or Supabase PostgreSQL)
```

## Environment Variables

### Required for Production

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | Application secret key (min 32 chars) |
| `JWT_SECRET_KEY` | JWT signing secret (min 32 chars) |
| `DATABASE_URL` | Database connection string |
| `VITE_API_URL` | Frontend API base URL |

### Optional

| Variable | Default | Description |
|----------|---------|-------------|
| `DEBUG` | `false` | Enable debug mode |
| `ENVIRONMENT` | `production` | Environment name |
| `REDIS_URL` | - | Redis connection URL |
| `LOG_LEVEL` | `INFO` | Logging level |

## Verification

After deployment, verify:
- [ ] Frontend loads at Vercel URL
- [ ] Registration page works
- [ ] Login works
- [ ] Dashboard loads
- [ ] API health check returns 200
- [ ] Paper trading is active

## Troubleshooting

### Build fails
- Check Node.js version (requires 20+)
- Verify `package.json` scripts
- Check build logs in Vercel dashboard

### API not working
- Verify environment variables
- Check Vercel function logs
- Ensure `VITE_API_URL` is set correctly

### Database errors
- SQLite is file-based, may not persist in serverless
- Consider using Supabase PostgreSQL for production
- Run migrations manually if needed

## Production Recommendations

1. **Use Supabase PostgreSQL** instead of SQLite for production
2. **Enable HTTPS** (automatic with Vercel)
3. **Set up monitoring** (Vercel Analytics, Sentry)
4. **Configure CORS** properly
5. **Use strong secrets** for SECRET_KEY and JWT_SECRET_KEY
6. **Enable rate limiting**
7. **Set up backup strategy**

## Cost

| Service | Free Tier | Monthly |
|---------|-----------|---------|
| Vercel | 100GB bandwidth | $0 |
| Total | | **$0** |

## Support

- [Vercel Docs](https://vercel.com/docs)
- [BARAKA AI README](README.md)
- [GitHub Issues](https://github.com/barakadevx-afk/tradingbot/issues)
