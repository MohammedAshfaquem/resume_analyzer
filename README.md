# Rolewise — Resume Analyzer

A small Django application that compares a resume with a job description and suggests truthful improvements. No login, database, saved history, React app, or frontend build step.

The interface uses a purple dashboard layout inspired by [this Mock AI design](https://dribbble.com/shots/27213385-Mock-AI-AI-Resume-Analyzer-SaaS-Design). Local CSS and vanilla JavaScript provide an animated score ring, score count-up, coverage bar, floating document illustration, card reveals and hover feedback. Motion respects `prefers-reduced-motion`, and content stays readable with JavaScript disabled. Sidebar and requirement chips link to actual page sections; dashboard values come from the analysis result.

## Run locally (Windows PowerShell)

Use Python 3.12 or newer.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements/development.txt
Copy-Item .env.example .env
```

Get a Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey). Edit `.env` and set `GEMINI_API_KEY` to your own key. `GEMINI_MODEL` defaults to `gemini-3.5-flash-lite`; change it to a model your account can access that supports Gemini structured JSON output. Restart Django after changing environment settings.

```powershell
.\.venv\Scripts\python.exe manage.py runserver
```

Open http://127.0.0.1:8000/. There is no migration step. Upload and preview work without an API key; AI analysis requires a valid key and API credit. If Windows opens the Microsoft Store for `python`, use the full path of your installed Python executable for the first command.

## Use it

1. Upload a PDF/DOCX and click **Extract text**, or paste resume text directly.
2. Review the extracted text, especially columns and tables. Paste a job description.
3. Click **Analyze my fit**. The resume text and job description are sent to Google Gemini.
4. Review requirement evidence, improvement suggestions and wording drafts.
5. Download the plain-text report before leaving, or edit the text and analyze again.

**Try example text** fills both fields with sample inputs. It does not generate fake results or bypass the API. **Edit text & analyze again** returns to the inputs; nothing is automatically added to a CV.

## Folder structure

```text
Resume Analyzer/
├── manage.py
├── .env.example
├── config/
│   ├── settings.py          # Environment, templates, static files; no database
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── apps/
│   ├── __init__.py
│   └── analyzer/
│       ├── __init__.py
│       ├── apps.py          # Django app registration
│       ├── urls.py
│       ├── views.py         # Function-based upload/preview/analysis view
│       ├── parsing.py       # PDF and DOCX extraction
│       ├── analysis.py      # AI response schema and evidence checks
│       ├── scoring.py       # Python coverage calculation
│       └── tests/
│           ├── __init__.py
│           ├── test_parsing.py
│           ├── test_scoring.py
│           └── test_analysis.py
├── templates/analyzer/
│   ├── base.html
│   ├── index.html
│   └── results.html
├── static/analyzer/
│   ├── style.css
│   └── app.js
├── tests/
│   ├── __init__.py
│   └── test_views.py        # Request/response integration tests
├── requirements/
│   ├── base.txt            # Shared dependencies
│   ├── development.txt     # Includes base.txt
│   └── production.txt      # Includes base.txt
└── docs/
    └── implementation-plan.md
```

Read `apps/analyzer/views.py` first, then `parsing.py`, `analysis.py` and `scoring.py` in the same folder. Application logic uses normal functions. The three small Pydantic classes in `analysis.py` only describe structured response data; `apps.py` uses Django's standard app configuration class, and test classes use Django/unittest conventions. There are no models, class-based views, repositories or service abstractions. Styles are plain local CSS to keep this version free of Node tooling and CDN dependencies.

App-specific tests live beside the analyzer code; complete request/response tests live in the root `tests/` package. Templates and static assets stay namespaced under `analyzer/` so future apps can use their own filenames. Development and production dependency files currently include the same base packages; add environment-specific packages only when needed. Install production dependencies with `pip install -r requirements/production.txt`.

There is no `users/` app because there is no login, no `models.py` or migrations because there is no database, and no `media/` folder because uploads are not saved. A `common/` package can be introduced when multiple apps actually share functionality.

## What the score means

The AI identifies distinct required/preferred requirements and matches them to resume evidence. Python checks that cited excerpts exist in the submitted documents, then calculates coverage:

- Required requirement: weight **2**; preferred requirement: weight **1**.
- Supported: **full credit**; partial: **half credit**.
- Not demonstrated or unclear: **zero credit**.
- Score: **earned weighted credit / possible weighted credit × 100**, rounded.

Requirements with fabricated job quotes or duplicate names invalidate the report. Matches with unverified resume quotes become unclear and receive no credit. Rewrites with unverified original text are omitted.

This is an explainable application rubric, not an employer's ATS score or probability of hiring. Exact quote checks prevent invented citations, but cannot prove that AI interpreted a requirement correctly or extracted every requirement. Review all results. Never add experience, certifications or metrics you cannot substantiate. Wording suggestions remain drafts.

## Files and privacy

- PDF/DOCX only, maximum 5 MB; PDFs maximum 15 pages.
- Resume text: 60–40,000 characters; job description: 50–20,000 characters.
- DOCX expanded contents are limited to 20 MB.
- Scanned/image-only PDFs need OCR, which is outside this version.
- Password-protected PDFs must be unlocked first. Legacy `.doc` files are unsupported.
- PDF reading order and Word text boxes/complex layouts can need manual correction.
- Uploads are read during a request. Django may use temporary upload files and closes/removes them at request completion; no permanent copy is written by the app.
- No server-side analysis history, browser local storage, database or sessions. Returned HTML includes inputs and report content so you can edit/download them. Refreshing a POST may resubmit; browser history is not an application history feature.
- Responses use `Cache-Control: no-store`. The only app cookie is for CSRF protection.
- Analysis sends document text to Google Gemini using the Google Gen AI SDK. Processing, retention and any use for product improvement depend on your Google API account and service terms. This app does not promise zero provider retention.
- API keys stay on the backend. The app does not log resume text or provider error bodies.

## Checks

```powershell
.\.venv\Scripts\python.exe manage.py test
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe -m pip check
```

Tests create real PDF/DOCX documents, verify weighted scores and evidence checks, exercise the upload/preview/results flow, and check CSRF and escaped output. Only external AI responses are mocked. Running the test suite does not call Google Gemini or need API credit.

## Deployment later

This version runs locally with Django's development server. Before a public deployment, set `DJANGO_DEBUG=false`, a strong `DJANGO_SECRET_KEY`, and your real `DJANGO_ALLOWED_HOSTS`; serve HTTPS using a production WSGI/ASGI server and configure static files. Limit request bodies at the proxy (for example, 6 MB total) and rate-limit the analysis endpoint to control anonymous API spending. Uploaded files have an application size check, but the proxy must reject oversized uploads before Django receives them.

No database is needed for deployment either. Docker, queues, OCR, accounts and saved history are deliberately outside this first version.
"# resume_analyzer" 
