from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func

# Reuse your project-wide Base
from app.database import Base


# ------------------------- User (kept minimal/safe) ------------------------- #
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    # Typical identity fields; kept nullable=False only for email to match common patterns
    email = Column(String(320), unique=True, index=True, nullable=False)
    hashed_password = Column(String(512), nullable=True)

    is_active = Column(Boolean, nullable=False, server_default="1")
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email!r}>"


# ---------------------------- Question (core) ------------------------------- #
class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)

    # Support either column name used by different parts of the codebase.
    # Your loader will populate 'text' if present, otherwise 'question'.
    text = Column(Text, nullable=True)       # preferred canonical field
    question = Column(Text, nullable=True)   # legacy/alternate field

    company = Column(String(128), index=True, nullable=True)  # e.g., "Google", "Generic"
    category = Column(String(128), index=True, nullable=True) # e.g., "System Design", "Behavioral"
    complexity = Column(String(64), nullable=True)            # e.g., "easy", "medium", "hard"
    experience_level = Column(String(64), index=True, nullable=True)  # e.g., "APM", "PM", "Senior PM"
    years_of_experience = Column(String(64), index=True, nullable=True)  # e.g., "0-1 years", "5-8 years", "8+ years"

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    def __repr__(self) -> str:
        t = (self.text or self.question or "").strip()
        short = (t[:37] + "…") if len(t) > 38 else t
        return f"<Question id={self.id} company={self.company!r} level={self.experience_level!r} yoexp={self.years_of_experience!r} text={short!r}>"
