from typing import Dict, List, Optional, Tuple, Any
import math
import random

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

# Adjust these imports only if your structure differs.
from ..database import get_db
from ..models import Question  # SQLAlchemy model

router = APIRouter(prefix="/interview", tags=["interview"])

# How many questions to return
TOTAL_QUESTIONS_TO_RETURN = 10

# ---- Role normalization ---------------------------------------------------- #

# Map UI role variants -> canonical labels used in your CSV's "Experience Level"
_ROLE_ALIASES: Dict[str, str] = {
    "apm": "APM",
    "associate pm": "APM",
    "product manager": "PM",
    "pm": "PM",
    "senior pm": "Senior PM",
    "sr pm": "Senior PM",
    "sr. pm": "Senior PM",
    "group pm": "Group PM",
    "gpm": "Group PM",
    "principal pm": "Principal PM",
    "pr. pm": "Principal PM",
    "director": "Director",
    "product director": "Director",
}

def normalize_role(role: Optional[str]) -> Optional[str]:
    if not role:
        return None
    key = role.strip().lower()
    return _ROLE_ALIASES.get(key, role.strip())

# ---- Experience parsing / matching ---------------------------------------- #

def _parse_range(token: str) -> Optional[Tuple[float, float]]:
    """
    Parse a 'Years of Experience' bucket like:
      '0-1 years', '1-2 years', '2-3', '3-5 years', '5-8', '8-10', '8-12', '12-20', '8+ years'
    Returns (lo, hi) with hi = math.inf for open-ended like '8+ years'.
    Returns None if unparsable.
    """
    if not token:
        return None
    t = token.strip().lower().replace("years", "").replace("year", "").replace("yrs", "").replace(" ", "")
    # common notations
    if t.endswith("+"):
        try:
            lo = float(t[:-1])
            return (lo, math.inf)
        except ValueError:
            return None
    if "+" in t and t.endswith("+years"):
        # in case '8+years' slipped through before replace
        try:
            lo = float(t.split("+", 1)[0])
            return (lo, math.inf)
        except ValueError:
            return None
    # ranged "a-b"
    if "-" in t:
        parts = t.split("-", 1)
        try:
            lo = float(parts[0])
            hi = float(parts[1])
            # Ensure proper ordering
            if hi < lo:
                lo, hi = hi, lo
            return (lo, hi)
        except ValueError:
            return None
    # single number '2'
    try:
        val = float(t)
        return (val, val)
    except ValueError:
        return None

def _desired_bucket_to_range(desired: str) -> Optional[Tuple[float, float]]:
    """
    UI typically sends '0-2', '2-4', '5-8', '8+'.
    Convert to numeric range.
    """
    if not desired:
        return None
    d = desired.strip().lower().replace(" ", "")
    if d.endswith("+"):
        try:
            lo = float(d[:-1])
            return (lo, math.inf)
        except ValueError:
            return None
    if "-" in d:
        a, b = d.split("-", 1)
        try:
            lo = float(a)
            hi = float(b)
            if hi < lo:
                lo, hi = hi, lo
            return (lo, hi)
        except ValueError:
            return None
    # Allow single number (rare)
    try:
        val = float(d)
        return (val, val)
    except ValueError:
        return None

def _ranges_overlap(a: Tuple[float, float], b: Tuple[float, float]) -> bool:
    """
    Returns True if numeric ranges a and b overlap.
    a, b are (lo, hi) where hi can be math.inf
    """
    (a_lo, a_hi), (b_lo, b_hi) = a, b
    return not (a_hi < b_lo or b_hi < a_lo)

def _experience_match(desired_bucket: Optional[str], row_bucket: Optional[str]) -> bool:
    """
    Decide if a DB row's 'Years of Experience' matches the desired UI bucket.
    If either is missing/unparsable, be lenient (return True) so we don't drop everything.
    """
    if not desired_bucket:
        return True  # no filter requested
    desired_range = _desired_bucket_to_range(desired_bucket)
    if desired_range is None:
        return True  # can't parse desired -> don't over-filter
    row_range = _parse_range(row_bucket or "")
    if row_range is None:
        # DB not normalized; accept to avoid empty results
        return True
    return _ranges_overlap(desired_range, row_range)

# ---- Company normalization ------------------------------------------------- #

def normalize_company(company: Optional[str]) -> Optional[str]:
    if not company:
        return None
    c = company.strip()
    return c if c else None

# ---- Serialization helper ------------------------------------------------- #

def _serialize_question(q: Any) -> Dict[str, Any]:
    """
    Make the response independent from Pydantic schemas to avoid import issues.
    Handles both q.text and q.question field names.
    """
    text = getattr(q, "text", None) or getattr(q, "question", None)
    return {
        "id": getattr(q, "id", None),
        "question": text,
        "company": getattr(q, "company", None),
        "category": getattr(q, "category", None),
        "complexity": getattr(q, "complexity", None),
        "experience_level": getattr(q, "experience_level", None),
        "years_of_experience": getattr(q, "years_of_experience", None),
    }

# ---- Core selection logic -------------------------------------------------- #

def _pick_questions(
    db: Session,
    company: Optional[str],
    role: Optional[str],
    experience: Optional[str],
    limit: int = TOTAL_QUESTIONS_TO_RETURN,
) -> List[Dict[str, Any]]:
    """
    Priority buckets:
      1) Exact: same company + same role (Experience Level) -> Python-filter by years overlap
      2) Company-only: same company (any role) -> filter by years
      3) Role-only: any company with same role -> filter by years
      4) Generic company fallback (company == 'Generic') with same role -> filter by years
      5) Absolute fallback: anything -> filter by years
    Dedup by id, then shuffle and cap at limit.
    """
    wanted_role = normalize_role(role)
    wanted_company = normalize_company(company)
    desired_experience = experience.strip() if experience else None

    results: List[Dict[str, Any]] = []
    seen_ids = set()

    def add_many(rows: List[Question]):
        for q in rows:
            if desired_experience and not _experience_match(desired_experience, getattr(q, "years_of_experience", None)):
                continue
            qid = getattr(q, "id", None)
            if qid in seen_ids:
                continue
            seen_ids.add(qid)
            results.append(_serialize_question(q))

    # 1) Exact: same company + same role
    if wanted_company and wanted_role:
        rows = (
            db.query(Question)
            .filter(
                and_(
                    Question.company == wanted_company,
                    Question.experience_level == wanted_role,
                )
            )
            .all()
        )
        add_many(rows)
        if len(results) >= limit:
            random.shuffle(results)
            return results[:limit]

    # 2) Company-only
    if wanted_company:
        rows = db.query(Question).filter(Question.company == wanted_company).all()
        add_many(rows)
        if len(results) >= limit:
            random.shuffle(results)
            return results[:limit]

    # 3) Role-only (any company)
    if wanted_role:
        rows = db.query(Question).filter(Question.experience_level == wanted_role).all()
        add_many(rows)
        if len(results) >= limit:
            random.shuffle(results)
            return results[:limit]

    # 4) Generic fallback (common pattern in your CSV)
    rows = db.query(Question).filter(Question.company == "Generic").all()
    add_many(rows)
    if len(results) >= limit:
        random.shuffle(results)
        return results[:limit]

    # 5) Absolute fallback: anything in table
    rows = db.query(Question).all()
    add_many(rows)

    random.shuffle(results)
    return results[:limit]

# ---- Public endpoint ------------------------------------------------------- #

@router.get("/questions")
def get_interview_questions(
    company: Optional[str] = Query(None, description="Preferred company (e.g., Google, Amazon)"),
    role: Optional[str] = Query(None, description="Role/level (e.g., APM, PM, Senior PM, Group PM, Director, Principal PM)"),
    experience: Optional[str] = Query(None, description="Experience bucket (e.g., 0-2, 2-4, 5-8, 8+)"),
    db: Session = Depends(get_db),
):
    """
    Returns up to 10 questions filtered by company/role/experience.
    Safe even if DB 'years_of_experience' is messy; it uses overlap logic.
    """
    try:
        data = _pick_questions(db, company, role, experience, limit=TOTAL_QUESTIONS_TO_RETURN)
        if not data:
            # Helpful error if DB is empty / CSV not loaded
            raise HTTPException(
                status_code=404,
                detail="No questions available. Make sure your CSV is loaded into the database."
            )
        return data
    except HTTPException:
        raise
    except Exception as exc:
        # Avoid leaking internals but provide actionable tip
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch interview questions. Please check database connectivity and CSV load. ({type(exc).__name__})"
        )
