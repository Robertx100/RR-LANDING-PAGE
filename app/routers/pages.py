from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, Response
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/robots.txt", response_class=Response)
async def get_robots():
    robots_content = """User-agent: *
Allow: /
Sitemap: https://reallyrobert.com/sitemap.xml
"""
    return Response(content=robots_content, media_type="text/plain")

@router.get("/sitemap.xml", response_class=Response)
async def get_sitemap():
    sitemap_content = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>https://reallyrobert.com/</loc>
        <changefreq>monthly</changefreq>
        <priority>1.0</priority>
    </url>
</urlset>"""
    return Response(content=sitemap_content, media_type="application/xml")

@router.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(
        request=request, name="index.html", context={"title": "reallyrobert.com | Financial Efficiency Consulting"}
    )

@router.get("/consultation", response_class=HTMLResponse)
async def get_consultation(request: Request):
    return templates.TemplateResponse(request=request, name="consultation.html")

@router.get("/hero-cta", response_class=HTMLResponse)
async def get_hero_cta(request: Request):
    return templates.TemplateResponse(request=request, name="hero_cta.html")

@router.get("/service-explainer/{service_name}", response_class=HTMLResponse)
async def get_service_explainer(request: Request, service_name: str):
    return templates.TemplateResponse(
        request=request, 
        name="service_explainer.html", 
        context={"service_name": service_name.replace("-", " ").title()}
    )
