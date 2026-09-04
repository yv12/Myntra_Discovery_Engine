# 🚀 Deploying Myntra Discovery Engine to Railway

This guide walks you through deploying the **Myntra Discovery Engine** and its interactive analytics dashboard on [Railway](https://railway.app).

---

## 🌟 Overview

The repository is equipped with:
- **FastAPI + Uvicorn Web Server (`server.py`)**: Hosts the interactive dashboard at `/` and exposes API endpoints for BM25 RAG queries and metrics.
- **Dockerized Runtime (`Dockerfile`)**: Containerized Python 3.11-slim setup.
- **Railway Configuration (`railway.json`)**: Configured with automated healthchecks at `/health` and zero-downtime deployment.

---

## 🛠️ Method 1: Deploy via Railway Dashboard (Recommended)

### Step 1: Push Code to GitHub
Ensure all latest files are pushed to your GitHub repository:
```bash
git add .
git commit -m "feat: add Railway deployment config, Dockerfile, and FastAPI server"
git push origin main
```

### Step 2: Create a New Project on Railway
1. Go to [railway.app](https://railway.app) and log in.
2. Click **"+ New Project"**.
3. Select **"Deploy from GitHub repo"**.
4. Choose your repository: `yv12/Myntra_Discovery_Engine` (or your repository fork).

### Step 3: Configure Environment Variables
In your Railway Service dashboard:
1. Navigate to the **"Variables"** tab.
2. Add the following variables:
   - `PORT`: `8000` *(Railway automatically maps its router to this port)*
   - `GROQ_API_KEY`: *(Optional - paste your Groq key if you plan to run live taxonomy classification pipelines in container)*
   - `PYTHONUNBUFFERED`: `1`

### Step 4: Generate a Public Domain
1. In your service settings, navigate to the **"Settings"** tab.
2. Scroll to the **"Networking"** section.
3. Click **"Generate Domain"** (e.g., `myntra-discovery-production.up.railway.app`) or attach a custom domain.

### Step 5: Verify Deployment
Once the build completes (green checkmark), open the generated domain in your browser:
- **Dashboard UI**: `https://<your-service>.up.railway.app/`
- **Healthcheck**: `https://<your-service>.up.railway.app/health`
- **Interactive API Docs**: `https://<your-service>.up.railway.app/docs`
- **RAG Search Endpoint**: `https://<your-service>.up.railway.app/api/rag/search?q=fabric`

---

## 💻 Method 2: Deploy via Railway CLI

If you prefer deploying directly from your terminal:

### 1. Install Railway CLI
```bash
# Windows (npm)
npm install -g @railway/cli

# macOS / Linux (Homebrew or curl)
# brew install railway
# or: curl -fsSL https://railway.app/install.sh | sh
```

### 2. Login & Link Project
```bash
# Authenticate
railway login

# Initialize project
railway init
```

### 3. Deploy
```bash
# Upload and deploy current repository
railway up

# Open dashboard in browser
railway open
```

---

## 🔍 Healthcheck & Monitoring

Railway monitors the service using the configured healthcheck endpoint:
```http
GET /health
```
**Sample response**:
```json
{
  "status": "healthy",
  "service": "myntra-discovery-engine",
  "version": "1.0.0",
  "records_loaded": 384,
  "environment": "production"
}
```

---

## ⚡ Useful API Endpoints

Once deployed, the service provides the following live endpoints:

| Endpoint | Method | Description |
|---|---|---|
| `/` | `GET` | Interactive HTML/JS Research Dashboard |
| `/health` | `GET` | Railway healthcheck & record count |
| `/api/metrics` | `GET` | Aggregated funnel, counts & opportunity score JSON |
| `/api/rag/presets` | `GET` | 10 executive PM grounded Q&A syntheses |
| `/api/rag/query` | `POST` | Custom BM25 query with JSON payload `{"query": "...", "top_k": 6}` |
| `/api/rag/search` | `GET` | Quick GET search endpoint: `/api/rag/search?q=sizing` |
| `/docs` | `GET` | Interactive Swagger API documentation |
