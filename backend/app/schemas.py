# backend/app/schemas.py

from pantic import BaseModel, EmailStr
from typing import Optional, List

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserInDB(UserBase):
    id: int
    onboarding_complete: bool

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class Message(BaseModel):
    message: str

# +++ Add the following new code +++
class QuestionBase(BaseModel):
    text: str
    company: Optional[str] = None
    category: Optional[str] = None
    complexity: Optional[str] = None
    experience_level: Optional[str] = None

class QuestionInDB(QuestionBase):
    id: int

    class Config:
        from_attributes = True
# +++ End of new code +++