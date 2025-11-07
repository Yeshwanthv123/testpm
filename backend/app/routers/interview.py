from typing import Dict, List, Optional, Tuple, Any
import math
import random
import re
import concurrent.futures
from datetime import timedelta, datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Body, Header
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, not_

from ..database import get_db
from ..models import Question, ServedQuestion, Evaluation, User
from .. import schemas
from ..ai_services import ai_service
from ..routers.auth import _decode_bearer
from fastapi.encoders import jsonable_encoder

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
    "Google","Meta","Amazon","Microsoft","Apple","Netflix","Uber",
    "Salesforce","Freshworks","Zoho","Stripe","Airbnb",
    "Spotify","Square","Twilio","Atlassian","Slack","LinkedIn","Tesla","Dropbox","HubSpot","Adobe","Shopify",
    "Instagram","Facebook","WhatsApp","Threads","Messenger","YouTube","Android","Chrome","Gmail",
    "App Store","iOS","Azure","Office","Teams","AWS","Prime","Kindle",
    "Freshdesk","Freshservice","Freshsales","Zoho CRM","Zoho Books","Zoho Mail"
]
_SANITIZE_RE = re.compile(
    r"\b(" + "|".join(re.escape(t) for t in sorted(_BRAND_TOKENS, key=len, reverse=True)) + r")\b",
    flags=re.IGNORECASE
)

def _normalize_prompt_brand(text: str, sanitize_to: Optional[str]) -> str:
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
            .order_by(func.random())
            .limit(remaining)
            .all()
        )
        for q in rows:
            results.append(_serialize_question(q, sanitize_to))
            qid = getattr(q, "id", None)
            if qid is not None:
                chosen_ids.append(qid)
        return remaining - len(rows)

    remaining = limit

    if wanted_company and wanted_role:
        remaining = add_from_query(
            db.query(Question).filter(and_(Question.company == wanted_company,
                                          Question.experience_level == wanted_role)),
            sanitize_to=wanted_company, remaining=remaining)

    if remaining > 0 and wanted_company:
        remaining = add_from_query(
            db.query(Question).filter(Question.company == wanted_company),
            sanitize_to=wanted_company, remaining=remaining)

    if remaining > 0:
        remaining = add_from_query(
            db.query(Question).filter(Question.company == "our company"),
            sanitize_to="our company", remaining=remaining)

    if remaining > 0 and wanted_role:
        remaining = add_from_query(
            db.query(Question).filter(Question.experience_level == wanted_role),
            sanitize_to=wanted_company or "our company", remaining=remaining)

    if remaining > 0:
        remaining = add_from_query(
            db.query(Question),
            sanitize_to=wanted_company or "our company", remaining=remaining)

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


def get_optional_user(db: Session = Depends(get_db), authorization: Optional[str] = Header(None)) -> Optional[User]:
    """Try to resolve an authenticated user from the Authorization header.
    Returns None if no valid bearer token is present or the token is invalid.
    This avoids making the evaluation endpoints strictly require auth while allowing
    us to persist the user_id when available.
    """
    try:
        if not authorization:
            return None
        payload = _decode_bearer(authorization)
        if payload.get("type") != "access":
            return None
        user_id = payload.get("sub")
        email = payload.get("email")
        if not user_id or not email:
            return None
        user = db.query(User).filter(User.id == int(user_id), User.email == email).first()
        if not user or not user.is_active:
            return None
        return user
    except Exception:
        return None


# -------------- Public endpoint --------------- #
@router.get("/questions")
def get_interview_questions(
    company: Optional[str] = Query(None),
    role: Optional[str] = Query(None),
    experience: Optional[str] = Query(None),
    session: Optional[str] = Query(None),
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
            raise HTTPException(status_code=404, detail="No questions available. Make sure your CSV is loaded.")
        return data
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to fetch interview questions. ({type(exc).__name__})")


# -------------- JD-based Interview Starter --------------- #
@router.post("/start-with-jd")
async def start_interview_with_jd(
    jd_upload: schemas.JDUpload = Body(...),
    db: Session = Depends(get_db),
):
    """
    1. Analyze a Job Description (JD) using local AI service.
    2. Extract Company and Role (Experience Level).
    3. Fetch one matching question from the question pool.
    """
    try:
        print("[InterviewRouter] Sending JD to AI service...")
        ai_details = await ai_service.extract_details_from_jd(jd_upload.jd_text)

        company = ai_details.get("company_name")
        role = ai_details.get("role") or ai_details.get("experience_level")
        level = ai_details.get("level")

        print(f"[InterviewRouter] AI extracted → Company={company}, Role={role}, Level={level}")

        questions_list = _pick_questions(
            db,
            company=company,
            role=role,
            experience=None,
            limit=1,
            session_key=None,
            no_repeat_days=0,
        )

        if not questions_list:
            raise HTTPException(status_code=404, detail="No questions found for extracted role/company.")

        return {
            "status": "success",
            "data": {
                "ai_extracted": {
                    "company_name": company,
                    "role": role,
                    "level": level,
                },
                "question": questions_list[0],
            },
        }

    except HTTPException:
        raise
    except Exception as exc:
        print(f"[InterviewRouter] Error in /start-with-jd: {exc}")
        raise HTTPException(status_code=500, detail=f"Failed to start interview from JD. ({type(exc).__name__})")


# -------------- Evaluate user answers (generate model answers + compare) --------------- #
@router.post("/evaluate-answers")
def evaluate_answers(
    payload: schemas.EvaluateRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    """
    Given a list of answered questions (each contains the original question object
    and the user's answer), generate an ideal/model answer and evaluate the user's
    answer against it. Returns per-question evaluation data and an overall score.
    """
    try:
        items = payload.items or []
        results = []
        total_score = 0
        count = 0

        # Prepare questions for batch generation
        qlist = []
        for it in items:
            qobj = it.question or {}
            qtext = qobj.get("question") or qobj.get("text") or ""
            category = qobj.get("category")
            complexity = qobj.get("complexity")
            skills = _infer_skills(category, complexity)
            qlist.append({"question": qtext, "skills": skills})

        # First, try a single-shot batch evaluation (model answer + evaluation in one call)
        batch_items = []
        for it in items:
            qobj = it.question or {}
            qtext = qobj.get("question") or qobj.get("text") or ""
            category = qobj.get("category")
            complexity = qobj.get("complexity")
            skills = _infer_skills(category, complexity)
            batch_items.append({"question": qtext, "user_answer": (it.user_answer or "").strip(), "skills": skills})

        try:
            batch_eval = ai_service.evaluate_answers_batch(batch_items) if batch_items else []
            if isinstance(batch_eval, list) and len(batch_eval) == len(items):
                # Use batch_eval directly
                results = []
                total_score = 0
                count = 0
                for idx, r in enumerate(batch_eval):
                    # r expected to have model_answer, score, strengths, weaknesses, feedback
                    qobj = items[idx].question or {}
                    # ensure skills propagate for frontend aggregation
                    if not qobj.get("skills"):
                        qobj["skills"] = _infer_skills(qobj.get("category"), qobj.get("complexity"))
                    score = int(r.get("score") or 0)
                    results.append({
                        "question": qobj,
                        "model_answer": r.get("model_answer") or "",
                        "score": score,
                        "strengths": r.get("strengths") or [],
                        "weaknesses": r.get("weaknesses") or [],
                        "feedback": r.get("feedback") or "",
                    })
                    total_score += score
                    count += 1

                overall = int(round((total_score / count))) if count > 0 else 0

                # persist
                try:
                    ev = Evaluation(session_id=None, user_id=(current_user.id if current_user else None), overall_score=overall, details={"per_question": results})
                    db.add(ev)
                    db.commit()
                except Exception as e:
                    print(f"[InterviewRouter] Failed to persist evaluation: {e}")

                resp = {"overall_score": overall, "per_question": results}
                return jsonable_encoder(resp)
        except Exception as e:
            print(f"[InterviewRouter] Batch evaluate failed, falling back: {e}")

        # Generate model answers in a single batch when possible
        model_answers = ai_service.generate_answers_batch(qlist) if qlist else []

        # Evaluate in parallel
        def process_eval(idx, it):
            try:
                qobj = it.question or {}
                user_ans = (it.user_answer or "").strip()
                q_text = qobj.get("question") or qobj.get("text") or ""
                skills = _infer_skills(qobj.get("category"), qobj.get("complexity"))
                if not qobj.get("skills"):
                    qobj["skills"] = skills
                model_ans = model_answers[idx] if idx < len(model_answers) else ai_service.generate_answer(q_text, skills)
                eval_res = ai_service.evaluate_answer(q_text, user_ans, model_ans)
                score = int(eval_res.get("score") or 0)
                return {
                    "question": qobj,
                    "model_answer": model_ans,
                    "score": score,
                    "strengths": eval_res.get("strengths") or [],
                    "weaknesses": eval_res.get("weaknesses") or [],
                    "feedback": eval_res.get("feedback") or "",
                }
            except Exception as e:
                print(f"[InterviewRouter] process_eval error: {e}")
                return {
                    "question": it.question or {},
                    "model_answer": "",
                    "score": 0,
                    "strengths": [],
                    "weaknesses": [],
                    "feedback": "Evaluation failed.",
                }

        max_workers = min(6, max(1, len(items)))
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as ex:
            futures = [ex.submit(process_eval, idx, it) for idx, it in enumerate(items)]
            for fut in concurrent.futures.as_completed(futures):
                r = fut.result()
                results.append(r)
                try:
                    total_score += int(r.get("score") or 0)
                    count += 1
                except Exception:
                    pass

        overall = int(round((total_score / count))) if count > 0 else 0

        # Persist evaluation to DB (best-effort)
        try:
            ev = Evaluation(session_id=None, user_id=(current_user.id if current_user else None), overall_score=overall, details={"per_question": results})
            db.add(ev)
            db.commit()
        except Exception as e:
            print(f"[InterviewRouter] Failed to persist evaluation: {e}")

        resp = {"overall_score": overall, "per_question": results}
        return jsonable_encoder(resp)

    except Exception as exc:
        print(f"[InterviewRouter] Error in /evaluate-answers: {exc}")
        raise HTTPException(status_code=500, detail=f"Failed to evaluate answers. ({type(exc).__name__})")
