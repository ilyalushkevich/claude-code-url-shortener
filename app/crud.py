import random
import string
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Link


def _generate_code(length: int = 6) -> str:
    chars = string.ascii_letters + string.digits
    return "".join(random.choices(chars, k=length))


async def get_link_by_code(db: AsyncSession, short_code: str) -> Link | None:
    result = await db.execute(select(Link).where(Link.short_code == short_code))
    return result.scalar_one_or_none()


async def create_link(
    db: AsyncSession,
    original_url: str,
    custom_code: str | None = None,
    expires_in_days: int | None = None,
) -> Link:
    if custom_code:
        short_code = custom_code
    else:
        for _ in range(10):
            candidate = _generate_code()
            existing = await get_link_by_code(db, candidate)
            if not existing:
                short_code = candidate
                break
        else:
            raise RuntimeError("Failed to generate a unique short code after 10 attempts")

    expires_at = None
    if expires_in_days:
        expires_at = datetime.now(timezone.utc) + timedelta(days=expires_in_days)

    link = Link(original_url=original_url, short_code=short_code, expires_at=expires_at)
    db.add(link)
    await db.commit()
    await db.refresh(link)
    return link


async def get_links(db: AsyncSession, skip: int = 0, limit: int = 20) -> tuple[list[Link], int]:
    count_result = await db.execute(select(func.count()).select_from(Link))
    total = count_result.scalar_one()

    result = await db.execute(
        select(Link).order_by(Link.created_at.desc()).offset(skip).limit(limit)
    )
    links = list(result.scalars().all())
    return links, total


async def increment_clicks(db: AsyncSession, link: Link) -> None:
    await db.execute(
        update(Link).where(Link.id == link.id).values(clicks=Link.clicks + 1)
    )
    await db.commit()


async def deactivate_link(db: AsyncSession, short_code: str) -> Link | None:
    link = await get_link_by_code(db, short_code)
    if not link:
        return None
    await db.execute(
        update(Link).where(Link.id == link.id).values(is_active=False)
    )
    await db.commit()
    await db.refresh(link)
    return link


def is_link_valid(link: Link) -> bool:
    if not link.is_active:
        return False
    if link.expires_at and link.expires_at < datetime.now(timezone.utc):
        return False
    return True
