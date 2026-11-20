# MEETING ACCESS

> **Know if you can participate before the meeting begins.**

An evidence-backed civic accessibility intelligence platform for California public meeting agendas. Built for **Bridge The Gap Hacks 2026** (Accessibility, Civic Technology & Public Participation).

---

## 🎯 Key Capabilities

- **Evidence-Backed Participation Intelligence:** Structures disability accommodation notices, assistive listening devices, live CART captioning, ASL interpretation, alternative formats, remote participation, and public-comment instructions across 9 discrete categories.
- **Deterministic Python Verification:** Eliminates LLM hallucinations. Every single finding must cite an exact physical PDF page (1 to N) and match page text verbatim. If evidence cannot be verified, it is flagged as `UNCLEAR` and any deadline calculation is withheld.
- **Transparent Accommodation Deadline Engine:** Computes accommodation request deadlines using deterministic weekday calendar math (skipping weekends), classifies instruction strength (`mandatory`, `recommended_or_qualified`, `informational`, `unclear`), preserves qualifiers (*"if possible"*), and explicitly discloses California municipal holiday closure uncertainty.
- **Contextual Distinction Defense:** Strictly separates public-comment submission rules (e.g., speaker card deadlines by 3:00 PM) from disability accommodation request timelines.
- **One-Click Authentic Sample Agendas:** Pre-loaded with authentic, unaltered agendas from Claremont, Berkeley, San José, and Isla Vista so judges and attendees can test instantly without finding a PDF.
- **Attendee Action Plan & Export:** Generates practical next steps for attendees with one-click clipboard copying and clean print layouts.
- **Ephemeral Processing & Zero Retention:** Documents are processed using temporary buffers that are closed and deleted immediately upon request completion. No attendee documents are permanently stored on server disk.

---

## 🛡️ What This Is NOT

- **NOT a legal compliance auditor:** We do not issue binding legal determinations under the Ralph M. Brown Act or ADA Title II, and we do not assign arbitrary letter grades or 0–100% scores.
- **NOT a generic chatbot:** We do not guess, converse, or hallucinate. Every finding is anchored to verbatim quotations and physical page numbers.
- **NOT a compliance barrier:** Designed strictly to support disabled attendees in participating in local democracy.

---

## 🏗️ Technical Architecture

- **Frontend:** React 19 + TypeScript + Vite (High-contrast accessible UI, responsive layouts, ARIA live regions)
- **Backend:** Python 3.11 + FastAPI + Pydantic v2
- **AI Engine:** Google Gemini (`gemini-3.8-flash`) via the official Google Gen AI Python SDK (`google-genai`)
- **PDF Extraction:** `pdfplumber` + `pypdf` (Ephemeral stream extraction with automatic descriptor cleanup)
- **Deterministic Verification:** Custom Python substring, whitespace-normalization, and semantic context validator
- **Testing:** `pytest` + `httpx` + `anyio` (43 automated tests passing)

```text
├── sample_data/                          # Authentic California agendas & manifest
│   ├── 11-10-26-city-council-agenda-only.pdf (City of Claremont, 6 pages)
│   ├── 2026-03-10-berkeley-council-agenda.pdf (City of Berkeley, 4 pages)
│   ├── sanjose-council-agenda-1101871.pdf     (City of San José, 11 pages)
│   ├── 10-27-2026-isla-vista-csd-agenda.pdf   (Isla Vista CSD, 4 pages)
│   └── MANIFEST.md                            # SHA-256 hashes & official URLs
├── DEMO_SCRIPT.md                        # 2-3 minute structured judge walkthrough
├── PROJECT_OVERVIEW.md                   # Comprehensive architecture & civic problem report
├── backend/
│   ├── app/
│   │   ├── config.py                     # Environment settings & model selection
│   │   ├── main.py                       # FastAPI entrypoint & CORS configuration
│   │   ├── routers/
│   │   │   ├── analysis.py               # Document & sample analysis endpoints
│   │   │   └── documents.py              # Ingestion & extraction endpoints
│   │   ├── schemas/
│   │   │   ├── analysis.py               # Findings & report schemas
│   │   │   ├── deadline.py               # Deadline interpretation schemas
│   │   │   └── document.py               # Page extraction schemas
│   │   └── services/
│   │       ├── analysis_service.py       # Google Gen AI integration & retry handler
│   │       ├── deadline_service.py       # Transparent deadline calculation engine
│   │       ├── pdf_extractor.py          # Ephemeral pdfplumber page extraction
│   │       ├── pdf_validator.py          # Magic bytes, bounds, & encryption validation
│   │       └── verification_service.py   # Deterministic quote & context verification
│   ├── tests/                            # 43 automated unit & integration tests
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── App.tsx                       # Complete interactive dashboard & sample loader
    │   └── main.tsx
    ├── package.json
    └── vite.config.ts
```

---

## 🚀 Quick Start

### 1. Backend Setup

```bash
cd backend

# Create and activate Python 3.11 virtual environment
python -m venv .venv
# On Windows PowerShell:
.venv\Scripts\Activate.ps1
# On Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Ensure GEMINI_API_KEY is set in backend/.env

# Start FastAPI backend
uvicorn app.main:app --reload --port 8000
```
- Health Check: `http://localhost:8000/api/health`
- Interactive API Docs: `http://localhost:8000/docs`

### 2. Frontend Setup

```bash
cd frontend

# Install npm dependencies
npm install

# Start Vite development server
npm run dev
```
- Web Application: `http://localhost:5173`

---

## 🧪 Running Automated Tests

Run the complete 43-test test suite:

```bash
# In backend directory with .venv active:
pytest -v
```

All 43 tests verify:
- Ephemeral PDF validation, encryption detection, and upload limits
- Scanned document heuristics and text extraction
- Contextual Gemini analysis and structured JSON parsing
- Exponential backoff recovery for transient API errors
- Deterministic quotation verification against physical pages
- Contextual separation of public comments vs disability deadlines
- Deterministic working-day deadline calculations (skipping weekends)
- Real-world validation against Claremont, Berkeley, San José, and Isla Vista fixtures

Build frontend for production:
```bash
cd frontend
npm run build
```

---

## 📚 Documentation Links

- **[DEMO_SCRIPT.md](file:///DEMO_SCRIPT.md):** 2–3 minute step-by-step judge demonstration guide.
- **[PROJECT_OVERVIEW.md](file:///PROJECT_OVERVIEW.md):** Detailed civic technology problem statement, Ralph M. Brown Act / ADA Title II context, and system design.
- **[sample_data/MANIFEST.md](file:///sample_data/MANIFEST.md):** Official source URLs, SHA-256 hashes, and provenance for all test fixtures.

---

## ⚖️ License & Acknowledgements

Created for **Bridge The Gap Hacks 2026**. Dedicated to advancing civic accessibility and public participation for disabled Californians under the Americans with Disabilities Act of 1990 and the Ralph M. Brown Act.
