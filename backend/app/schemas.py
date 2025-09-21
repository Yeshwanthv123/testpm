from pydantic import BaseModel, EmailStr, Field
from typing import Optional
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)
    full_name: Optional[str] = None
class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str] = None
    class Config: from_attributes = True
class LoginRequest(BaseModel):
    email: EmailStr
    password: str
class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
class RefreshRequest(BaseModel):
    refresh_token: str
