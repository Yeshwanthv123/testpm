#!/bin/sh

# In a real-world scenario, you'd want a more robust way to check if the DB is ready.
# For this example, a simple sleep will suffice.
echo "Waiting for postgres..."
sleep 5

echo "Creating database tables..."
python create_tables.py

echo "Loading questions..."
python load_questions.py

echo "Starting server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000