from pydantic import BaseModel, EmailStr
from typing import Optional, List

# New schema for handling JSON login requests
class UserLogin(BaseModel):
    email: EmailStr
    password: str

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