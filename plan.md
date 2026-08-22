# Project Plan - ReallyRobert.com Enhancement

## 1. Research & Analysis
- [x] Inspect existing `requirements.txt` and compare against `app/main.py` imports.
- [x] Document all necessary production dependencies.
- [x] **CRITICAL:** Fix validation mismatch between consultation form and `/contact` endpoint.

## 2. Template and Code Refactoring
- [x] Move HTML content from `app/main.py` into new template files.
- [x] Update `app/main.py` to use `Jinja2Templates`.
- [x] **MODULARITY UPDATE:** Split routes into `app/routers/pages.py` and `app/routers/api.py`.
- [x] Ensure HTMX triggers and targets remain functional.

## 3. Production Configuration
- [x] Ensure the application listens on `0.0.0.0` and respects the `$PORT` environment variable.
- [x] Add `railway.toml`.
- [x] Add a `/health` endpoint.

## 4. UI/UX Refinement Phase
- [x] Fix form submission feedback.
- [x] Fix accidental anchor-scroll on page load.
- [x] Typography, hierarchy, interactive components, error/success feedback, and responsiveness.

## 5. Security & Robustness
- [x] Add input validation/sanitization to form endpoints (`/contact`).
- [x] Implement Python standard logging for server-side diagnostics.
- [x] Ensure no secrets are hardcoded.
- [x] Documentation endpoints (`/docs`, `/redoc`) hidden in production.
- [x] Backend input validation implemented.
- [x] `UniqueConstraint` on email in `models.py` added.
- [x] Rate-limiting middleware implemented.

## 6. Verification & Final Deployment
- [x] Run local FastAPI server and verify all routes.
- [x] Validate static file and template loading.
- [x] Complete test suite (`pytest`) verification.
- [ ] Final production environment smoke test.

