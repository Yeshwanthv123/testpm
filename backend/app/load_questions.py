import os
import csv
import math
from typing import Dict, Optional, Tuple, List, Set

from sqlalchemy.orm import Session

# Import your app's DB and model (do not change these module paths)
from app.database import SessionLocal
from app.models import Question


# ------------------------------ Utilities ---------------------------------- #

def _infer_csv_path() -> Optional[str]:
    env_path = os.getenv("PM_QUESTIONS_CSV")
    candidates = [
        env_path,
        os.path.join(os.getcwd(), "PM_Questions_FINAL_12x2000_Formatted_Final_HUMANIZED.csv"),
        os.path.join(os.path.dirname(os.getcwd()), "PM_Questions_FINAL_12x2000_Formatted_Final_HUMANIZED.csv"),
        "/app/PM_Questions_FINAL_12x2000_Formatted_Final_HUMANIZED.csv",
    ]
    for p in candidates:
        if p and os.path.isfile(p):
            return p
    return None


def _clean_str(s: Optional[str]) -> Optional[str]:
    if s is None:
        return None
    t = str(s).strip()
    return t if t else None


def load_questions_from_csv(db: Session, csv_path: Optional[str] = None) -> Dict[str, int]:
    path = csv_path or _infer_csv_path()
    if not path or not os.path.isfile(path):
        raise FileNotFoundError(f"Questions CSV not found (looked for {path})")

    # Load from new CSV with experience_level and years_of_experience columns
    model_cols = {c.name for c in Question.__table__.columns}
    to_insert: List[Question] = []
    read_count = 0
    skip_count = 0

    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            read_count += 1
            question_text = _clean_str(row.get("Question"))
            if not question_text:
                skip_count += 1
                continue
            
            data = {
                "company": _clean_str(row.get("Company")) or "Generic",
                "category": _clean_str(row.get("Category")),
                "complexity": _clean_str(row.get("Complexity")),
                "experience_level": _clean_str(row.get("Experience Level")),
                "years_of_experience": _clean_str(row.get("Years of Experience")),
            }
            
            if "text" in model_cols:
                data["text"] = question_text
            elif "question" in model_cols:
                data["question"] = question_text
            
            to_insert.append(Question(**{k: v for k, v in data.items() if k in model_cols}))

    db.query(Question).delete()
    if to_insert:
        db.add_all(to_insert)
    db.commit()

    return {"read": read_count, "inserted": len(to_insert), "skipped": skip_count}


if __name__ == "__main__":
    session = SessionLocal()
    try:
        stats = load_questions_from_csv(session, None)
        print(f"Loaded questions. Read={stats['read']}, Inserted={stats['inserted']}, Skipped={stats['skipped']}")
    finally:
        session.close()
