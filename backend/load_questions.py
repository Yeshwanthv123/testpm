import os
import csv
import math
from typing import Dict, Iterable, Optional, Tuple, List, Set

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
      - ./PM_Questions_dedup.csv
      - ../PM_Questions_dedup.csv
      - /app/PM_Questions_dedup.csv
    """
    env_path = os.getenv("PM_QUESTIONS_CSV")
    candidates = [
        env_path,
        os.path.join(os.getcwd(), "PM_Questions_dedup.csv"),
        os.path.join(os.path.dirname(os.getcwd()), "PM_Questions_dedup.csv"),
        "/app/PM_Questions_dedup.csv",
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
    rng = _parse_range(raw or "")
    if rng is None:
        return raw  # keep whatever was there; router is lenient if unparsable

    lo, hi = rng
    # Normalize infinities/singletons into buckets by overlap
    def overlaps(a: Tuple[float, float], b: Tuple[float, float]) -> bool:
        (a_lo, a_hi), (b_lo, b_hi) = a, b
        return not (a_hi < b_lo or b_hi < a_lo)

    canonical_buckets = [
        ((0.0, 1.0), "0-1 years"),
        ((1.0, 2.0), "1-2 years"),
        ((2.0, 3.0), "2-3 years"),
        ((3.0, 5.0), "3-5 years"),
        ((5.0, 8.0), "5-8 years"),
        ((8.0, math.inf), "8+ years"),
    ]

    for (blo, bhi), label in canonical_buckets:
        if overlaps((lo, hi), (blo, bhi)):
            return label
    # Fallback: keep original string
    return raw


# ------------------------------ Core Loader -------------------------------- #

def _model_columns() -> Set[str]:
    """Get real column names on Question so we only pass valid fields."""
    return {c.name for c in Question.__table__.columns}  # type: ignore[attr-defined]


def _row_to_kwargs(row: Dict[str, str], model_cols: Set[str]) -> Dict[str, str]:
    """
    Map CSV columns to model fields, only including keys that actually exist
    in the Question model (so we don't break if your column is 'text' vs 'question').
    """
    question_text = _clean_str(row.get("Question"))
    company = _clean_str(row.get("Company")) or "Generic"
    category = _clean_str(row.get("Category"))
    complexity = _clean_str(row.get("Complexity"))
    exp_level = _normalize_role(_clean_str(row.get("Experience Level")))
    yoexp = _canonicalize_years(_clean_str(row.get("Years of Experience")))

    data = {
        "company": company,
        "category": category,
        "complexity": complexity,
        "experience_level": exp_level,
        "years_of_experience": yoexp,
    }

    # Handle text field name difference
    if "text" in model_cols:
        data["text"] = question_text
    elif "question" in model_cols:
        data["question"] = question_text

    # Only keep keys that are actual model columns
    return {k: v for k, v in data.items() if k in model_cols}


def load_questions_from_csv(db: Session, csv_path: Optional[str] = None) -> Dict[str, int]:
    """
    Load/replace questions from CSV into DB.
    Returns stats: {'read': N, 'inserted': M, 'skipped': D}
    """
    path = csv_path or _infer_csv_path()
    if not path or not os.path.isfile(path):
        raise FileNotFoundError(
            f"Questions CSV not found. Looked for PM_Questions_dedup.csv; "
            f"set PM_QUESTIONS_CSV or place the file in backend/ (current: {os.getcwd()})"
        )

    model_cols = _model_columns()
    seen: Set[Tuple] = set()
    to_insert: List[Question] = []

    read_count = 0
    skip_count = 0

    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        # Validate headers minimally
        required = {"Question", "Company", "Category", "Complexity", "Experience Level", "Years of Experience"}
        missing = required.difference(set(reader.fieldnames or []))
        if missing:
            raise ValueError(f"CSV missing required columns: {', '.join(sorted(missing))}")

        for row in reader:
            read_count += 1
            kwargs = _row_to_kwargs(row, model_cols)

            # Must have a non-empty question text (under 'text' or 'question')
            qtext = kwargs.get("text") or kwargs.get("question")
            if not qtext:
                skip_count += 1
                continue

            # Deduplicate on key fields present in the model
            dedupe_key = (
                (kwargs.get("text") or kwargs.get("question")),
                kwargs.get("company"),
                kwargs.get("category"),
                kwargs.get("complexity"),
                kwargs.get("experience_level"),
                kwargs.get("years_of_experience"),
            )
            if dedupe_key in seen:
                skip_count += 1
                continue
            seen.add(dedupe_key)

            to_insert.append(Question(**kwargs))

    # Replace contents atomically
    # (If you prefer append-only, remove the delete)
    db.query(Question).delete()
    if to_insert:
        db.add_all(to_insert)
    db.commit()

    return {"read": read_count, "inserted": len(to_insert), "skipped": skip_count}


# ------------------------------ CLI entrypoint ------------------------------ #

if __name__ == "__main__":
    """
    Allow: `python -m backend.load_questions` from project root (in Docker or locally).
    Optionally set PM_QUESTIONS_CSV=/path/to/PM_Questions_dedup.csv
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
