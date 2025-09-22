from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from .config import settings

# This line ensures the database URL is a string, which is required by create_engine
DATABASE_URL = str(settings.DATABASE_URL)

# This is the correct configuration for your engine
engine = create_engine(
    DATABASE_URL,
    # The connect_args are only needed for SQLite, this handles that safely
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# This creates the session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# This is the declarative base that your models will inherit from
class Base(DeclarativeBase):
    pass

# This is the dependency that your API routes will use to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()