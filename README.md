# Insider Threat Detection System

A full-stack application for reviewing employee behavior anomalies, risk levels,
and blocked accounts. It uses FastAPI, React, MySQL/TiDB, and an Isolation
Forest model.

## Features

- Anomaly detection and LOW / MEDIUM / HIGH risk classification
- Temporal and peer behavior analysis
- Responsive administrator dashboard
- Block and unblock employee accounts
- Assign an employee to an analyst by email through the Brevo HTTPS API
- JWT authentication and role-protected API routes

## Project structure

```text
backend/       FastAPI API, data pipeline, and model artifacts
frontend/      React and Vite application
requirements.txt
render.yaml    Render backend blueprint
netlify.toml   Netlify frontend configuration
```

## Local setup

The project targets Python 3.13. From the repository root:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Copy `.env.example` to `.env` and replace every placeholder:

```dotenv
ENVIRONMENT=development
DB_URL=mysql+pymysql://USERNAME:PASSWORD@HOST:3306/DATABASE_NAME
SECRET_KEY=replace-with-a-random-secret-of-at-least-32-characters
CORS_ORIGINS=http://localhost:5173
SEED_ADMIN_USERNAME=admin
SEED_ADMIN_PASSWORD=replace-with-a-strong-unique-password
ADMIN_EMAIL=verified-sender@example.com
BREVO_API_KEY=replace-with-your-real-brevo-api-key
ANALYST_EMAIL=analyst@example.com
```

Generate a suitable secret : 

Never commit `.env`, API keys, passwords, or database exports.

### Database and administrator

Create the database locally, then import your private SQL export if you have
one. Database dumps are intentionally ignored by Git and are not distributed
with this repository.

```sql
CREATE DATABASE insider_threat_database;
```

From the repository root, create or update the administrator:

```powershell
Set-Location backend
python -m scripts.seed_users
Set-Location ..
```

The seed command does not print the password. Remove
`SEED_ADMIN_PASSWORD` from a hosted environment after the account is seeded.

### Start the backend

```powershell
Set-Location backend
uvicorn app:app --reload
```

The API is available at `http://localhost:8000`.

### Start the frontend

In another terminal:

```powershell
Set-Location frontend
npm install
npm run dev
```

The frontend is available at `http://localhost:5173`.

## Optional data pipeline

If you need to rebuild data instead of importing a database export, run the
relevant modules from the `backend` directory:

```powershell
python -m scripts.merge_data
python -m scripts.clean_data
python -m feature_engineering.temporal_features
python -m feature_engineering.peer_features
python -m feature_engineering.base_features
python -m model.predict_anomaly
```

Review the scripts and input paths before running them. They modify database or
generated-data state.

## Email notifications

The backend sends assignment notifications with Brevo's HTTPS API. `ADMIN_EMAIL`
must be a sender verified in Brevo, `ANALYST_EMAIL` is the recipient, and
`BREVO_API_KEY` must contain the real API key. The API key belongs only in the
local `.env` file and Render environment settings.

The assign endpoint returns success only after Brevo accepts the message.
Delivery failures return an error to the dashboard and are recorded in backend
logs without exposing addresses, message content, or the key.

## Free hosting

### Backend on Render

1. Push the repository to GitHub.
2. In Render, create a Blueprint from the repository. `render.yaml` configures
   the backend service.
3. Set `DB_URL`, `CORS_ORIGINS`, `ADMIN_EMAIL`, `BREVO_API_KEY`, and
   `ANALYST_EMAIL` in Render.
4. Set `CORS_ORIGINS` to the exact Netlify URL and custom-domain URL, separated
   as supported by the application configuration.
5. Deploy, seed the administrator once, and verify `/healthz`.

### Frontend on Netlify

1. Import the GitHub repository into Netlify.
2. The checked-in `netlify.toml` supplies the build directory and SPA redirect.
3. Set `VITE_API_URL` to the Render HTTPS service URL before building.
4. Deploy and connect the custom domain in Netlify DNS/domain settings.
5. Add the final custom-domain origin to Render's `CORS_ORIGINS`.

### Database on TiDB Cloud

Create a TiDB Cloud cluster and database, import the private schema/data, and
create a least-privilege application user. Put the TLS-enabled SQLAlchemy
connection string in Render as `DB_URL`; do not add it to the repository.

Free service limits and inactivity behavior can change, so check each provider's
current limits before production use.

## Production checklist

- Replace all example values with strong, unique secrets.
- Use only HTTPS origins and database TLS.
- Keep the Brevo sender verified and test an analyst notification.
- Restrict database privileges and retain protected backups.
- Review [SECURITY.md](SECURITY.md) before using real employee data.
- Run frontend lint/build and backend tests before every release.
