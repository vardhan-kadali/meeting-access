# MEETING ACCESS — Hackathon Judge Demo Script
**Project:** MEETING ACCESS  
**Tagline:** Know if you can participate before the meeting begins.  
**Hackathon:** Bridge The Gap Hacks 2026  
**Category:** Accessibility, Civic Technology & Public Participation  
**Target Geography:** California, USA  
**Estimated Demo Time:** 2–3 minutes  

---

## 🎯 1. The Opening Hook (30 Seconds)

> *"Good morning judges. Imagine you are a Californian with a disability—a wheelchair user, a person who is deaf or hard of hearing, or a resident who needs meeting materials in large print.*
> 
> *A local city council meeting is scheduled to decide on zoning or budget issues that directly affect your life. You want to attend and speak. You find the official agenda PDF online.*
> 
> *Now ask yourself: Do you know how to request an accommodation? Whom do you contact? Is there an ASL interpreter? Are assistive listening devices available in chambers? And crucially—when is the deadline to ask? If you miss it, you may be shut out before the meeting even starts.*
> 
> *This is why we built **MEETING ACCESS**."*

---

## 💡 2. What MEETING ACCESS Is (and Is NOT) (30 Seconds)

> *"MEETING ACCESS is an evidence-backed civic accessibility intelligence platform. It takes authentic California public meeting agendas and answers one essential question: **Know if you can participate before the meeting begins.**
> 
> Let us be clear about what this is NOT:
> 1. **It is NOT a legal compliance checker.** We do not judge whether a city violated the Ralph M. Brown Act or Title II of the Americans with Disabilities Act. We do not issue arbitrary letter grades or 0–100% compliance scores.
> 2. **It is NOT a generic chatbot.** Standard LLMs frequently hallucinate phone numbers, invent generic deadlines like '72 hours', and confuse public-comment rules with disability accommodation rights.
> 3. **MEETING ACCESS is attendee-first intelligence.** Every single finding is backed by an exact verbatim quotation matched deterministically to a physical PDF page. If the evidence isn't on that page, it is rejected."*

---

## 🖥️ 3. Live Demonstration Walkthrough (90 Seconds)

### Step 1: Instant Judge Demo via Authentic Pre-Loaded Agendas
- Point to the **"Try with Authentic California Agendas (One-Click Demo)"** section at the top of the interface.
- *"Judges don't need to hunt for California municipal agendas on government websites. We have pre-loaded four diverse, authentic, unaltered government records directly into the UI."*

### Step 2: The Core Case Study — City of Claremont City Council
1. Click **"Analyze Sample"** on the **City of Claremont** card (`11-10-26-city-council-agenda-only.pdf`).
2. Watch the **Multi-Stage Processing Indicator**:
   - *Stage 1:* Ephemeral PDF extraction & text density check.
   - *Stage 2:* Contextual Gemini extraction across 9 participation categories.
   - *Stage 3:* Deterministic physical page quotation verification.
   - *Stage 4:* Transparent deadline interpretation & holiday disclosure.
3. Show the **Accommodation Request Deadline Interpretation Card**:
   - **Target Event:** Claremont City Council Meeting (Tuesday, November 10, 2026).
   - **Original Instruction:** *"AT LEAST THREE (3) WORKING DAYS PRIOR TO THE MEETING, IF POSSIBLE."* (Page 6).
   - **Instruction Strength:** `RECOMMENDED / QUALIFIED` — preserves the statutory qualifier *"if possible"*.
   - **Estimated Request Deadline:** **Thursday, November 05, 2026** (3 weekdays subtracted, skipping Saturday and Sunday).
   - **Calculation Status:** `PROVISIONAL` with full disclosure: local municipal holiday closures could shift this earlier.
4. Show the **Contextual Distinction Defense**:
   - On Page 1 of Claremont's agenda, there is a public-comment phone registration cutoff: *"by 3 PM the day of the meeting"*.
   - Point out that MEETING ACCESS properly categorizes this under `Public Comment Instructions` and **never confuses it with the disability accommodation deadline**.

### Step 3: Multi-Category Accessibility — City of Berkeley City Council
1. Click **"Analyze Sample"** on the **City of Berkeley** card (`2026-03-10-berkeley-council-agenda.pdf`).
2. Show the rich multi-category extraction:
   - **Live Captioning (Page 1 & 3):** Verified citation for B-TV broadcast and live web stream.
   - **Assisted Listening Devices (Page 3):** Available in chambers from the City Clerk prior to meeting start.
   - **TDD Line (Page 3):** `(510) 981-6347 (TDD)`.
   - **Calculated Deadline:** Tuesday, March 10, 2026 minus 3 business days = **Thursday, March 05, 2026**.

### Step 4: Robust Edge Cases — San José & Isla Vista
1. **City of San José Planning Commission (11 Pages):**
   - Automatically detects that Wednesday, May 10, 2023 is a past meeting and tags it with a **Past Meeting** badge.
   - Accurately ignores non-disability uses of the word "accommodate" (such as Page 5's *"to accommodate significant public testimony"*).
2. **Isla Vista Community Services District (Bilingual Notice):**
   - Contains a bilingual English/Spanish notice ("encouraged to contact the District prior to the meeting date").
   - Notice that the system safely marks calculation status as `CANNOT CALCULATE` without inventing an arbitrary deadline date.

### Step 5: Attendee Action Plan & Export
- Scroll to the **"Your Participation Next Steps"** card.
- Click **"📋 Copy Attendee Summary"** to demonstrate how an attendee gets an instant, plain-text summary ready to paste into an email to the City Clerk or save on their phone.
- Click **"🖨️ Print Plan"** to show the clean print-ready format.

---

## 🏗️ 4. Technical Architecture & Constraints (30 Seconds)

> *"Under the hood, MEETING ACCESS is built with a zero-cost production stack:
> - **Frontend:** React 19 + TypeScript + Vite, featuring high-contrast accessible layouts and ARIA live regions.
> - **Backend:** Python 3.11 + FastAPI + Pydantic v2 schemas.
> - **AI Extraction:** Google Gemini (`gemini-3.5-flash-lite` primary with `gemini-3.1-flash-lite` fallback) via the official Google Gen AI Python SDK.
> - **Verification Engine:** Pure Python deterministic substring & normalization validator running in memory.
> - **Ephemeral Processing:** Ephemeral document processing; temporary spooled files are released immediately on completion without persistent document storage.
> - **Test Suite:** 61 automated unit and integration tests passing in pytest with zero failures."*

---

## 🏁 5. Concluding Takeaway

> *"Participation in local democracy shouldn't require legal training or detective work.
> 
> With **MEETING ACCESS**, every disabled Californian can know exactly who to call, what services exist, and when to act—before the meeting begins.
> 
> Thank you."*
