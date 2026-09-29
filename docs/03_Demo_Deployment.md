# Demo Deployment (Vercel + Render)

This setup is for a demonstration with synthetic data only. Do not enter real patient information.

## Before Connecting Hosts

1. Push the project source to a GitHub repository. This workspace currently has no Git remote configured.
2. Confirm `.env`, `.env.local`, database files, and patient data are not committed. The repository ignores local environment files and SQLite databases.

## Deploy the API on Render

1. In Render, create a new Blueprint and connect the GitHub repository containing this project.
2. Render reads the root `render.yaml` and creates the `mediextract-api` web service.
3. Wait for the `/health` check to pass. Copy the service's public URL, for example `https://mediextract-api.onrender.com`.

The service uses local SQLite when `MONGODB_URL` is not configured. On Render's free service, the filesystem is ephemeral, so demo accounts and records can be lost when the service restarts or redeploys. Add a demo MongoDB connection through the Render service's environment settings if data must persist. Do not use real patient data.

## Deploy the Frontend on Vercel

1. Import the same GitHub repository into Vercel.
2. Set the project root directory to `frontend`.
3. Add the environment variable `VITE_API_URL` with the Render API URL, without a trailing slash, such as `https://mediextract-api.onrender.com`.
4. Deploy. `frontend/vercel.json` handles client-side route fallback.

The backend currently allows cross-origin requests for this demo. Keep the Render API URL public only for demonstration use and do not treat the app as a production clinical system.

## Local Smoke Check

Build the frontend before deployment:

```powershell
Push-Location frontend
npm ci
npm run build
Pop-Location
```

For a basic API health check, open `https://<your-render-service>/health` after Render finishes deploying.