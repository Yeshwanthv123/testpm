import pandas as pd
from app.db import SessionLocal
from app.models import Question
import os

# This path now correctly points to the CSV file inside the /app directory
CSV_PATH = '/app/PM_Questions_dedup.csv'

def load_data():
    db = SessionLocal()
    print(f"Reading data from {CSV_PATH}...")
    try:
        df = pd.read_csv(CSV_PATH)

        df['Company'] = df['Company'].replace({'(None)': 'Generic', None: 'Generic'})
        df.fillna({'Company': 'Generic', 'Category': '', 'Complexity': '', 'Experience Level': ''}, inplace=True)

        questions_to_add = []
        for _, row in df.iterrows():
            if not isinstance(row['Question'], str) or not row['Question'].strip():
                continue

            question_obj = Question(
                text=row['Question'],
                company=row['Company'],
                category=row['Category'],
                complexity=row['Complexity'],
                experience_level=row['Experience Level']
            )
            questions_to_add.append(question_obj)

        print(f"Found {len(questions_to_add)} questions to load.")

        if questions_to_add:
            db.bulk_save_objects(questions_to_add)
            db.commit()
            print("Successfully loaded questions into the database.")
        else:
            print("No questions to load.")

    except FileNotFoundError:
        print(f"Error: The file {CSV_PATH} was not found inside the container.")
    finally:
        db.close()

if __name__ == "__main__":
    load_data()