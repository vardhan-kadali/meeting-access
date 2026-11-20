# Test Fixtures & Source Provenance Manifest

## 1. Authentic Official Government Record

- **File Name:** `11-10-26-city-council-agenda-only.pdf`
- **Jurisdiction:** City of Claremont, California
- **Body:** City Council Regular Meeting
- **Meeting Date:** Tuesday, November 10, 2026 at 6:30 PM
- **Official Source URL:** `https://www.claremontca.gov/files/assets/public/v/1/city-clerk/documents/city-council-agendas/2026/11-10-26-city-council-agenda-only.pdf`
- **File Size:** 119,267 bytes
- **SHA-256 Checksum:** `f52ca0ed1a784c6d077b10c9d02f93e158ce8acc040b734c0415d3d9b3ed023d`
- **PDF Version:** `%PDF-1.7`
- **Total Physical Pages:** 6
- **Physical Page of ADA Notice:** Page 6 (bottom certification block)
- **Official Disability Accommodation Verbatim Text:**
  > "IN COMPLIANCE WITH THE AMERICANS WITH DISABILITIES ACT 0F 1990, THIS AGENDA WILL BE MADE AVAILABLE IN APPROPRIATE ALTERNATIVE FORMATS TO PERSONS WITH DISABILITIES. ANY PERSON WITH A DISABILITY WHO REQUIRES A MODIFICATION OR ACCOMMODATION IN ORDER TO PARTICIPATE IN A CITY MEETING SHOULD CONTACT THE CITY CLERK AT 909-399-5461 or 909-399-5463 “VOICE” OR 1-800-735-2929 “TT/TTY” AT LEAST THREE (3) WORKING DAYS PRIOR TO THE MEETING, IF POSSIBLE."
- **Provenance / Ingestion Notes:** Downloaded directly from the official City of Claremont municipal web portal on November 20, 2026 via Playwright Chromium browser session, preserving exact original binary bytes.

---

## 2. Synthetic Test Fixture (Clearly Labeled)

- **File Name:** `synthetic_claremont_agenda.pdf` (formerly `claremont_sample_agenda.pdf`)
- **Classification:** **SYNTHETIC TEST FIXTURE (NOT AN OFFICIAL RECORD)**
- **Purpose:** Created programmatically during Milestone 2 unit tests to verify basic PDF parser mechanics before live source acquisition.
- **Discrepancies Against Official Record:**
  * Contained synthetic phone number `(909) 399-5460` instead of official `909-399-5461` or `909-399-5463`.
  * Contained synthetic email `cityclerk@ci.claremont.ca.us` instead of official `cityclerk@claremontca.gov`.
  * Contained a rigid `72 hours prior` timeline instead of the authentic statutory instruction `THREE (3) WORKING DAYS PRIOR TO THE MEETING, IF POSSIBLE`.
  * Omitted California Relay TTY/TDD service `1-800-735-2929`.
  * Condensed meeting into 3 pages rather than the authentic 6-page document.
