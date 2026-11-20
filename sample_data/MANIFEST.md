# Test Fixtures & Source Provenance Manifest

This manifest documents the authentic official California public meeting agendas and synthetic test benchmarks used to test and validate **MEETING ACCESS** ("Know if you can participate before the meeting begins").

All authentic records preserve exact original binary bytes as published by California municipal and special-district government bodies.

---

## 1. Authentic Official Government Records

### Fixture 1: City of Claremont City Council
- **File Name:** `11-10-26-city-council-agenda-only.pdf`
- **Jurisdiction:** City of Claremont, California (Los Angeles County)
- **Body:** City Council Regular Meeting
- **Meeting Date:** Tuesday, November 10, 2026 at 6:30 PM
- **Official Source URL:** `https://www.claremontca.gov/files/assets/public/v/1/city-clerk/documents/city-council-agendas/2026/11-10-26-city-council-agenda-only.pdf`
- **File Size:** 119,267 bytes
- **SHA-256 Checksum:** `f52ca0ed1a784c6d077b10c9d02f93e158ce8acc040b734c0415d3d9b3ed023d`
- **PDF Version:** `%PDF-1.7`
- **Physical Pages:** 6
- **Physical Page of ADA Notice:** Page 6 (bottom certification block)
- **Official Disability Accommodation Verbatim Text:**
  > "IN COMPLIANCE WITH THE AMERICANS WITH DISABILITIES ACT 0F 1990, THIS AGENDA WILL BE MADE AVAILABLE IN APPROPRIATE ALTERNATIVE FORMATS TO PERSONS WITH DISABILITIES. ANY PERSON WITH A DISABILITY WHO REQUIRES A MODIFICATION OR ACCOMMODATION IN ORDER TO PARTICIPATE IN A CITY MEETING SHOULD CONTACT THE CITY CLERK AT 909-399-5461 or 909-399-5463 “VOICE” OR 1-800-735-2929 “TT/TTY” AT LEAST THREE (3) WORKING DAYS PRIOR TO THE MEETING, IF POSSIBLE."
- **Distinct Features:**
  - Qualified accommodation timeline ("at least three (3) working days prior to the meeting, if possible").
  - Alternative formats available.
  - California Relay TTY (`1-800-735-2929`) alongside voice phones.
  - Page 1 contains a distinct public-comment phone registration cutoff ("by 3 PM the day of the meeting"), properly isolated from ADA deadlines.

---

### Fixture 2: City of Berkeley City Council
- **File Name:** `2026-03-10-berkeley-council-agenda.pdf`
- **Jurisdiction:** City of Berkeley, California (Alameda County)
- **Body:** City Council Special Meeting
- **Meeting Date:** Tuesday, March 10, 2026 at 4:00 PM
- **Official Source URL:** `https://berkeleyca.gov/sites/default/files/2026-03/2026-03-10%20Special%20Agenda%20-%20Council.pdf`
- **File Size:** 290,456 bytes
- **SHA-256 Checksum:** `d5901172eb0632c02357ffc592a8826f1fc9551afd7e4146a081e3ff8059a78f`
- **PDF Version:** `%PDF-1.4`
- **Physical Pages:** 4
- **Physical Page of ADA Notice:** Page 3 (Communication Access Information) and Page 1 (Broadcast Captioning)
- **Official Disability Accommodation Verbatim Text:**
  > "COMMUNICATION ACCESS INFORMATION: To request a disability-related accommodation(s) to participate in the meeting, including auxiliary aids or services, please contact the Disability Services specialist at ada@berkeleyca.gov, (510) 981-6418 (V), or (510) 981-6347 (TDD) at least three business days before the meeting date. Captioning services are provided at the meeting, on B-TV, and on the Internet. In addition, assisted listening devices for the hearing impaired are available from the City Clerk prior to the meeting, and are to be returned before the end of the meeting."
- **Distinct Features:**
  - Multi-category accommodations: Live captions on B-TV and Internet stream (Page 1 & 3), assisted listening devices from City Clerk (Page 3), TDD line (`510-981-6347`), and dedicated email (`ada@berkeleyca.gov`).
  - Mandatory 3 business days request window before the meeting.
  - Detailed remote video and teleconference public comment rules on Page 1.

---

### Fixture 3: City of San José City Council
- **File Name:** `sanjose-council-agenda-1101871.pdf`
- **Jurisdiction:** City of San José, California (Santa Clara County)
- **Body:** City Council Regular Meeting
- **Meeting Date:** Tuesday, February 10, 2026 at 1:30 PM
- **Official Source URL:** `https://sanjose.legistar.com/View.ashx?M=A&ID=1101871&GUID=CC2EC380-3279-46E2-9423-D8438A276B80`
- **File Size:** 362,209 bytes
- **SHA-256 Checksum:** `1aad279ec6439a426f9f4acc0486e7fc8bcf03b465d922286fe596885da2ec58`
- **PDF Version:** `%PDF-1.5`
- **Physical Pages:** 11
- **Physical Page of ADA Notice:** Page 3
- **Official Disability Accommodation Verbatim Text:**
  > "To request an alternative format agenda under the Americans with Disabilities Act for City-sponsored meetings, events or printed materials, please call (408) 535-1260 (Voice) or (408) 294-9337 (TTY) as soon as possible, but at least three business days before the meeting or event. Accommodations: Any member of the public who needs accommodations should email the ADA Coordinator at ADA@sanjoseca.gov or by calling (408) 535-8430."
- **Distinct Features:**
  - Extensive 11-page legislative agenda from Legistar.
  - Accommodation instructions split between alternative format request line (`(408) 535-1260` / `(408) 294-9337`) and general ADA coordinator (`ADA@sanjoseca.gov` / `(408) 535-8430`).
  - Contains non-disability usage of the word "accommodate" on Page 5 ("to accommodate significant public testimony"), testing avoidance of false positives.

---

### Fixture 4: Isla Vista Community Services District
- **File Name:** `10-27-2026-isla-vista-csd-agenda.pdf`
- **Jurisdiction:** Isla Vista Community Services District, California (Santa Barbara County)
- **Body:** Board of Directors Regular Meeting
- **Meeting Date:** Tuesday, October 27, 2026 at 6:00 PM
- **Official Source URL:** `https://islavistacsd.ca.gov/files/6c8163956/10_27_2026+Regular+Meeting+Agenda.pdf`
- **File Size:** 390,013 bytes
- **SHA-256 Checksum:** `cbce85e696f7829663bfc3ec3416c5951ddf798d42ccf92e5fb4e9efd565789e`
- **PDF Version:** `%PDF-1.4`
- **Physical Pages:** 4
- **Physical Page of ADA Notice:** Page 1 & Page 4 (bilingual English/Spanish notice)
- **Official Disability Accommodation Verbatim Text:**
  > Page 1: "In compliance with the Americans with Disabilities Act (ADA), individuals with disabilities who need an accommodation to participate in this meeting are encouraged to contact the District as early as possible."
  > Page 4: "In accordance with the Ralph M. Brown Act and the Americans with Disabilities Act of 1990, a request for a disability-related modification or accommodation, including auxiliary aids or services, may be made by a person with a disability who requires a modification or accommodation in order to participate in the public meeting."
- **Distinct Features:**
  - Special district governance (community services district) rather than charter city.
  - Informational timing statement ("as early as possible" without a rigid day count), exercising the `informational` instruction strength classifier without producing false dates.
  - Bilingual notice provided in both English and Spanish on Page 4.

---

## 2. Synthetic Test Fixture (Clearly Demarcated)

- **File Name:** `synthetic_claremont_agenda.pdf` (formerly `claremont_sample_agenda.pdf`)
- **Classification:** **SYNTHETIC TEST FIXTURE (NOT AN OFFICIAL RECORD)**
- **Purpose:** Created programmatically during Milestone 2 unit tests to verify parser mechanics before live source acquisition.
- **Discrepancies Against Official Record:**
  - Contained synthetic phone number `(909) 399-5460` instead of official `909-399-5461` or `909-399-5463`.
  - Contained synthetic email `cityclerk@ci.claremont.ca.us` instead of official `cityclerk@claremontca.gov`.
  - Contained a rigid `72 hours prior` timeline instead of the authentic statutory instruction `THREE (3) WORKING DAYS PRIOR TO THE MEETING, IF POSSIBLE`.
  - Omitted California Relay TTY/TDD service `1-800-735-2929`.
  - Condensed into 3 pages rather than authentic 6 pages.
