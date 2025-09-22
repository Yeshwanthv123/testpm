from app.db import engine, Base
from app.models import User, InterviewSession, Question

print("Creating all database tables...")
Base.metadata.create_all(bind=engine)
print("Tables created successfully.")