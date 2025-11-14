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
    """
    Try sensible defaults so you don't have to pass a path every time.
    Checks (in order):
      - ENV PM_QUESTIONS_CSV
      - ./PM_Questions_dedup_final_clean.csv
      - ./PM_Questions_dedup.csv
      - ../PM_Questions_dedup_final_clean.csv
      - ../PM_Questions_dedup.csv
      - /app/PM_Questions_dedup_final_clean.csv
      - /app/PM_Questions_dedup.csv
    """
    env_path = os.getenv("PM_QUESTIONS_CSV")
    # Prefer the final humanized CSV if present, otherwise fall back to env or older names
    candidates = [
        env_path,
        os.path.join(os.getcwd(), "PM_Questions_FINAL_12x2000_Formatted_Final_HUMANIZED.csv"),
        os.path.join(os.path.dirname(os.getcwd()), "PM_Questions_FINAL_12x2000_Formatted_Final_HUMANIZED.csv"),
        os.path.join(os.getcwd(), "PM_Questions_dedup_final_clean.csv"),
        os.path.join(os.getcwd(), "PM_Questions_dedup.csv"),
        os.path.join(os.path.dirname(os.getcwd()), "PM_Questions_dedup_final_clean.csv"),
        os.path.join(os.path.dirname(os.getcwd()), "PM_Questions_dedup.csv"),
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


# ---- Role normalization (Experience Level) -------------------------------- #

# Canonical labels we expect in DB
_CANON_ROLES = {
    "APM": {"apm", "associate product manager", "associate pm"},
    "PM": {"pm", "product manager"},
    "Senior PM": {"senior pm", "sr pm", "sr. pm", "senior product manager"},
    "Group PM": {"group pm", "gpm"},
    "Principal PM": {"principal pm", "pr. pm", "principal product manager"},
    "Director": {"director", "product director"},
}

def _normalize_role(raw: Optional[str]) -> Optional[str]:
    if not raw:
        return None
    key = raw.strip().lower()
    for canon, variants in _CANON_ROLES.items():
        if key == canon.lower() or key in variants:
            return canon
    # If it's already something standard-looking, keep it as-is
    return raw.strip()


# ---- Years-of-experience normalization ------------------------------------ #

def _parse_range(token: str) -> Optional[Tuple[float, float]]:
    """
    Parse free-form ranges like:
      '0-1 years', '1-2 years', '2-3', '3-5 years', '5-8', '8-10', '8-12', '12-20', '8+ years', '8+'
    Returns (lo, hi) with hi=math.inf for open-ended buckets.
    """
    if not token:
        return None
    t = token.strip().lower()
    t = (
        t.replace("years", "")
         .replace("year", "")
         .replace("yrs", "")
         .replace(" ", "")
    )
    if not t:
        return None

    if t.endswith("+"):
        try:
            lo = float(t[:-1])
            return (lo, math.inf)
        except ValueError:
            return None

    if "-" in t:
        a, b = t.split("-", 1)
        try:
            lo = float(a)
            hi = float(b)
            if hi < lo:
                lo, hi = hi, lo
            return (lo, hi)
        except ValueError:
            return None

    # Single number case
    try:
        v = float(t)
        return (v, v)
    except ValueError:
        return None


def _canonicalize_years(raw: Optional[str]) -> Optional[str]:
    """
    Map many CSV variants to a small canonical set we use in filtering:
      '0-1 years', '1-2 years', '2-3 years', '3-5 years', '5-8 years', '8+ years'
    Heuristic mapping for wide ranges:
      - anything overlapping 0..1.0  -> '0-1 years'
      - 1..2  -> '1-2 years'
      - 2..3  -> '2-3 years'
      - 3..5  -> '3-5 years'
      - 5..8  -> '5-8 years'
      - 8+    -> '8+ years'
    """
    # Map many CSV variants into the canonical buckets used by the app:
    #   "0-2", "3-5", "6-10", "10+"
    rng = _parse_range(raw or "")
    if rng is None:
        # try simple textual mappings
        if not raw:
            return None
        t = raw.strip().lower()
        if t in ("0-2", "0-1", "1-2"):
            return "0-2"
        if t in ("3-5", "2-3", "2-4", "2-5"):
            return "3-5"
        if t in ("5-8", "6-10", "8-10"):
            return "6-10"
        if t.endswith("+"):
            return "10+"
        return raw

    lo, hi = rng
    # Determine which canonical bucket the parsed range overlaps
    def overlaps(a: Tuple[float, float], b: Tuple[float, float]) -> bool:
        (a_lo, a_hi), (b_lo, b_hi) = a, b
        return not (a_hi < b_lo or b_hi < a_lo)

    canonical_buckets = [
        ((0.0, 2.0), "0-2"),
        ((3.0, 5.0), "3-5"),
        ((6.0, 10.0), "6-10"),
        ((10.0, math.inf), "10+"),
    ]

    for (blo, bhi), label in canonical_buckets:
        if overlaps((lo, hi), (blo, bhi)):
            return label

    # Fallback using midpoint
    mid = (lo + (hi if hi != math.inf else lo + 10)) / 2.0
    if mid <= 2:
        return "0-2"
    if mid <= 5:
        return "3-5"
    if mid <= 10:
        return "6-10"
    return "10+"


# ------------------------------ Core Loader -------------------------------- #

def _model_columns() -> Set[str]:
    """Get real column names on Question so we only pass valid fields."""
    return {c.name for c in Question.__table__.columns}  # type: ignore[attr-defined]


def _split_companies(raw: Optional[str]) -> List[str]:
    """Split a CSV Company cell like 'Google, Meta, Amazon' into normalized company names."""
    if not raw:
        return []
    parts = [p.strip() for p in str(raw).split(",")]
    return [p for p in parts if p]


def load_questions_from_csv(db: Session, csv_path: Optional[str] = None) -> Dict[str, int]:
    """
    Load/replace questions from CSV into DB.
    Expands multi-company rows into one DB row per company.
    Returns stats: {'read': N, 'inserted': M, 'skipped': D}
    """
    path = csv_path or _infer_csv_path()
    if not path or not os.path.isfile(path):
        raise FileNotFoundError(
            f"Questions CSV not found. Looked for PM_Questions_dedup_final_clean.csv/PM_Questions_dedup.csv; "
            f"set PM_QUESTIONS_CSV or place the file in backend/ (current: {os.getcwd()})"
        )

    model_cols = _model_columns()
    seen: Set[Tuple] = set()
    to_insert: List[Question] = []

    read_count = 0
    skip_count = 0

    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        required = {"Question", "Company", "Category", "Complexity", "Experience Level", "Years of Experience"}
        missing = required.difference(set(reader.fieldnames or []))
        if missing:
            raise ValueError(f"CSV missing required columns: {', '.join(sorted(missing))}")

        for row in reader:
            read_count += 1

            question_text = _clean_str(row.get("Question"))
            company_cell  = _clean_str(row.get("Company")) or "Generic"
            category      = _clean_str(row.get("Category"))
            complexity    = _clean_str(row.get("Complexity"))
            exp_level     = _normalize_role(_clean_str(row.get("Experience Level")))
            yoexp         = _canonicalize_years(_clean_str(row.get("Years of Experience")))

            if not question_text:
                skip_count += 1
                continue

            companies = _split_companies(company_cell)
            if not companies:
                companies = ["Generic"]

            for company in companies:
                data = {
                    "company": company,
                    "category": category,
                    "complexity": complexity,
                    "experience_level": exp_level,
                    "years_of_experience": yoexp,
                }
                # text vs question column name
                if "text" in model_cols:
                    data["text"] = question_text
                elif "question" in model_cols:
                    data["question"] = question_text

                # Deduplicate per (text|question, company, ...)
                dedupe_key = (
                    (data.get("text") or data.get("question")),
                    data.get("company"),
                    data.get("category"),
                    data.get("complexity"),
                    data.get("experience_level"),
                    data.get("years_of_experience"),
                )
                if dedupe_key in seen:
                    skip_count += 1
                    continue
                seen.add(dedupe_key)

                to_insert.append(Question(**{k: v for k, v in data.items() if k in model_cols}))

    # Replace contents atomically
    db.query(Question).delete()
    if to_insert:
        db.add_all(to_insert)
    db.commit()

    return {"read": read_count, "inserted": len(to_insert), "skipped": skip_count}


# ------------------------------ CLI entrypoint ------------------------------ #

if __name__ == "__main__":
    """
    Allow: `python -m backend.load_questions` from project root (in Docker or locally).
    Optionally set PM_QUESTIONS_CSV=/path/to/PM_Questions_dedup_final_clean.csv
    """
    session = SessionLocal()
    try:
        stats = load_questions_from_csv(session, None)
        print(
            f"Loaded questions. Read={stats['read']}, Inserted={stats['inserted']}, "
            f"Skipped (dupes/invalid)={stats['skipped']}"
        )
    finally:
        session.close()
