# MEETING ACCESS — Free Cloud Deployment Guide

This guide details the step-by-step process for deploying **MEETING ACCESS** to free-tier cloud hosting:
- **Backend API:** [Render](https://render.com) (Free Web Service)
- **Frontend Dashboard:** [Cloudflare Pages](https://pages.cloudflare.com) (Free Static / SPA Hosting)
- **Total Budget:** **$0 / month** (no credit card or paid trials required)

---

## 📋 Architectural Overview

```
[ User Browser / Judge ]
         │
         │  1. Loads React SPA assets
         ▼
[ Cloudflare Pages: https://<your-project>.pages.dev ]
  • Root Directory: frontend
  • Build Command: npm run build
  • Output Directory: dist
  • Env Var: VITE_API_BASE_URL=https://<your-service>.onrender.com
         │
         │  2. REST API Requests (JSON & multipart PDF streams)
         ▼
[ Render Web Service: https://<your-service>.onrender.com ]
  • Root Directory: (empty / repository root)
  • Build Command: pip install -r backend/requirements.txt
  • Start Command: uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port $PORT
  • Health Check: /api/health
  • Env Vars: GEMINI_API_KEY, GEMINI_MODEL, CORS_ORIGINS, PYTHON_VERSION
         │
         │  3. Contextual extraction
         ▼
[ Google Gemini Interactions API (`gemini-3.8-flash`) ]
```

---

## 🚀 Part 1: Backend Deployment on Render

Render hosts the FastAPI backend as a free web service.

### Step 1.1: Sign In to Render
1. Visit [dashboard.render.com](https://dashboard.render.com) and sign in (using GitHub is recommended).

### Step 1.2: Create a New Web Service
1. Click the **"New +"** button in the top navigation bar and select **"Web Service"**.
2. Select **"Build and deploy from a Git repository"** and click **Next**.
3. Choose your `MEETING ACCESS` GitHub repository (connect your GitHub account if not already connected).

### Step 1.3: Configure Web Service Settings
Fill in the deployment settings exactly as follows:

| Setting | Value | Notes |
| :--- | :--- | :--- |
| **Name** | `meeting-access-api` | Or any unique name you choose |
| **Region** | `Oregon (US West)` | Or Ohio (US East) |
| **Branch** | `master` | The branch to deploy from |
| **Root Directory** | *(Leave blank / empty)* | **Important:** Leaving this blank ensures the server has access to `sample_data/` at the repository root |
| **Runtime** | `Python 3` | Render native Python environment |
| **Build Command** | `pip install -r backend/requirements.txt` | Installs FastAPI, Uvicorn, google-genai, pdfplumber, pypdf |
| **Start Command** | `uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port $PORT` | Binds to 0.0.0.0 using Render's dynamic `$PORT` |
| **Instance Type** | `Free` | $0.00 / month |

### Step 1.4: Configure Environment Variables
Scroll down to the **"Environment Variables"** section and add the following keys:

| Key | Value | Purpose |
| :--- | :--- | :--- |
| `PYTHON_VERSION` | `3.11.0` | Pin Python runtime version |
| `ENVIRONMENT` | `production` | Production environment flag |
| `GEMINI_MODEL` | `gemini-3.8-flash` | Candidate Gemini model |
| `GEMINI_API_KEY` | *(Paste your Google Gemini API key)* | **Do not share in chat or public logs**; enter securely in Render's dashboard |
| `CORS_ORIGINS` | `*` | Allows Cloudflare Pages to connect. (You can also specify your exact `https://<project>.pages.dev` domain once created) |

### Step 1.5: Configure Health Check Path
1. Under **"Advanced"**, find **"Health Check Path"**.
2. Set it to: `/api/health`.
3. Render will poll this endpoint during deployment and ensure the service is fully running before routing live traffic.

### Step 1.6: Deploy and Obtain Backend URL
1. Click **"Create Web Service"**.
2. Render will build and deploy the container. Once the build finishes, you will see a public URL near the top of the service dashboard:
   - Example: `https://meeting-access-api.onrender.com`
3. Verify the deployment in your browser by visiting:
   - `https://<your-render-url>/api/health`
   - You should see `{"status":"healthy","service":"MEETING ACCESS API",...}`.
4. **Copy this live Render backend URL** for Part 2.

---

## ⚡ Part 2: Frontend Deployment on Cloudflare Pages

Cloudflare Pages hosts the Vite + React frontend with free global edge distribution.

### Step 2.1: Sign In to Cloudflare
1. Visit [dash.cloudflare.com](https://dash.cloudflare.com) and log in.
2. In the left navigation, go to **"Workers & Pages"** > **"Overview"**.

### Step 2.2: Create a New Pages Application
1. Click **"Create Application"** > select the **"Pages"** tab.
2. Click **"Connect to Git"**.
3. Select your `MEETING ACCESS` GitHub repository and click **"Begin setup"**.

### Step 2.3: Configure Build & Output Settings
Configure the build parameters exactly as follows:

| Setting | Value | Notes |
| :--- | :--- | :--- |
| **Project name** | `meeting-access` | This determines your default `*.pages.dev` subdomain |
| **Production branch** | `master` | The branch to deploy from |
| **Framework preset** | `Vite` | Standard Vite preset |
| **Root directory** | `frontend` | **Important:** The React frontend lives inside `frontend/` |
| **Build command** | `npm run build` | Runs `tsc -b && vite build` |
| **Build output directory** | `dist` | Vite production bundle destination |

### Step 2.4: Set Frontend Environment Variable
Scroll down to **"Environment variables (advanced)"** and add:

| Variable Name | Value | Description |
| :--- | :--- | :--- |
| `VITE_API_BASE_URL` | `https://<your-render-url>.onrender.com` | **The live Render URL from Part 1** (without trailing slash) |

*Note: You can add this under both Production and Preview environments.*

### Step 2.5: Deploy
1. Click **"Save and Deploy"**.
2. Cloudflare will install npm packages, compile TypeScript, run the Vite build, and deploy the assets to its global CDN in ~1 minute.
3. When finished, Cloudflare gives you a live production URL:
   - Example: `https://meeting-access.pages.dev`

---

## 🧪 Part 3: Live Verification Checklist

Once both services are deployed, test the complete live application in your browser:

1. **Backend Health Check:**
   - Open: `https://<your-render-url>/api/health`
   - Verify HTTP 200 JSON response confirming `status: "healthy"`, `configured_gemini_model: "gemini-3.8-flash"`, and `api_key_configured: true`.
2. **Frontend UI Loading:**
   - Open: `https://<your-cloudflare-pages-url>.pages.dev`
   - Confirm the hero section, tagline, and badges render cleanly.
3. **Sample Agenda Loading:**
   - Confirm all 4 sample cards (Claremont, Berkeley, San José, Isla Vista) appear in the demo section.
4. **Sample PDF Downloads:**
   - Click **"View PDF"** on the Claremont card.
   - Confirm the authentic government PDF opens in a new tab.
5. **One-Click Sample Analysis:**
   - Click **"Analyze Sample"** on the Claremont card.
   - Confirm the multi-stage progress indicator runs.
   - Confirm the **Accommodation Request Deadline** displays:
     * Calculated Date: **November 05, 2026**
     * Instruction Strength: **Recommended / Qualified** (*"if possible"*)
     * Page: **6**
     * Verification status: **Verified Document Citation**
6. **Attendee Action Plan:**
   - Click **"📋 Copy Attendee Summary"** and verify feedback confirmation appears.
7. **Custom Upload Validation:**
   - Drag and drop or upload a non-PDF file or corrupted file.
   - Confirm a clear, accessible error alert appears without crashing.
8. **Network Inspection:**
   - Open browser DevTools (F12 > Network tab).
   - Verify all API calls hit `https://<your-render-url>/api/...` with HTTP 200.
   - Verify that no API key or server secret is ever exposed in client requests or responses.

---

## ⚠️ Free-Tier Caveats & Expectations

- **Render Free Web Service Sleep Policy:**
  - On the Render free tier, web services automatically **spin down into sleep mode after 15 minutes of inactivity**.
  - When a user visits the site after it has been asleep, the first request triggers a cold-start spin-up taking approximately **45 to 60 seconds**.
  - Subsequent requests respond immediately with standard latency.
  - *Judge Tip:* If the sample analysis takes ~50 seconds on the very first click, the backend is cold-starting. Once awake, analysis completes in seconds.
- **Cloudflare Pages:**
  - Cloudflare Pages runs on Cloudflare's global edge network and does **not** sleep. It serves static assets instantaneously 24/7.
