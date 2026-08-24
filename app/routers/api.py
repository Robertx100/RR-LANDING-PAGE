from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from typing import Annotated, Optional
from urllib.parse import urlparse
from sqlalchemy.ext.asyncio import AsyncSession
from email_validator import validate_email, EmailNotValidError
from app.limiter import limiter

from app.database import get_db
from app.services.contact_service import save_contact_submission
from app.logger import get_logger, mask_email

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
logger = get_logger(__name__)

@router.get("/health")
async def health_check():
    return JSONResponse(content={"status": "ok"})

def _is_same_origin_request(request: Request) -> bool:
    """CSRF defense for the state-changing POST below. There's no session/cookie
    auth in this app for SameSite cookies to protect, so validate Origin/Referer
    directly (OWASP's recommended fallback) to stop a third-party page from
    silently auto-submitting this form through a visitor's browser.

    Compares hosts only (not scheme) so this doesn't depend on uvicorn's
    proxy-header trust config correctly reconstructing request.url.scheme."""
    host = request.headers.get("host", "")
    origin = request.headers.get("origin")
    if origin is not None:
        return urlparse(origin).netloc == host
    referer = request.headers.get("referer")
    if referer is not None:
        return urlparse(referer).netloc == host
    return False

@router.post("/contact", response_class=HTMLResponse)
@limiter.limit("5/minute")
async def contact_form(
    request: Request,
    name: Annotated[str, Form(max_length=50)],
    email: Annotated[str, Form(max_length=200)],
    link: Annotated[str, Form(max_length=500)],
    constraint: Annotated[Optional[str], Form(max_length=2000)] = None,
    fix_attempt: Annotated[Optional[str], Form(max_length=2000)] = None,
    performance_gap: Annotated[Optional[str], Form(max_length=2000)] = None,
    impact_bottleneck: Annotated[Optional[str], Form(max_length=2000)] = None,
    db: AsyncSession = Depends(get_db)
):
    if not _is_same_origin_request(request):
        logger.warning("Rejected cross-site /contact submission (Origin/Referer mismatch)")
        return HTMLResponse(
            content='<div class="text-red-600 p-4">Request blocked for security reasons. Please refresh the page and try again.</div>',
            status_code=403,
        )

    # Server-side validation
    name = name.strip()
    email = email.strip()
    link = link.strip()

    if not name or not email or not link:
        return f'<div class="text-red-600 p-4">Name, email, and link are required.</div>'

    # Explicit Email Validation
    try:
        validate_email(email)
    except EmailNotValidError as e:
        return f'<div class="text-red-600 p-4">Invalid email address.</div>'

    # The consultation form's four questions are HTML-required there, but the
    # shorter homepage contact form never sends them at all. If any one is
    # present, treat this as a consultation submission and require all four —
    # otherwise a partially-filled deep dive would save silently with gaps.
    deep_dive = {
        "constraint": constraint.strip() if constraint else "",
        "fix_attempt": fix_attempt.strip() if fix_attempt else "",
        "performance_gap": performance_gap.strip() if performance_gap else "",
        "impact_bottleneck": impact_bottleneck.strip() if impact_bottleneck else "",
    }
    if any(deep_dive.values()) and not all(deep_dive.values()):
        return '<div class="text-red-600 p-4">Please answer all four questions, or leave them all blank.</div>'

    submission_data = {
        "name": name,
        "email": email,
        "link": link,
        "constraint": deep_dive["constraint"] or None,
        "fix_attempt": deep_dive["fix_attempt"] or None,
        "performance_gap": deep_dive["performance_gap"] or None,
        "impact_bottleneck": deep_dive["impact_bottleneck"] or None,
    }

    try:
        await save_contact_submission(db, submission_data)
        logger.info(f"Submission saved for email: {mask_email(email)}")
    except ValueError:
        # Duplicate email: save is skipped, but the response below still looks
        # like a fresh success. Revealing "already submitted" here would let
        # anyone probe this endpoint to check whether a given email has
        # already contacted us — logging it (masked) is enough for our own
        # visibility without exposing that to the requester.
        logger.info(f"Duplicate submission attempt for email: {mask_email(email)}")
    except Exception as e:
        logger.error(f"Failed to save submission for {mask_email(email)}: {e}")
        return f'<div class="text-red-600 p-4">Failed to save submission. Please try again later.</div>'

    return templates.TemplateResponse(
        request=request,
        name="contact_success.html",
        context={"name": name}
    )

