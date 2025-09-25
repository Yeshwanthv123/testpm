from typing import Dict, List, Optional, Tuple, Any
import math
import random
import re
from datetime import timedelta, datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, not_

from ..database import get_db
from ..models import Question, ServedQuestion

router = APIRouter(prefix="/interview", tags=["interview"])

# How many questions to return each time
TOTAL_QUESTIONS_TO_RETURN = 10
# Avoid repeating questions for the same browser session for N days
NO_REPEAT_DAYS_DEFAULT = 90

# ---------------- Role normalization ---------------- #

_ROLE_ALIASES: Dict[str, str] = {
    "apm": "APM", "associate pm": "APM", "product manager": "PM", "pm": "PM",
    "senior pm": "Senior PM", "sr pm": "Senior PM", "sr. pm": "Senior PM",
    "group pm": "Group PM", "gpm": "Group PM",
    "principal pm": "Principal PM", "pr. pm": "Principal PM",
    "director": "Director", "product director": "Director",
}
def normalize_role(role: Optional[str]) -> Optional[str]:
    if not role:
        return None
    key = role.strip().lower()
    return _ROLE_ALIASES.get(key, role.strip())

# -------------- Experience matching --------------- #

def _parse_range(token: str) -> Optional[Tuple[float, float]]:
    if not token:
        return None
    t = token.strip().lower().replace("years","").replace("year","").replace("yrs","").replace(" ","")
    if t.endswith("+"):
        try:
            return (float(t[:-1]), math.inf)
        except ValueError:
            return None
    if "-" in t:
        a, b = t.split("-", 1)
        try:
            lo, hi = float(a), float(b)
            if hi < lo: lo, hi = hi, lo
            return (lo, hi)
        except ValueError:
            return None
    try:
        v = float(t)
        return (v, v)
    except ValueError:
        return None

def _desired_bucket_to_range(desired: str) -> Optional[Tuple[float, float]]:
    if not desired:
        return None
    d = desired.strip().lower().replace(" ", "")
    if d.endswith("+"):
        try:
            return (float(d[:-1]), math.inf)
        except ValueError:
            return None
    if "-" in d:
        a, b = d.split("-", 1)
        try:
            lo, hi = float(a), float(b)
            if hi < lo: lo, hi = hi, lo
            return (lo, hi)
        except ValueError:
            return None
    try:
        v = float(d)
        return (v, v)
    except ValueError:
        return None

def _ranges_overlap(a: Tuple[float, float], b: Tuple[float, float]) -> bool:
    (a_lo, a_hi), (b_lo, b_hi) = a, b
    return not (a_hi < b_lo or b_hi < a_lo)

def _experience_match(desired_bucket: Optional[str], row_bucket: Optional[str]) -> bool:
    if not desired_bucket:
        return True
    desired = _desired_bucket_to_range(desired_bucket)
    if desired is None:
        return True
    row = _parse_range(row_bucket or "")
    if row is None:
        return True
    return _ranges_overlap(desired, row)

# -------------- Company normalization --------------- #

def normalize_company(company: Optional[str]) -> Optional[str]:
    if not company:
        return None
    c = company.strip()
    return c if c else None

# -------------- Brand sanitizer + skills --------------- #

_BRAND_TOKENS = [
    # your 12
    "Google","Meta","Amazon","Microsoft","Apple","Netflix","Uber",
    "Salesforce","Freshworks","Zoho","Stripe","Airbnb",
    # common legacy brand tokens still appearing in text
    "Spotify","Square","Twilio","Atlassian","Slack","LinkedIn","Tesla","Dropbox","HubSpot","Adobe","Shopify",
    # sub-brands / product names
    "Instagram","Facebook","WhatsApp","Threads","Messenger","YouTube","Android","Chrome","Gmail",
    "App Store","iOS","Azure","Office","Teams","AWS","Prime","Kindle",
    "Freshdesk","Freshservice","Freshsales","Zoho CRM","Zoho Books","Zoho Mail"
]
_SANITIZE_RE = re.compile(
    r"\b(" + "|".join(re.escape(t) for t in sorted(_BRAND_TOKENS, key=len, reverse=True)) + r")\b",
    flags=re.IGNORECASE
)

def _normalize_prompt_brand(text: str, sanitize_to: Optional[str]) -> str:
    """Replace any known brand token in text with sanitize_to (selected company or 'our company')."""
    if not text or not sanitize_to:
        return text or ""
    return _SANITIZE_RE.sub(sanitize_to, text)

_CATEGORY_TO_SKILLS = {
    "strategic": ["Strategy","Prioritization","Business Acumen"],
    "strategy":  ["Strategy","Prioritization","Business Acumen"],
    "leadership": ["Leadership","Stakeholder Mgmt","Communication"],
    "metrics":   ["Metrics","Analysis","Decision-making"],
    "product health": ["Metrics","Product Health","Diagnostics"],
    "growth":    ["Growth","Experimentation","Retention"],
    "a/b testing": ["Experimentation","Hypothesis Design","Analysis"],
    "customer obsession": ["Customer Empathy","Voice of Customer","Execution"],
    "foundation":["Execution","Ownership","Collaboration"],
    "behavioral":["Communication","Leadership","Stakeholder Mgmt"],
    "technical": ["Technical Depth","System Design","Trade-offs"],
    "system design": ["System Design","Scalability","Trade-offs"],
    "product sense": ["Product Sense","User Empathy","Prioritization"],
    "execution": ["Execution","Project Mgmt","Cross-functional"],
    "launch": ["Go-to-Market","Execution","Stakeholder Mgmt"],
    "go-to-market": ["Go-to-Market","Positioning","Execution"],
    "pricing": ["Pricing","Market Analysis","Trade-offs"],
    "success criteria": ["Metrics","Success Criteria","Decision-making"],
    "prioritization": ["Prioritization","Trade-offs","Decision-making"],
}
def _infer_skills(category: Optional[str], complexity: Optional[str]) -> List[str]:
    cat = (category or "").lower()
    picked = None
    for key, skills in _CATEGORY_TO_SKILLS.items():
        if key in cat:
            picked = skills
            break
    if not picked:
        picked = ["Product Sense","Execution"]
    cx = (complexity or "").lower()
    if cx == "easy":
        return picked[:2] if len(picked) > 2 else picked
    if cx == "hard":
        return list(dict.fromkeys(picked + ["Depth","Edge Cases"]))
    return picked

def _serialize_question(q: Any, sanitize_to: Optional[str]) -> Dict[str, Any]:
    raw_text = getattr(q, "text", None) or getattr(q, "question", None) or ""
    category = getattr(q, "category", None)
    complexity = getattr(q, "complexity", None)
    safe_text = _normalize_prompt_brand(raw_text, sanitize_to)
    return {
        "id": getattr(q, "id", None),
        "question": safe_text,
        "company": getattr(q, "company", None),
        "category": category,
        "complexity": complexity,
        "experience_level": getattr(q, "experience_level", None),
        "years_of_experience": getattr(q, "years_of_experience", None),
        "skills": _infer_skills(category, complexity),
    }

# -------------- No-repeat + tiered selection --------------- #

def _pick_questions(
    db: Session,
    company: Optional[str],
    role: Optional[str],
    experience: Optional[str],
    limit: int,
    session_key: Optional[str],
    no_repeat_days: int,
) -> List[Dict[str, Any]]:

    wanted_company = normalize_company(company)
    wanted_role = normalize_role(role)
    desired_experience = experience.strip() if experience else None
    horizon = datetime.utcnow() - timedelta(days=no_repeat_days)

    # Exclude IDs already served to this session for same context recently
    exclude_ids: List[int] = []
    if session_key and (wanted_company or wanted_role):
        q_excl = db.query(ServedQuestion.question_id).filter(
            ServedQuestion.session_key == session_key,
            ServedQuestion.served_at >= horizon,
        )
        if wanted_company:
            q_excl = q_excl.filter(ServedQuestion.company == wanted_company)
        if wanted_role:
            q_excl = q_excl.filter(ServedQuestion.role == wanted_role)
        exclude_ids = [x[0] for x in q_excl.all()]

    results: List[Dict[str, Any]] = []
    chosen_ids: List[int] = []

    def add_from_query(base_q, sanitize_to: Optional[str], remaining: int) -> int:
        if remaining <= 0:
            return 0
        rows = (
            base_q
            .filter(not_(Question.id.in_(exclude_ids + chosen_ids)) if (exclude_ids or chosen_ids) else True)
            .order_by(func.random())  # randomize at DB level
            .limit(remaining)
            .all()
        )
        for q in rows:
            # final experience guard (keeps code simple)
            if desired_experience and not _experience_match(desired_experience, getattr(q,"years_of_experience",None)):
                continue
            results.append(_serialize_question(q, sanitize_to))
            qid = getattr(q, "id", None)
            if qid is not None:
                chosen_ids.append(qid)
        return remaining - len(rows)

    remaining = limit

    # A1) exact company + role
    if wanted_company and wanted_role:
        remaining = add_from_query(
            db.query(Question).filter(and_(Question.company == wanted_company,
                                           Question.experience_level == wanted_role)),
            sanitize_to=wanted_company, remaining=remaining)

    # A2) exact company (any role)
    if remaining > 0 and wanted_company:
        remaining = add_from_query(
            db.query(Question).filter(Question.company == wanted_company),
            sanitize_to=wanted_company, remaining=remaining)

    # B) 'our company' general pool
    if remaining > 0:
        remaining = add_from_query(
            db.query(Question).filter(Question.company == "our company"),
            sanitize_to="our company", remaining=remaining)

    # C1) role-only (any company)
    if remaining > 0 and wanted_role:
        remaining = add_from_query(
            db.query(Question).filter(Question.experience_level == wanted_role),
            sanitize_to=wanted_company or "our company", remaining=remaining)

    # C2) absolute fallback (anything)
    if remaining > 0:
        remaining = add_from_query(
            db.query(Question),
            sanitize_to=wanted_company or "our company", remaining=remaining)

    # Record what we served for this session/context
    if session_key and chosen_ids:
        bulk = [
            ServedQuestion(
                session_key=session_key,
                user_id=None,
                company=wanted_company,
                role=wanted_role,
                question_id=qid
            ) for qid in chosen_ids
        ]
        db.add_all(bulk)
        db.commit()

    random.shuffle(results)
    return results[:limit]

# -------------- Public endpoint --------------- #

@router.get("/questions")
def get_interview_questions(
    company: Optional[str] = Query(None, description="Preferred company (e.g., Zoho, Amazon)"),
    role: Optional[str] = Query(None, description="Role/level (APM, PM, Senior PM, etc.)"),
    experience: Optional[str] = Query(None, description="Experience bucket (0-2, 2-4, 5-8, 8+)"),
    session: Optional[str] = Query(None, description="Anonymous session key (uuid) for no-repeat sampling"),
    no_repeat_days: int = Query(NO_REPEAT_DAYS_DEFAULT, ge=1, le=365),
    db: Session = Depends(get_db),
):
    try:
        data = _pick_questions(
            db, company, role, experience,
            limit=TOTAL_QUESTIONS_TO_RETURN,
            session_key=session,
            no_repeat_days=no_repeat_days
        )
        if not data:
            raise HTTPException(status_code=404, detail="No questions available. Make sure your CSV is loaded into the database.")
        return data
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to fetch interview questions. ({type(exc).__name__})")
