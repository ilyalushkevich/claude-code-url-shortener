from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.config import settings
from app.database import get_db

router = APIRouter(tags=["web"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def home(
    request: Request,
    db: AsyncSession = Depends(get_db),
    msg: str | None = None,
    error: str | None = None,
):
    links, _ = await crud.get_links(db, skip=0, limit=20)
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "links": links,
            "base_url": settings.BASE_URL,
            "msg": msg,
            "error": error,
        },
    )


@router.post("/", response_class=HTMLResponse)
async def home_post(
    request: Request,
    url: str = Form(...),
    custom_code: str = Form(""),
    expires_in_days: str = Form(""),
    db: AsyncSession = Depends(get_db),
):
    import re

    error = None
    msg = None

    if not url.startswith(("http://", "https://")):
        error = "URL must start with http:// or https://"
    elif custom_code and not re.match(r"^[a-zA-Z0-9]{3,20}$", custom_code):
        error = "Custom code must be 3–20 alphanumeric characters"
    else:
        try:
            code = custom_code.strip() or None
            days = int(expires_in_days.strip()) if expires_in_days.strip() else None

            if code:
                existing = await crud.get_link_by_code(db, code)
                if existing:
                    error = f"Short code '{code}' is already taken"

            if not error:
                link = await crud.create_link(db, original_url=url, custom_code=code, expires_in_days=days)
                msg = f"Short link created: {settings.BASE_URL}/{link.short_code}"
        except Exception as e:
            error = str(e)

    links, _ = await crud.get_links(db, skip=0, limit=20)
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "links": links,
            "base_url": settings.BASE_URL,
            "msg": msg,
            "error": error,
        },
    )


@router.get("/stats/{short_code}", response_class=HTMLResponse)
async def stats_page(request: Request, short_code: str, db: AsyncSession = Depends(get_db)):
    link = await crud.get_link_by_code(db, short_code)
    if not link:
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "links": [], "base_url": settings.BASE_URL, "error": "Link not found"},
            status_code=404,
        )
    return templates.TemplateResponse(
        "stats.html",
        {
            "request": request,
            "link": link,
            "base_url": settings.BASE_URL,
            "is_valid": crud.is_link_valid(link),
        },
    )


@router.post("/delete/{short_code}")
async def web_delete(short_code: str, db: AsyncSession = Depends(get_db)):
    await crud.deactivate_link(db, short_code)
    return RedirectResponse(url="/?msg=Link+deactivated", status_code=303)


@router.get("/{short_code}")
async def redirect(short_code: str, db: AsyncSession = Depends(get_db)):
    link = await crud.get_link_by_code(db, short_code)
    if not link or not crud.is_link_valid(link):
        return RedirectResponse(url="/?error=Link+not+found+or+expired", status_code=302)
    await crud.increment_clicks(db, link)
    return RedirectResponse(url=link.original_url, status_code=301)
