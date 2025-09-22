    # backend/app/models.py

import sqlalchemy
from .db import metadata


User = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("email", sqlalchemy.String, unique=True, index=True),
    sqlalchemy.Column("hashed_password", sqlalchemy.String),
    sqlalchemy.Column("full_name", sqlalchemy.String),
    sqlalchemy.Column("is_active", sqlalchemy.Boolean, default=True),
    sqlalchemy.Column("onboarding_complete", sqlalchemy.Boolean, default=False),
)


InterviewSession = sqlalchemy.Table(
    "interview_sessions",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("user_id", sqlalchemy.ForeignKey("users.id")),
    sqlalchemy.Column("session_date", sqlalchemy.DateTime),
    sqlalchemy.Column("score", sqlalchemy.Float),
    # Add other relevant fields
)

# +++ Add the following new code +++
Question = sqlalchemy.Table(
    "questions",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("text", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("company", sqlalchemy.String, index=True),
    sqlalchemy.Column("category", sqlalchemy.String),
    sqlalchemy.Column("complexity", sqlalchemy.String),
    sqlalchemy.Column("experience_level", sqlalchemy.String),
)
# +++ End of new code +++