from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.config import settings
from app.database import get_db
from app.schemas import LinkList, LinkStats, ShortenRequest, ShortenResponse

router = APIRouter(prefix="/api", tags=["api"])


@router.post("/shorten", response_model=ShortenResponse, status_code=status.HTTP_201_CREATED)
async def shorten_url(payload: ShortenRequest, db: AsyncSession = Depends(get_db)):
    if payload.custom_code:
        existing = await crud.get_link_by_code(db, payload.custom_code)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Short code '{payload.custom_code}' is already taken",
            )

    link = await crud.create_link(
        db,
        original_url=str(payload.url),
        custom_code=payload.custom_code,
        expires_in_days=payload.expires_in_days,
    )

    return ShortenResponse(
        short_url=f"{settings.BASE_URL}/{link.short_code}",
        short_code=link.short_code,
        original_url=link.original_url,
        expires_at=link.expires_at,
    )


@router.get("/links", response_model=LinkList)
async def list_links(skip: int = 0, limit: int = 20, db: AsyncSession = Depends(get_db)):
    if limit > 100:
        limit = 100
    links, total = await crud.get_links(db, skip=skip, limit=limit)
    return LinkList(
        items=[LinkStats.model_validate(link) for link in links],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/links/{short_code}/stats", response_model=LinkStats)
async def link_stats(short_code: str, db: AsyncSession = Depends(get_db)):
    link = await crud.get_link_by_code(db, short_code)
    if not link:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Link not found")
    return LinkStats.model_validate(link)


@router.delete("/links/{short_code}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_link(short_code: str, db: AsyncSession = Depends(get_db)):
    link = await crud.deactivate_link(db, short_code)
    if not link:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Link not found")
