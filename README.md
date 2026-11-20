# MEETING ACCESS

> **Know if you can participate before the meeting begins.**

An evidence-backed civic accessibility intelligence platform for California public meeting agendas. Built for **Bridge The Gap Hacks 2026** (Accessibility, Civic Technology & Public Participation).

---

## 🏛️ The Problem We Are Solving

In California, thousands of local legislative bodies—city councils, county boards of supervisors, school boards, and special districts—meet regularly under the statutory mandates of the **Ralph M. Brown Act** (California Government Code § 54950 et seq.) and **Title II of the Americans with Disabilities Act of 1990** (42 U.S.C. § 12131 et seq.).

Under state and federal law, public agencies must make their meetings accessible, furnish agendas in alternative formats upon request, and provide auxiliary aids and services—including American Sign Language (ASL) interpretation, live captioning (CART), and assistive listening devices—at no cost to participants.

However, in practice:
- **Buried Information:** Crucial accommodation instructions are frequently relegated to fine print on the final page of a 10-to-50-page legislative PDF agenda.
- **Confusing Advance Timelines:** Instructions vary widely (e.g., "three working days", "72 hours", "as soon as possible"), frequently qualified by phrases like "if possible".
- **Public Comment Confusion:** Agendas routinely specify separate cutoffs for public-comment speaker registration (e.g., "by 3:00 PM the day of the meeting"), which attendees frequently mistake for disability accommodation request deadlines.
- **AI Hallucination Risk:** Standard consumer AI chat tools routinely invent fictional phone numbers, guess generic deadlines, or hallucinate non-existent accessibility features.

**MEETING ACCESS** bridges this gap: it extracts, structures, and deterministically verifies accessibility notices against physical PDF pages, calculating transparent request deadlines while protecting attendees from misleading hallucinations.

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
├── DEPLOYMENT.md                         # Free cloud deployment guide (Render + Cloudflare)
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
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── App.tsx                       # Complete interactive dashboard & sample loader
│   │   └── main.tsx
│   ├── package.json
│   ├── vite.config.ts
│   └── .env.example
└── render.yaml                           # Render Web Service blueprint
```

---

## ⚙️ Environment Variables Required

### Backend Environment Variables (`backend/.env`)

| Variable Name | Default / Example | Required | Description |
| :--- | :--- | :---: | :--- |
| `GEMINI_API_KEY` | *(Secret key)* | **Yes** (for live AI) | Google Gemini API key from Google AI Studio. |
| `GEMINI_MODEL` | `gemini-3.8-flash` | No | Configurable Gemini model identifier. |
| `ENVIRONMENT` | `development` | No | Application environment (`development` / `production`). |
| `PORT` | `8000` | No | Port for Uvicorn server (automatically provided by cloud hosts like Render). |
| `HOST` | `0.0.0.0` | No | Network host binding. |
| `CORS_ORIGINS` | `["http://localhost:5173"]` | No | Allowed frontend origins (supports JSON array or comma-separated string). |
| `MAX_UPLOAD_SIZE_MB`| `15` | No | Maximum allowed agenda PDF upload size. |
| `MAX_PAGE_COUNT` | `100` | No | Maximum allowed physical page count per document. |

### Frontend Environment Variables (`frontend/.env`)

| Variable Name | Default / Example | Required | Description |
| :--- | :--- | :---: | :--- |
| `VITE_API_BASE_URL` | `""` (empty for local proxy) | No | Base URL of deployed backend (e.g. `https://meeting-access-api.onrender.com`). |

---

## 🚀 Local Installation & Quick Start

### 1. Prerequisites
- Python 3.11+
- Node.js 18+ and npm
- Git

### 2. Backend Setup

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
# Edit backend/.env to set your GEMINI_API_KEY

# Start FastAPI backend
uvicorn app.main:app --reload --port 8000
```
- Health Check: `http://localhost:8000/api/health`
- Interactive API Docs: `http://localhost:8000/docs`

### 3. Frontend Setup

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

## ⚠️ Current Limitations & API Key Requirement

1. **Gemini API Key Required for Live AI Analysis:**  
   The application requires a valid Google Gemini API key (`GEMINI_API_KEY`) to perform live contextual information extraction on new PDF agendas.
   - Without an API key, the health endpoint (`/api/health`) reports `api_key_configured: false`.
   - Text extraction (`/api/documents/extract`), sample listing, and PDF downloads remain fully operational without an API key.
2. **Text-Based Agenda Requirement:**  
   The system processes text-layer PDF documents. Photocopied or scanned image-only PDFs without an OCR text layer are identified and flagged with a clear user notice (`no_extractable_text`).
3. **Attendee Support Guidance, Not Legal Advice:**  
   Deadline calculations are deterministic estimates for attendee planning. Local municipal holiday closures could require requests to be submitted earlier. Calculations do not constitute formal legal compliance determinations.

---

## 🏛️ Authentic Sample Agendas & Attribution

MEETING ACCESS includes four authentic, unaltered California public meeting agendas downloaded directly from municipal web portals, cataloged with SHA-256 binary checksums in [`sample_data/MANIFEST.md`](file:///sample_data/MANIFEST.md):

| Sample Fixture | Agency & Jurisdiction | Meeting Date | Physical Pages | Official Source URL |
| :--- | :--- | :---: | :---: | :--- |
| **City of Claremont** | City of Claremont, CA | Nov 10, 2026 | 6 | [claremontca.gov](https://www.claremontca.gov/files/assets/public/v/1/city-clerk/documents/city-council-agendas/2026/11-10-26-city-council-agenda-only.pdf) |
| **City of Berkeley** | City of Berkeley, CA | Mar 10, 2026 | 4 | [berkeleyca.gov](https://berkeleyca.gov/sites/default/files/2026-03/2026-03-10%20Special%20Agenda%20-%20Council.pdf) |
| **City of San José** | City of San José, CA | May 10, 2023 | 11 | [sanjose.legistar.com](https://sanjose.legistar.com/View.ashx?M=A&ID=1101871&GUID=CC2EC380-3279-46E2-9423-D8438A276B80) |
| **Isla Vista CSD** | Isla Vista CSD, CA | Oct 27, 2026 | 4 | [islavistacsd.ca.gov](https://islavistacsd.ca.gov/files/6c8163956/10_27_2026+Regular+Meeting+Agenda.pdf) |

---

## 📚 Documentation Links

- **[DEPLOYMENT.md](file:///DEPLOYMENT.md):** Step-by-step free cloud deployment guide for Render and Cloudflare Pages.
- **[DEMO_SCRIPT.md](file:///DEMO_SCRIPT.md):** 2–3 minute step-by-step judge demonstration guide.
- **[PROJECT_OVERVIEW.md](file:///PROJECT_OVERVIEW.md):** Detailed civic technology problem statement, Ralph M. Brown Act / ADA Title II context, and system design.
- **[sample_data/MANIFEST.md](file:///sample_data/MANIFEST.md):** Official source URLs, SHA-256 hashes, and provenance for all test fixtures.

---

## ⚖️ License Decision & Acknowledgements

Created for **Bridge The Gap Hacks 2026**. Dedicated to advancing civic accessibility and public participation for disabled Californians under the Americans with Disabilities Act of 1990 and the Ralph M. Brown Act.

*Note: A formal open-source license decision (e.g., MIT License, Apache 2.0) is pending final publication review.*
