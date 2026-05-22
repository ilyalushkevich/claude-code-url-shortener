import re
import uuid
from datetime import datetime

from pydantic import BaseModel, HttpUrl, field_validator


class ShortenRequest(BaseModel):
    url: HttpUrl
    custom_code: str | None = None
    expires_in_days: int | None = None

    @field_validator("custom_code")
    @classmethod
    def validate_custom_code(cls, v: str | None) -> str | None:
        if v is None:
            return v
        if not re.match(r"^[a-zA-Z0-9]{3,20}$", v):
            raise ValueError("Custom code must be 3–20 alphanumeric characters")
        return v

    @field_validator("expires_in_days")
    @classmethod
    def validate_expires_in_days(cls, v: int | None) -> int | None:
        if v is not None and v < 1:
            raise ValueError("expires_in_days must be at least 1")
        return v


class ShortenResponse(BaseModel):
    short_url: str
    short_code: str
    original_url: str
    expires_at: datetime | None

    model_config = {"from_attributes": True}


class LinkStats(BaseModel):
    id: uuid.UUID
    original_url: str
    short_code: str
    created_at: datetime
    expires_at: datetime | None
    clicks: int
    is_active: bool

    model_config = {"from_attributes": True}


class LinkList(BaseModel):
    items: list[LinkStats]
    total: int
    skip: int
    limit: int
