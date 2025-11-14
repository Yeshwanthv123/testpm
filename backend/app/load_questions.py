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


def _map_years_to_bucket(s: Optional[str]) -> Optional[str]:
    """
    Map a raw Years of Experience value from CSV into one of the canonical
    buckets used by the app: "0-2", "3-5", "6-10", "10+".
    """
    if not s:
        return None
    t = str(s).strip().lower()
    # Common literal forms
    if t in ("0-2", "0-1", "1-2", "0-2 years", "0-1 years", "1-2 years"):
        return "0-2"
    if t in ("3-5", "2-3 years", "2-3", "2-3 years"):
        return "3-5"
    if t in ("3-5 years", "2-4", "2-4 years", "2-5", "2-5 years"):
        return "3-5"
    if t in ("5-8", "5-8 years", "5-8 yrs"):
        return "6-10"
    if t in ("6-10", "6-10 years"):
        return "6-10"
    if t in ("8 years", "8-10", "8-12", "8-10 years", "8-12 years"):
        return "6-10"
    if t.endswith("+"):
        # e.g., "10+", "12+"
        try:
            val = int(t[:-1])
            return "10+" if val >= 10 else ("6-10" if val >= 6 else ("3-5" if val >= 3 else "0-2"))
        except Exception:
            return "10+"
    # try parsing numeric range
    try:
        # remove words
        clean = t.replace("years", "").replace("year", "").replace("yrs", "").replace(" ", "")
        if "-" in clean:
            a, b = clean.split("-", 1)
            a_v = int(a)
            b_v = int(b)
            lo, hi = min(a_v, b_v), max(a_v, b_v)
            # determine overlap with buckets
            if hi <= 2:
                return "0-2"
            if lo <= 3 and hi <= 5:
                return "3-5"
            if lo <= 6 and hi <= 10:
                return "6-10"
            if lo >= 10 or hi > 10:
                return "10+"
    except Exception:
        pass
    # Fallback: check for digits
    import re
    m = re.search(r"(\d+)", t)
    if m:
        v = int(m.group(1))
        if v <= 2:
            return "0-2"
        if 3 <= v <= 5:
            return "3-5"
        if 6 <= v <= 10:
            return "6-10"
        return "10+"
    return None


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
                # Normalize years_of_experience to canonical buckets
                "years_of_experience": _map_years_to_bucket(_clean_str(row.get("Years of Experience"))),
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
