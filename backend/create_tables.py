from app.database import engine, Base
# Import only the models that exist: User and Question
from app.models import User, Question

print("Creating all database tables...")
# This will create the 'users' and 'questions' tables.
Base.metadata.create_all(bind=engine)
print("Tables created successfully.")
