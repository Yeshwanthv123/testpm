# backend/app/schemas.py
from datetime import datetime
from typing import Optional

# Pydantic v1/v2 compatibility layer
try:
    from pydantic import BaseModel, Field, ConfigDict  # v2
    _PD_V2 = True
except Exception:  # pragma: no cover
    from pydantic import BaseModel, Field  # type: ignore
    _PD_V2 = False
    ConfigDict = None  # type: ignore


class _FromORMMixin(BaseModel):
    """
    Works with both Pydantic v1 (Config.orm_mode) and v2 (model_config.from_attributes).
    """
    if _PD_V2:
        model_config = ConfigDict(from_attributes=True)  # type: ignore
    else:  # v1
        class Config:
            orm_mode = True


# ------------------------------ Auth Schemas ------------------------------ #

class Token(_FromORMMixin):
    access_token: str
    token_type: str = "bearer"


class TokenData(_FromORMMixin):
    user_id: Optional[int] = None
    email: Optional[str] = None


# ------------------------------ User Schemas ------------------------------ #

class UserBase(_FromORMMixin):
    email: str = Field(..., max_length=320)


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=512)


class UserUpdate(_FromORMMixin):
    email: Optional[str] = Field(None, max_length=320)
    password: Optional[str] = Field(None, min_length=6, max_length=512)
    is_active: Optional[bool] = None


class UserOut(UserBase):
    id: int
    is_active: bool = True
    created_at: datetime


# ---------------------------- Question Schemas ---------------------------- #

class QuestionOut(_FromORMMixin):
    id: Optional[int] = None

    # Support either DB column name; your code can read 'question' safely.
    # (The router already normalizes, but we keep this schema for completeness.)
    question: Optional[str] = None
    text: Optional[str] = None  # present in DB; clients should prefer 'question' if available

    company: Optional[str] = None
    category: Optional[str] = None
    complexity: Optional[str] = None
    experience_level: Optional[str] = None
    years_of_experience: Optional[str] = None
    created_at: Optional[datetime] = None
