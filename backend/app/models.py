from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Float
from .db import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    onboarding_complete = Column(Boolean, default=False)

class InterviewSession(Base):
    __tablename__ = "interview_sessions"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    session_date = Column(DateTime)
    score = Column(Float)

class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)
    company = Column(String, index=True)
    category = Column(String)
    complexity = Column(String)
    experience_level = Column(String)