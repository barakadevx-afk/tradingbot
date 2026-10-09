# BARAKA deployment: Vercel, Render, and Supabase

This repository can be deployed as three services:

- **Frontend:** Vercel, rooted at `frontend`
- **API:** Vercel (serverless Python) or Render, configured by the root `render.yaml`
- **Database:** Supabase PostgreSQL

Deployment configuration does not create cloud projects or transfer local database contents. Create each service in its provider dashboard and keep all passwords, connection strings, and generated secrets private.

GitHub Actions validates the frontend build and backend Python syntax. Connect the repository to Vercel and Render to enable their Git-based deployments; the workflow does not publish to GitHub Pages or deploy a Supabase Edge Function.

## 1. Create the Supabase database

1. Create a Supabase project and wait for provisioning to finish.
2. In **Connect**, choose the **Session pooler** connection string. It is appropriate when the backend host needs IPv4 connectivity. Require SSL.
3. Keep the database empty for the first deployment. The backend creates SQLAlchemy tables on startup. Disable automatic exposure of new tables; keep automatic RLS enabled.

**Do not run `supabase/migrations/001_initial_schema.sql` against this backend.** That legacy SQL file defines UUID identifiers and a schema that does not match the current SQLAlchemy models, which use integer identifiers. Using it would make registration and other database operations fail.

## 2. Deploy the API on Vercel (no-cost option)

1. Import the same GitHub repository as a **new Vercel project**. Set **Root Directory** to `backend`; its `vercel.json` serves the FastAPI app.
2. Set the following private environment variables for Production:
   - `DATABASE_URL`: Supabase Session pooler URI from step 1.
   - `SECRET_KEY` and `JWT_SECRET_KEY`: two different random values, each at least 32 characters.
   - `ADMIN_EMAIL` and `ADMIN_PASSWORD`: a unique administrator address and a new strong password of at least 12 characters. Keep these values private.
   - `CORS_ORIGINS`: a JSON array with the exact frontend origin, for example `["https://tradingbot-utyx.vercel.app"]`.
3. Deploy and wait for the deployment to complete. Check `https://<api-project>.vercel.app/` for a JSON response with `"status": "running"`.
4. In the existing frontend Vercel project, set `VITE_API_URL=https://<api-project>.vercel.app/api/v1` for Production and redeploy the frontend.
5. Submit a test registration, sign out, and sign back in. The API creates SQLAlchemy tables on startup; use a clean database and do not apply the incompatible legacy migration.

Vercel functions do not provide a persistent process for the market simulation or WebSockets. The API therefore disables its background simulation there; authentication and ordinary HTTP API routes use the configured database. Use Render below if continuous workers or WebSockets are required.

## 3. Deploy the API on Render

1. Create a Render **Blueprint** from this repository and apply the root `render.yaml`.
2. Set `DATABASE_URL` to the Supabase Session pooler URI from step 1. Do not commit or paste the URI into source files.
3. Set `CORS_ORIGINS` to a JSON array containing the exact Vercel origin, for example `["https://your-project.vercel.app"]`. Add your production custom domain as another array entry if applicable.
4. Set `ADMIN_EMAIL` and `ADMIN_PASSWORD` in Render's private environment settings. Use a unique administrator address and a strong password of at least 12 characters. The backend provisions or synchronizes this account at startup; changing the configured password rotates the account password on the next deploy. Never use these values in Vercel or commit them to Git.
5. Deploy and wait for the `/` health check to pass. Render generates `SECRET_KEY` and `JWT_SECRET_KEY` for the service.
6. Copy the API service URL, such as `https://baraka-api.onrender.com`.

The `DATABASE_URL` environment value should be a PostgreSQL URI such as `postgresql://...`; the backend converts PostgreSQL URI schemes to the installed psycopg 3 SQLAlchemy driver and uses SSL parameters supplied by Supabase.

## 4. Deploy the frontend on Vercel

1. Import the repository into Vercel.
2. Set **Root Directory** to `frontend`; use the Vite preset, `npm run build`, and `dist`.
3. Add the build-time environment variable:

   ```text
   VITE_API_URL=https://<api-project>.vercel.app/api/v1
   ```

   Replace the host with the URL of the API deployment from step 2 or 3. Do not add a trailing slash.
4. Deploy. Vercel serves the SPA routes; the frontend sends API calls directly to Render.

The same `VITE_API_URL` must be set for **Preview** deployments if they should use an API. Add each preview origin to Render's `CORS_ORIGINS`, or keep previews disconnected from production data.

## 5. Verify the deployment

- Open the API service URL and check for a JSON response with `"status": "running"`.
- In the Vercel deployment, create a test account, then sign out and sign back in.
- Confirm the API accepts the Vercel origin and the user appears in the Supabase database.
- Confirm the Vercel build contains the correct API URL and no secrets.

## Production notes

- The Supabase SQL migration is not compatible with the current backend ORM schema; use a clean database until a matching migration is provided.
- Supabase's free database has limited storage and may pause after a period of inactivity. Expect the first request after a pause to take longer.
- Keep live exchange keys out of Vercel frontend variables. Only provide server-side secrets to the API, and keep paper trading enabled until live execution has been separately reviewed.
- The initial administrator must be configured through the API host's private `ADMIN_EMAIL` and `ADMIN_PASSWORD` settings before the API starts in production. Administrator sign-in uses the normal API login and server-side role authorization; no admin credential belongs in frontend environment variables.

## Runtime notes

- Set `CORS_ORIGINS` to JSON syntax; comma-separated values are not parsed as a list by the current settings model.
- `VITE_API_URL` is embedded into the frontend at build time. Changing it in Vercel requires a new deployment.
- The free Render web service may sleep when idle, so the first request after inactivity can be slow.
- The API can run as a Vercel Python function for HTTP requests, but serverless instances cannot provide persistent market-data workers or WebSocket support.
- Back up the Supabase database and use Supabase's connection string and SSL settings from its dashboard.
