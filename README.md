# reallyrobert.com

This is a production-hardened, FastAPI-based web application for "reallyrobert.com", deployed on Railway.

## Technical Stack
- **Framework:** FastAPI
- **Template Engine:** Jinja2
- **Frontend Interactivity:** HTMX
- **Styling:** Tailwind CSS
- **Database:** PostgreSQL (via SQLAlchemy/asyncpg)
- **Security:** SlowAPI (Rate-limiting)

## Modular Architecture
- `app/main.py`: Entry point, configuration, and app startup.
- `app/limiter.py`: Centralized rate-limiting configuration.
- `app/routers/`: Modular route definitions (`pages.py` for UI, `api.py` for API/Forms).
- `app/services/`: Business logic layer.
- `app/models.py`: Database schema with `UniqueConstraint` for concurrency safety.
- `app/templates/`: HTML templates and fragments.

## Security & SEO Features
- **Rate-Limiting:** `/contact` endpoint limited to 5 requests per minute using SlowAPI.
- **Input Validation:** Sanitization and validation for all contact form submissions.
- **Database Safety:** Unique constraints on email submissions.
- **SEO Ready:** Dynamically generated `/sitemap.xml` and `/robots.txt`.
- **Social Media:** Open Graph meta tags and favicon included in `base.html`.

## Brand Persona & About Content
**Core Philosophy:** 
"Efficiency isn't about the newest tool; it's about the smartest setup."

**Hero Section Messaging:**
"Opportunities To Improve Business Optimization. Get More From the Tools You Already Own! We help businesses reframe everyday tasks to eliminate inefficiencies, simplify workflows & improve operational performance."

## Deployment & Configuration
- **Railway Ready:** Includes `railway.toml` for automatic production deployment.
- **Environment Variables:** Configuration via `DATABASE_URL`.
    - Set `DATABASE_URL` in Railway's project dashboard for production.

## Local Development
1. Create a virtual environment: `python -m venv .venv && source .venv/bin/activate`
2. Install dependencies: `pip install -r requirements.txt` (or `pip install -r requirements-dev.txt` to also get test dependencies)
3. Configure `.env` with `DATABASE_URL`.
4. Run: `uvicorn app.main:app --reload`
5. Run tests: `pytest`

### Frontend assets
Tailwind CSS and HTMX are compiled/vendored into `app/static/` and committed, so the
steps above are all a fresh clone needs. Only rebuild if you change a template's
classes or bump the HTMX version:
1. `npm install`
2. `npm run build` (runs `build:css` and `build:js`; source lives in `assets/css/input.css` and `package.json`)
