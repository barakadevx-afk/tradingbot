# Vercel frontend deployment

The frontend is hosted on Vercel; the FastAPI backend and PostgreSQL database are separate services. Follow the complete [deployment guide](./DEPLOY.md) for Render, Supabase, required environment variables, and verification steps.

For Vercel, set the project root directory to `frontend`, use `npm run build` with `dist` as the output directory, and set `VITE_API_URL` to the deployed backend URL ending in `/api/v1`.

Do not deploy the current admin interface publicly until the hard-coded admin credentials are removed and rotated. See the production blockers in the deployment guide.
