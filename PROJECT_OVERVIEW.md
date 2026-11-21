# MEETING ACCESS — Project Overview & Architecture

**Project Name:** MEETING ACCESS  
**Tagline:** Know if you can participate before the meeting begins.  
**Hackathon:** Bridge The Gap Hacks 2026  
**Category:** Accessibility, Civic Technology & Public Participation  
**Target Geography:** California, USA  

---

## 1. Executive Summary & Civic Mission

In California, thousands of local government bodies—city councils, county boards of supervisors, school boards, planning commissions, and special districts—meet regularly under the statutory requirements of the **Ralph M. Brown Act** (California Government Code § 54950 et seq.) and **Title II of the Americans with Disabilities Act of 1990** (42 U.S.C. § 12131 et seq.).

Under California law and federal regulations, public agencies must make their meetings accessible, provide agendas in alternative formats upon request, and furnish auxiliary aids and services—including American Sign Language (ASL) interpreters, live captioning (CART), and assistive listening devices—at no cost to participants.

### The Real-World Problem
In practice, vital participation and accommodation notices are buried in dense, multi-page PDF agendas:
- **Buried Information:** Disability accommodation notices frequently appear in fine print on the final page of a 10-to-50-page legislative document.
- **Confusing Timelines:** Instructions vary wildly between agencies: some state "three working days", others "72 hours", others "as soon as possible", and many qualify deadlines with "if possible" or "when feasible".
- **Public Comment Confusion:** Agendas routinely specify separate cutoffs for public-comment speaker cards (e.g., "by 3:00 PM the day of the meeting"), which attendees frequently mistake for disability accommodation request deadlines.
- **AI Hallucination Risk:** Generic consumer AI tools frequently invent fictional phone numbers, miss exact page numbers, or make unfounded compliance assertions that could mislead disabled constituents.

### Our Solution
**MEETING ACCESS** is not a generic chatbot and not a legal compliance auditor. It is an **evidence-backed public-meeting participation intelligence platform**. It accepts any California municipal agenda PDF, extracts and structures accessibility information across nine discrete categories, verifies every single finding against physical PDF page text deterministically, and provides a transparent, attendee-centered deadline interpretation.

---

## 2. Core Functional Pillars

### Pillar 1: Evidence-Backed Participation Intelligence
The application evaluates agendas across nine discrete categories without assuming all must be present:
1. **Disability Accommodation Contact Information:** Specific coordinator, office, voice phone, TTY/TDD line, or email.
2. **Accommodation Request Methods:** Clear instructions on how an attendee submits a modification request.
3. **Explicit Accommodation Deadlines:** Required advance notice timelines (working days, hours, calendar days).
4. **Alternative Document / Agenda Formats:** Availability of large print, Braille, or electronic formats.
5. **Sign Language / ASL Interpretation:** Specific instructions and notice timelines for requesting certified interpreters.
6. **Live Captions / Captioning:** Availability of CART, broadcast captioning (B-TV), or digital stream captions.
7. **Assisted Listening Devices:** Headsets, FM receivers, or induction neck loops available in hearing chambers.
8. **Remote Participation Instructions:** Teleconference, telephone dial-in, or video platform (Zoom) access links and passcode procedures.
9. **Public Comment Instructions:** Speaker cards, speaking time limits, and written public-comment submission rules.

### Pillar 2: Deterministic Python Verification Engine
To protect disabled residents from LLM hallucinations, MEETING ACCESS introduces an isolated **Python Verification Engine**:
- **Physical Page Citations:** Every finding must cite the exact physical page (1 to N) of the PDF.
- **Verbatim Substring Matching:** Whitespace-normalized quotations are checked directly against the text extracted from that specific physical page.
- **Contextual Distinction Defense:**
  - Public-comment deadlines (e.g., "by 3 PM") citing speaker cards are strictly rejected from the accommodation deadline category.
  - General accommodation language is rejected from the ASL category unless sign-language terms are explicitly present.
- **Status Integrity:** If a quote cannot be verified on the claimed page, its status is adjusted to `UNCLEAR` and its calculated deadline is withheld.

### Pillar 3: Transparent Accommodation Deadline Engine
Deadlines are interpreted through an attendee-support lens rather than a legal verdict:
- **Instruction Strength Classification:**
  - `MANDATORY`: Strict cutoff phrasing (*"must submit no later than"*, *"shall request"*).
  - `RECOMMENDED / QUALIFIED`: Instructions containing statutory qualifiers (*"if possible"*, *"when feasible"*, *"should"*).
  - `INFORMATIONAL`: General timing advice (*"as early as possible"*, *"prior to meeting"*) without specific day counts.
  - `UNCLEAR`: Conflicting or ambiguous instructions.
- **Deterministic Calendar Calculation:**
  - Weekday subtraction: For rules specifying "working days" or "business days", the engine counts backwards skipping Saturdays and Sundays.
  - Past Meeting Detection: Automatically identifies historical agendas and flags them.
- **Mandatory Limitation Disclosures:**
  - Discloses that local California state, county, or municipal holiday office closures could shift deadlines earlier.
  - Clarifies that calculations represent attendee support estimates, not binding legal determinations.

---

## 3. Real-World Agenda Benchmarks & Ground Truth

MEETING ACCESS was validated against authentic, unaltered government records downloaded directly from California municipal web portals. These files serve as reproducible repository test fixtures and automated regression benchmarks—they are optional demo fixtures, not mandatory application inputs:

| Benchmark Fixture | Jurisdiction & Body | Meeting Date | Pages | Key Distinct Features |
| :--- | :--- | :--- | :---: | :--- |
| **City of Claremont** | Claremont City Council | Nov 10, 2026 | 6 | Standard 3 working days qualified notice (*"if possible"*), TTY line, certification on Page 6, separate 3 PM public comment cutoff on Page 1. |
| **City of Berkeley** | Berkeley City Council | Mar 10, 2026 | 4 | Multi-category accommodations: Live B-TV captioning, assisted listening devices in chambers, TDD line, 3 business days request window. |
| **City of San José** | Planning Commission | May 10, 2023 | 11 | 11-page Legistar agenda, past meeting detection, multiple ADA contacts, non-disability term suppression (*"to accommodate public testimony"*). |
| **Isla Vista CSD** | Board of Directors | Oct 27, 2026 | 4 | Special district, bilingual English/Spanish notice, general advance notice without speculative date calculation. |

All source records, URLs, and SHA-256 binary checksums are maintained in [`sample_data/MANIFEST.md`](file:///sample_data/MANIFEST.md).

---

## 4. Technical Architecture & Zero-Cost Stack

MEETING ACCESS was designed from day one to operate entirely within a **$0 budget constraint**:

```
[ User Browser / Judge ]
         │
         ▼
[ React 19 + TypeScript + Vite Frontend ]
  • High-contrast accessible design
  • User-upload-first workflow with optional authentic test fixtures
  • Multi-stage animated processing indicator
  • Attendee participation action plan with clipboard copy & print
         │  HTTP REST (JSON & multipart/form-data)
         ▼
[ FastAPI (Python 3.11) Monorepo Backend ]
  ├── /api/health                          (Service & model status)
  ├── /api/documents/samples               (List authentic sample agendas)
  ├── /api/documents/samples/{id}/analyze  (Instant one-click sample analysis)
  ├── /api/documents/samples/{id}/download (Direct official government PDF download)
  └── /api/documents/analyze               (Custom PDF upload & analysis)
         │
  ├── 1. PDF Validator & Extractor (`pypdf`, `pdfplumber`)
  │      • Ephemeral processing (temporary spooled resources released immediately in finally blocks)
  │      • Text density & scanned document heuristic checks (OCR not currently implemented; scans flagged)
  │
  ├── 2. Google Gen AI SDK (`gemini-3.5-flash-lite` primary with automatic fallback to `gemini-3.1-flash-lite`)
  │      • Contextual schema extraction with structured JSON output
  │      • Prompt injection containment (`<untrusted_agenda_content>`)
  │      • Exponential backoff retry handler (mitigating transient 503 spikes)
  │
  ├── 3. Deterministic Quote Verification Service
  │      • Physical PDF page number bounding & exact substring validation
  │      • Semantic context distinction (public comment vs disability)
  │
  └── 4. Transparent Deadline Service
         • Weekday calendar calculations skipping weekends
         • Instruction strength & qualifier preservation
         • Holiday uncertainty disclosures
```

---

## 5. Security, Privacy & Ephemeral Document Processing

- **Ephemeral Processing & Resource Cleanup:** Uploaded agendas are handled via Starlette's `UploadFile` spooled temporary buffers. Small buffers remain in memory while larger payloads safely roll over to OS temporary files. In all cases, file descriptors and temporary resources are explicitly closed and released in `finally` blocks (`await file.close()`) immediately upon request completion. The backend does not maintain a database, persistent document archive, or long-term disk cache of user uploads.
- **Key Isolation:** Google Gemini API keys exist exclusively in server environment variables (`GEMINI_API_KEY`) and are never exposed to the client.
- **Prompt Injection Defense:** Untrusted document text is wrapped in defensive boundary tags (`<untrusted_agenda_content>`) with strict instructions to the model to ignore any embedded system directives.
- **Deterministic Python Enforcement:** Even if an adversarial prompt injection succeeded in convincing the model to fabricate a finding, the pure Python verification engine would reject it because the fabricated text cannot be located on the physical page.

---

## 6. Verification & Quality Assurance

- **61 Automated Tests:** All unit and integration tests pass with 100% success across extraction, schema validation, multi-model fallback chain, environment parsing, deadline calculations, and real-world agenda regressions.
- **MIT License:** Published under the open-source MIT License (see [LICENSE](LICENSE)).
- **TypeScript Type Safety:** Frontend code is strictly typed with zero build errors under `tsc -b && vite build`.
- **Reproducible Local Environment:** Clean monorepo structure with isolated virtualenv (`backend/.venv`) and standard npm scripts.
