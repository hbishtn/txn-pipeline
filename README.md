# AI-Powered Transaction Processing Pipeline

## Tech Stack
- Django REST Framework
- PostgreSQL
- Celery + Redis
- Gemini AI (LLM)
- Docker Compose

## Setup & Run

### Prerequisites
- Docker Desktop installed

### Start the project
```bash
git clone https://github.com/hbishtn/ai-transaction-pipeline
cd ai-transaction-pipeline
docker compose up --build
```

API will be available at: `http://localhost:8000`

## API Endpoints

### Upload CSV
```bash
curl -X POST http://localhost:8000/jobs/upload \
  -F "file=@transactions.csv"
```

### Check Job Status
```bash
curl http://localhost:8000/jobs/1/status
```

### Get Results
```bash
curl http://localhost:8000/jobs/1/results
```

### List All Jobs
```bash
curl http://localhost:8000/jobs/
```

## Pipeline Steps
1. **Data Cleaning** — dates normalize, $ remove, duplicates hatao
2. **Anomaly Detection** — 3x median flag, wrong currency flag
3. **LLM Classification** — Gemini se categories assign
4. **LLM Summary** — narrative + risk level generate

Note: Gemini free tier quota limits may apply