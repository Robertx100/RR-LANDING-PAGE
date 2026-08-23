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
    link: Annotated[str, Form()],
    constraint: Annotated[Optional[str], Form()] = None,
    fix_attempt: Annotated[Optional[str], Form()] = None,
    performance_gap: Annotated[Optional[str], Form()] = None,
    impact_bottleneck: Annotated[Optional[str], Form()] = None,
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

    submission_data = {
        "name": name,
        "email": email,
        "link": link,
        "constraint": constraint.strip() if constraint else None,
        "fix_attempt": fix_attempt.strip() if fix_attempt else None,
        "performance_gap": performance_gap.strip() if performance_gap else None,
        "impact_bottleneck": impact_bottleneck.strip() if impact_bottleneck else None,
    }

    try:
        await save_contact_submission(db, submission_data)
        logger.info(f"Submission saved for email: {mask_email(email)}")

        return templates.TemplateResponse(
            request=request, 
            name="contact_success.html", 
            context={"name": name}
        )
    except ValueError as ve:
        logger.warning(f"Validation error for {mask_email(email)}: {ve}")
        return f'<div class="text-red-600 p-4">{str(ve)}</div>'
    except Exception as e:
        logger.error(f"Failed to save submission for {mask_email(email)}: {e}")
        return f'<div class="text-red-600 p-4">Failed to save submission. Please try again later.</div>'

