# Resume Analyzer Implementation Plan

**Goal:** A readable, function-based Django application that compares a CV with a job description, without login or a database.

**Architecture:** One Django app renders HTML templates. Files are parsed during the request, users review extracted text, and a separate request sends that text to Google Gemini. Nothing is saved between requests. Pydantic classes describe API response data only; application behavior lives in ordinary functions.

**Stack:** Django, plain CSS and JavaScript, PyMuPDF, python-docx, Google Gemini, Pydantic, python-dotenv. Plain CSS replaces Tailwind to avoid a Node build or runtime CDN for this small app.

## Files

- `config/`: settings and root URLs/WSGI/ASGI entry points.
- `apps/analyzer/views.py`: upload, preview and analysis requests.
- `apps/analyzer/utils.py`: bounded PDF/DOCX text extraction and weighted requirement coverage.
- `apps/analyzer/analysis.py`: structured AI response and evidence validation.
- `templates/analyzer/`: input and results templates.
- `static/analyzer/`: local CSS and progressive JavaScript.
- `apps/analyzer/tests/`: parsing, scoring, AI boundary and request tests.
- `README.md`, `.env.example`, `requirements/base.txt`: setup and usage.

## Constraints and review focus

- No database, accounts, sessions, stored uploads or server-side report history.
- Function views and helpers; no service/repository layers or background workers.
- Support text PDFs and DOCX; reject scans with an actionable message. No OCR initially.
- Limit files to 5 MB, PDFs to 15 pages, extracted text to 40,000 characters, job descriptions to 20,000 characters, and DOCX expanded contents to 20 MB.
- Reject corrupt, empty, encrypted and unsupported files without exposing parser exceptions.
- AI evidence must occur in the submitted documents; unsupported resume evidence becomes unclear and earns no credit.
- Scores are requirement coverage, not hiring predictions. Required items weigh 2 and preferred items weigh 1; supported earns 1, partial 0.5, missing/unclear 0.
- Render model and user text with HTML escaping. Validate CSRF. Do not log CVs, job descriptions or API credentials.
- Clearly report missing API configuration, provider failures, invalid responses and ungrounded job requirements.

## Tasks

- [x] 1. Add parsing and scoring behavior tests; run them red. Implement extraction and deterministic scoring; run green.
- [x] 2. Add AI-boundary and request tests; run red. Implement structured analysis, evidence checks and database-free Django requests; run green.
- [x] 3. Build responsive input, preview and results pages, sample text, loading feedback, and browser-side report download.
- [x] 4. Write setup documentation, run the full suite and Django checks, then verify the rendered flow. Record any live-API verification limitation.

## Progress

- User approved the simplified scope and requested implementation directly. No extra design approval round or git workflow is needed in this empty, non-git folder.
- Verification: 26 tests pass; Django system check, dependency check and JavaScript syntax check pass. Database-free upload/preview/results requests are covered by Django tests.
- Browser: desktop input page and 390px mobile layout inspected; sample inputs and report download work without JavaScript errors or horizontal overflow. Results layout/download checked with a synthetic fixture rendered through the real template, not a live AI result.
- Review caught whitespace-only evidence bypassing substring checks. A regression test failed first, then passed after rejecting blank normalized job evidence.
- Live provider check with synthetic text: sandbox connection blocked; authorized network retry reached the provider and returned HTTP 429. Successful live generation remains unverified pending provider quota/rate-limit resolution.

- Folder layout updated to the user example: `apps/analyzer/`, root `templates/`, `static/`, integration `tests/`, and `requirements/`. Imports, app registration, template discovery and static discovery updated together. No unused database/auth/shared modules added.

- Provider changed to Gemini using google-genai, GEMINI_API_KEY and GEMINI_MODEL. Existing evidence checks, score calculation and function-based flow remain.
- Gemini verification: all 29 tests pass, Django checks pass and dependencies are consistent. Live synthetic analysis reached Gemini but the configured credential was rejected: "API key not valid." Successful live Gemini generation needs a valid key.
- Visual refresh: purple dashboard, functional section navigation, animated score ring/count-up, coverage bar, requirement chips, card reveals, hover feedback and loading spinner. CSS/vanilla JavaScript only, with reduced-motion and no-JavaScript support. Reference: https://dribbble.com/shots/27213385-Mock-AI-AI-Resume-Analyzer-SaaS-Design
- Visual verification: desktop and 390px mobile layouts checked; no horizontal overflow or browser JavaScript errors. Score ring animates with normal motion and has zero active animations with reduced motion. Chips reach requirement anchors; plain-text report downloads. Results verified using synthetic fixtures; no live AI call was needed for the design change. All 29 tests and Django checks pass after the refresh.
