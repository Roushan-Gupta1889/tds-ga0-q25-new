# TDS GA0 Q25 — Vercel POST Analytics Endpoint

## Files
- `api/index.py`: FastAPI app; POST endpoint is `/api/latency`; CORS allows all origins.
- `telemetry_data.py`: the supplied 36 telemetry records bundled as a Python constant.
- `requirements.txt`: FastAPI dependency.
- `vercel.json`: routes traffic to the FastAPI app.

## Deploy
1. Create a new GitHub repository (e.g. `tds-ga0-q25`).
2. Upload the contents of this folder to the repository root. Keep the `api` folder and its `index.py` file structure. Do not upload the ZIP itself.
3. On Vercel, sign in with GitHub, choose Add New → Project, import this repository and deploy.
4. Your endpoint URL is `https://YOUR-DEPLOYMENT.vercel.app/api/latency`. Replace `YOUR-DEPLOYMENT` with the actual hostname Vercel gives you.
5. Submit that real URL in GA0, not the placeholder `https://your-app.vercel.app/api/latency`.

## Test request
POST to `/api/latency` with JSON:
`{"regions":["apac","emea"],"threshold_ms":178}`

Expected metrics (minor floating point representation differences are normal):
- APAC: avg_latency 157.90916666666666, p95_latency 204.2215, avg_uptime 98.456, breaches 3
- EMEA: avg_latency 168.57, p95_latency 229.52, avg_uptime 98.32958333333333, breaches 4
