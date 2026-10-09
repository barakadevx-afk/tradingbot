# Vercel deployment

The frontend and FastAPI API can both be deployed on Vercel as separate projects, with Supabase PostgreSQL for the database. Follow the complete [deployment guide](./DEPLOY.md) for setup and verification.

For the frontend project, set the root directory to `frontend`, use `npm run build` with `dist` as the output directory, and set `VITE_API_URL` to the API deployment URL ending in `/api/v1`.

For the API project, set the root directory to `backend`; its existing `vercel.json` deploys the FastAPI app as a Python function. Provide the required private database, JWT, administrator, and CORS environment variables in the Vercel project settings.
