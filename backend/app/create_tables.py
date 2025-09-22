# backend/create_tables.py

from app.db import engine, Base
from app.models import Question # Import your new Question model class

print("Creating tables...")
# This command tells SQLAlchemy to create all tables that inherit from Base
Base.metadata.create_all(bind=engine)
print("Tables created successfully.")