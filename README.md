# MEETING ACCESS

> **Know if you can participate before the meeting begins.**

Civic accessibility intelligence system for California public meeting agendas. Analyzes meeting agendas (PDF format) against Ralph M. Brown Act and ADA Title II participation indicators with deterministic evidence verification and deadline calculation.

## Architecture

- **Frontend:** React 19 + TypeScript + Vite
- **Backend:** Python 3.11 + FastAPI + Pydantic v2
- **AI / SDK:** Google Gen AI Python SDK (`google-genai`) with configurable model (`gemini-3.8-flash`)
- **PDF Extraction:** `pdfplumber` + `pypdf`
- **Testing:** `pytest` + `httpx`

## Project Structure

```text
├── .gitignore
├── README.md
├── backend/
│   ├── .env.example
│   ├── requirements.txt
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── main.py
│   └── tests/
│       ├── __init__.py
│       └── test_health.py
└── frontend/
    ├── package.json
    ├── vite.config.ts
    ├── index.html
    └── src/
        ├── App.tsx
        ├── main.tsx
        └── ...
```

## Quick Start

### Backend Setup
```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```
Health Check: `http://localhost:8000/api/health`

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Application: `http://localhost:5173`
