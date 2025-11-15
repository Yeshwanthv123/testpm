from typing import Dict, List, Optional, Tuple, Any
import math
import random
import re
import concurrent.futures
from datetime import timedelta, datetime
from sqlalchemy import inspect
from ..logger import logger

from fastapi import APIRouter, Depends, HTTPException, Query, Body, Header
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, not_

from ..database import get_db
from ..models import Question, ServedQuestion, Evaluation, User
from .. import schemas
from ..ai_services import ai_service
from ..routers.auth import _decode_bearer, get_current_user
from fastapi.encoders import jsonable_encoder

router = APIRouter(prefix="/interview", tags=["interview"])

# How many questions to return each time
# Reduced per request to match new requirement: 8 questions per interview
TOTAL_QUESTIONS_TO_RETURN = 8
# Avoid repeating questions for the same browser session for N days
NO_REPEAT_DAYS_DEFAULT = 90


# -------------- Experience Level normalization (no longer using role) -------- #
def normalize_experience(experience: Optional[str]) -> Optional[Tuple[str, Optional[str]]]:
    """
    Normalize experience level string (e.g., '6-10 years', '10+ years')
    Returns (years_bucket, expected_role_level).
    
    Maps:
    - '0-2 years' -> ('0-2', 'APM')
    - '3-5 years' -> ('3-5', 'PM')
    - '6-10 years' -> ('6-10', 'Senior PM')
    - '10+ years' -> ('10+', None) filters to Principal/Director only
    """
    if not experience:
        return None
    exp = experience.strip().lower()
    m = exp.replace("years", "").replace("year", "").replace("yrs", "").replace(" ", "")
    
    # Map to (years_bucket, expected_role_level)
    if m in ("0-2", "0-1", "1-2"):
        return ("0-2", "APM")
    if m in ("3-5", "2-3", "2-4", "2-5", "3-4"):
        return ("3-5", "PM")
    if m in ("5-8", "6-10", "5-10", "6-8", "8-10"):
        return ("6-10", "Senior PM")
    if m.endswith("+"):
        try:
            val = int(m[:-1])
            if val >= 10:
                return ("10+", None)  # None means Principal/Director level
            elif val >= 6:
                return ("6-10", "Senior PM")
            elif val >= 3:
                return ("3-5", "PM")
            else:
                return ("0-2", "APM")
        except Exception:
            return ("10+", None)
    # try numeric single value
    try:
        v = int(re.search(r"(\d+)", m).group(1))
        if v <= 2:
            return ("0-2", "APM")
        if 3 <= v <= 5:
            return ("3-5", "PM")
        if 6 <= v <= 10:
            return ("6-10", "Senior PM")
        return ("10+", None)
    except Exception:
        return None


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
    exp_result = normalize_experience(experience)
    wanted_experience = exp_result[0] if exp_result else None
    expected_role = exp_result[1] if exp_result else None
    
    horizon = datetime.utcnow() - timedelta(days=no_repeat_days)

    exclude_ids: List[int] = []
    if session_key and (wanted_company or wanted_experience):
        q_excl = db.query(ServedQuestion.question_id).filter(
            ServedQuestion.session_key == session_key,
            ServedQuestion.served_at >= horizon,
        )
        if wanted_company:
            q_excl = q_excl.filter(ServedQuestion.company == wanted_company)
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

    # Build a helper to add role filtering to any base query
    def add_role_filter(query):
        """Add experience_level filtering based on expected_role"""
        if expected_role == "Senior PM":
            # 6-10 years: exclude Principal/Director roles
            return query.filter(not_(Question.experience_level.in_(["Principal PM", "Director", "Principal Product Manager"])))
        elif expected_role is None:
            # 10+ years: ONLY Principal/Director, exclude APM/PM/Senior PM
            return query.filter(~Question.experience_level.in_(["APM", "PM", "Senior PM"]))
        else:
            # Other roles (APM, PM): no additional filtering needed for fallback
            return query

    # 1. Try to match both company and experience level (most specific)
    if wanted_company and wanted_experience:
        base_filter = and_(Question.company == wanted_company, Question.years_of_experience == wanted_experience)
        query = db.query(Question).filter(base_filter)
        query = add_role_filter(query)
        
        remaining = add_from_query(query, sanitize_to=wanted_company, remaining=remaining)

    # 2. Try company + any experience (company is important) - APPLY ROLE FILTER
    if remaining > 0 and wanted_company:
        query = db.query(Question).filter(Question.company == wanted_company)
        query = add_role_filter(query)
        remaining = add_from_query(query, sanitize_to=wanted_company, remaining=remaining)

    # 3. Try desired experience + generic/any company (experience is important) - APPLY ROLE FILTER
    if remaining > 0 and wanted_experience:
        base_filter = Question.years_of_experience == wanted_experience
        query = db.query(Question).filter(base_filter)
        query = add_role_filter(query)
        remaining = add_from_query(query, sanitize_to=wanted_company or "Generic", remaining=remaining)

    # 4. If still not enough, get any questions
    if remaining > 0:
        remaining = add_from_query(
            db.query(Question),
            sanitize_to=wanted_company or "Generic", remaining=remaining)

    if session_key and chosen_ids:
        bulk = [
            ServedQuestion(
                session_key=session_key,
                user_id=None,
                company=wanted_company,
                role=None,  # No longer using role
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
    experience: Optional[str] = Query(None),
    session: Optional[str] = Query(None),
    no_repeat_days: int = Query(NO_REPEAT_DAYS_DEFAULT, ge=1, le=365),
    db: Session = Depends(get_db),
):
    """
    Fetch interview questions filtered by company and experience level.
    
    Args:
        company: Optional company name (e.g., "Google", "Meta", "Generic")
        experience: Optional years of experience (e.g., "0-2", "2-4", "5-8", "8+")
        session: Session key for avoiding repeated questions
        no_repeat_days: Number of days to look back for previously served questions
    """
    try:
        data = _pick_questions(
            db, company, role=None, experience=experience,
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
    2. Extract Company and Years of Experience.
    3. Fetch matching questions from the question pool.
    """
    try:
        print("[InterviewRouter] Sending JD to AI service...")
        ai_details = await ai_service.extract_details_from_jd(jd_upload.jd_text)

        company = ai_details.get("company_name")
        years_of_experience = ai_details.get("years_of_experience")  # e.g., "6-10"
        level = ai_details.get("level")

        print(f"[InterviewRouter] AI extracted → Company={company}, YearsOfExperience={years_of_experience}, Level={level}")

        questions_list = _pick_questions(
            db,
            company=company,
            role=None,  # No longer using role
            experience=years_of_experience,  # Use years_of_experience instead
            limit=8,
            session_key=None,
            no_repeat_days=0,
        )

        if not questions_list:
            raise HTTPException(status_code=404, detail="No questions found for extracted company/experience level.")

        return {
            "status": "success",
            "data": {
                "ai_extracted": {
                    "company_name": company,
                    "years_of_experience": years_of_experience,
                    "level": level,
                },
                "questions": questions_list,
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
    x_session_key: Optional[str] = Header(None, alias="X-Session-Key"),
    session_key: Optional[str] = Query(None),
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
                    sess = x_session_key or session_key
                    logger.info(f"(Batch) Persisting evaluation: session={sess!r} type={type(sess)} user_id={(current_user.id if current_user else None)!r} overall={overall}")
                    
                    ev = Evaluation(session_id=str(sess) if sess is not None else None, user_id=(current_user.id if current_user else None), overall_score=overall, details={"per_question": results})
                    # Log what's going into the database
                    logger.debug(f"(Batch) Evaluation object before save: {dict(inspect(ev).attrs.items())}")
                    
                    db.add(ev)
                    db.commit()
                    db.refresh(ev)
                    
                    # Log what's in the database
                    logger.info(f"(Batch) Saved evaluation with session_id={ev.session_id!r} overall_score={ev.overall_score}")
                    
                    # Double check with a fresh query
                    saved = db.query(Evaluation).filter_by(id=ev.id).first()
                    logger.info(f"(Batch) Fresh query result: id={saved.id} session_id={saved.session_id!r} overall_score={saved.overall_score}")
                except Exception as e:
                    logger.error(f"(Batch) Failed to persist evaluation: {e}", exc_info=True)

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
            sess = x_session_key or session_key
            logger.info(f"Persisting evaluation: session={sess!r} type={type(sess)} user_id={(current_user.id if current_user else None)!r} overall={overall}")
            
            ev = Evaluation(session_id=str(sess) if sess is not None else None, user_id=(current_user.id if current_user else None), overall_score=overall, details={"per_question": results})
            # Log what's going into the database
            logger.debug(f"Evaluation object before save: {dict(inspect(ev).attrs.items())}")
            
            db.add(ev)
            db.commit()
            db.refresh(ev)
            
            # Log what's in the database
            logger.info(f"Saved evaluation with session_id={ev.session_id!r} overall_score={ev.overall_score}")
            
            # Double check with a fresh query
            saved = db.query(Evaluation).filter_by(id=ev.id).first()
            logger.info(f"Fresh query result: id={saved.id} session_id={saved.session_id!r} overall_score={saved.overall_score}")
        except Exception as e:
            logger.error(f"Failed to persist evaluation: {e}", exc_info=True)

        resp = {"overall_score": overall, "per_question": results}
        return jsonable_encoder(resp)

    except Exception as exc:
        print(f"[InterviewRouter] Error in /evaluate-answers: {exc}")
        raise HTTPException(status_code=500, detail=f"Failed to evaluate answers. ({type(exc).__name__})")


# -------------- Interview metrics and history --------------- #
@router.get("/metrics")
def get_interview_metrics(
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db),
    session_key: Optional[str] = Query(None),
    x_session_key: Optional[str] = Header(None, alias="X-Session-Key"),
    history_page: int = Query(1, ge=1),
    history_page_size: int = Query(20, ge=1, le=200),
):
    """Get interview metrics for the current user.

    Returns a consistent JSON shape with:
    - completed: total interviews completed
    - avgScore: average overall score
    - improvementRate: percent improvement (recent vs older)
    - percentileRank: percentile among users (based on avg per-user score)
    - recentInterviews: list of interviews (most recent first) with `canRetake`
    - achievements: list of earned badges
    """
    # Normalize session key: prefer explicit query param, then header
    if not session_key and x_session_key:
        session_key = x_session_key

    # Determine whether to aggregate by authenticated user or by anonymous session_key
    if current_user:
        total_q = db.query(func.count(Evaluation.id)).filter(Evaluation.user_id == current_user.id)
        completed = int(total_q.scalar() or 0)
        eval_filter_user = lambda q: q.filter(Evaluation.user_id == current_user.id)
    elif session_key:
        total_q = db.query(func.count(Evaluation.id)).filter(Evaluation.session_id == session_key)
        completed = int(total_q.scalar() or 0)
        eval_filter_user = lambda q: q.filter(Evaluation.session_id == session_key)
    else:
        # No auth and no session_key — return zeros (same shape as before)
        return {
            "completed": 0,
            "avgScore": 0,
            "improvementRate": 0,
            "percentileRank": 0,
            "recentInterviews": [],
            "achievements": [],
        }

    # Gather scores for improvement computation (fetch latest 10 scores only)
    latest_scores_rows = eval_filter_user(db.query(Evaluation.overall_score)).filter(
        Evaluation.overall_score.isnot(None)
    ).order_by(Evaluation.created_at.desc()).limit(10).all()
    scores = [r[0] for r in latest_scores_rows if r[0] is not None]
    # For avgScore across all evaluations, use SQL aggregate
    avg_row = eval_filter_user(db.query(func.avg(Evaluation.overall_score))).filter(
        Evaluation.overall_score.isnot(None)
    ).first()
    avgScore = float(avg_row[0]) if avg_row and avg_row[0] is not None else 0

    # Improvement rate: compare recent 5 vs previous 5 (if available)
    recent_scores = scores[:5]
    older_scores = scores[5:10]
    recent_avg = (sum(recent_scores) / len(recent_scores)) if recent_scores else 0
    older_avg = (sum(older_scores) / len(older_scores)) if older_scores else 0
    
    # Calculate improvement rate
    if len(older_scores) >= 3 and older_avg > 0:
        # Need at least 3 older scores for meaningful comparison
        raw_improvement = ((recent_avg - older_avg) / older_avg) * 100
        # Cap improvement rate to realistic range: -100% to +100%
        improvementRate = round(max(min(raw_improvement, 100), -100), 2)
    else:
        # Not enough history for improvement calculation
        improvementRate = 0

    # Percentile rank: compute average score per user and compare (aggregate by region if user has region)
    user_region = getattr(current_user, 'region', None) if current_user else None
    
    # Build query for all users to compare against
    if user_region:
        # Regional percentile: compare only against users in same region
        all_user_avgs = db.query(func.avg(Evaluation.overall_score).label("avg_score")).join(
            User, Evaluation.user_id == User.id
        ).filter(
            Evaluation.overall_score.isnot(None),
            User.region == user_region
        ).group_by(Evaluation.user_id).all()
    else:
        # Global percentile: compare against all users
        all_user_avgs = db.query(func.avg(Evaluation.overall_score).label("avg_score")).filter(
            Evaluation.overall_score.isnot(None)
        ).group_by(Evaluation.user_id).all()
    
    all_avgs = [r[0] for r in all_user_avgs if r[0] is not None]
    if all_avgs:
        better_than = sum(1 for a in all_avgs if avgScore > a)
        percentileRank = round((better_than / len(all_avgs)) * 100, 2)
    else:
        percentileRank = 0

    # Recent interviews (paginated) with questions and retake flag
    recent_interviews = []
    # Compute offset/limit
    offset = (history_page - 1) * history_page_size
    eval_rows = (
        eval_filter_user(db.query(Evaluation))
        .order_by(Evaluation.created_at.desc())
        .offset(offset)
        .limit(history_page_size)
        .all()
    )
    for ev in eval_rows:
        company = "Practice Interview"
        category = "General"
        questions = []
        if ev.details and isinstance(ev.details, dict):
            per_q = ev.details.get("per_question") or []
            for q in per_q:
                if isinstance(q, dict):
                    q_obj = q.get("question") or {}
                    if isinstance(q_obj, dict):
                        company = q_obj.get("company") or company
                        category = q_obj.get("category") or category
                    questions.append({
                        "id": str(q_obj.get("id")) if q_obj.get("id") is not None else None,
                        "question": q_obj.get("question") or q_obj.get("text") or "",
                        "category": q_obj.get("category") or "General",
                        "skills": q_obj.get("skills") or [],
                        "model_answer": q.get("model_answer", ""),
                        "score": q.get("score", 0),
                        "strengths": q.get("strengths", []) if isinstance(q.get("strengths", []), list) else [],
                        "weaknesses": q.get("weaknesses", []) if isinstance(q.get("weaknesses", []), list) else [],
                        "feedback": q.get("feedback", ""),
                    })

        recent_interviews.append({
            "id": ev.session_id or str(ev.id),
            "date": ev.created_at.isoformat(),
            "company": company,
            "category": category,
            "score": ev.overall_score,
            "questions": questions,
            "canRetake": True,
        })

    # Achievements
    achievements = []
    if completed >= 10:
        achievements.append({
            "id": "interview_master",
            "title": "Interview Master",
            "description": "Completed 10+ interviews",
            "icon": "trophy",
        })
    if avgScore >= 85:
        achievements.append({
            "id": "high_performer",
            "title": "High Performer",
            "description": "Scored 85+ average",
            "icon": "star",
        })
    # Consistency: last 3 scores >= 70
    if len(scores) >= 3 and all(s >= 70 for s in scores[:3]):
        achievements.append({
            "id": "consistent",
            "title": "Consistent Practicer",
            "description": "Strong recent performance",
            "icon": "check-circle",
        })
    if improvementRate is not None and improvementRate > 20:
        achievements.append({
            "id": "quick_learner",
            "title": "Quick Learner",
            "description": "Improved by 20%+",
            "icon": "trending-up",
        })

    return {
        "completed": completed,
        "avgScore": round(avgScore, 2),
        "improvementRate": improvementRate,
        "percentileRank": percentileRank,
        "recentInterviews": recent_interviews,
        "achievements": achievements,
        "history_page": history_page,
        "history_page_size": history_page_size,
        "history_total": completed,
    }


@router.post("/retake")
def retake_interview(
    payload: Dict[str, Any] = Body(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return the original questions for a past interview so the user can retake the same set.

    Expects JSON { "interview_id": "<id or session_key>" } where id can be the numeric Evaluation.id
    or the Evaluation.session_id string. Returns serialized questions in the same shape as /questions.
    """
    interview_id = payload.get("interview_id")
    if not interview_id:
        raise HTTPException(status_code=400, detail="interview_id is required")

    # Try to find evaluation by numeric id or by session_id
    evaluation = None
    try:
        # numeric id
        eid = int(interview_id)
        evaluation = db.query(Evaluation).filter(Evaluation.id == eid).first()
    except Exception:
        evaluation = db.query(Evaluation).filter(Evaluation.session_id == str(interview_id)).first()

    if not evaluation:
        raise HTTPException(status_code=404, detail="Interview not found")

    if evaluation.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to retake this interview")

    # If the evaluation stored a per-question snapshot, prefer returning that exact snapshot
    # This preserves question text, company, skills, model_answer, score, strengths, weaknesses, feedback
    if evaluation.details and isinstance(evaluation.details, dict):
        per_q = evaluation.details.get("per_question") or []
        if isinstance(per_q, list) and len(per_q) > 0:
            serialized = []
            for idx, q in enumerate(per_q):
                if not isinstance(q, dict):
                    continue
                q_obj = q.get("question") or {}
                qid = None
                if isinstance(q_obj, dict):
                    qid = q_obj.get("id")
                qtext = None
                if isinstance(q_obj, dict):
                    qtext = q_obj.get("question") or q_obj.get("text")
                if not qtext:
                    qtext = q.get("question") or q.get("text") or ""

                serialized.append({
                    "id": str(qid) if qid is not None else f"retaken_{idx}",
                    "question": qtext or "",
                    "company": (q_obj.get("company") if isinstance(q_obj, dict) else None) or q.get("company"),
                    "category": (q_obj.get("category") if isinstance(q_obj, dict) else None) or q.get("category") or "General",
                    "complexity": (q_obj.get("complexity") if isinstance(q_obj, dict) else None) or q.get("complexity") or q.get("difficulty"),
                    "experience_level": (q_obj.get("experience_level") if isinstance(q_obj, dict) else None) or q.get("experience_level"),
                    "years_of_experience": (q_obj.get("years_of_experience") if isinstance(q_obj, dict) else None) or q.get("years_of_experience"),
                    "skills": (q_obj.get("skills") if isinstance(q_obj, dict) else None) or q.get("skills") or [],
                    "model_answer": q.get("model_answer") or "",
                    "score": q.get("score") or 0,
                    "strengths": q.get("strengths") or [],
                    "weaknesses": q.get("weaknesses") or [],
                    "feedback": q.get("feedback") or "",
                })
            return {"questions": serialized}

    # Fallback: return questions by id from ServedQuestion mapping or evaluation snapshot ids
    question_ids: List[int] = []
    # Prefer ServedQuestion mapping when session_id exists
    if evaluation.session_id:
        rows = db.query(ServedQuestion).filter(ServedQuestion.session_key == evaluation.session_id).order_by(ServedQuestion.served_at.asc()).all()
        question_ids = [r.question_id for r in rows]

    if not question_ids and evaluation.details and isinstance(evaluation.details, dict):
        per_q = evaluation.details.get("per_question") or []
        for q in per_q:
            if isinstance(q, dict):
                qobj = q.get("question") or {}
                if isinstance(qobj, dict):
                    qid = qobj.get("id")
                    if qid:
                        try:
                            question_ids.append(int(qid))
                        except Exception:
                            pass

    if not question_ids:
        raise HTTPException(status_code=404, detail="No question ids available for this interview")

    questions = db.query(Question).filter(Question.id.in_(question_ids)).all()
    # preserve order according to question_ids
    id_to_q = {q.id: q for q in questions}
    serialized = []
    for qid in question_ids:
        q = id_to_q.get(qid)
        if q:
            serialized.append(_serialize_question(q, sanitize_to=q.company))

    return {"questions": serialized}


# -------------- User ranking and peer comparison --------------- #
@router.get("/my-ranking")
def get_my_ranking(
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db),
):
    """
    Get current user's ranking and peer comparison data.
    Returns:
    - avgScore: User's average score across all interviews
    - percentileRank: User's percentile rank globally
    - regionalPercentile: User's percentile rank in their region
    - experiencePercentile: User's percentile rank by experience level
    - totalCandidates: Total number of candidates globally
    - regionalCandidates: Total candidates in user's region
    """
    if not current_user:
        return {
            "avgScore": 0,
            "percentileRank": 0,
            "regionalPercentile": 0,
            "experiencePercentile": 0,
            "totalCandidates": 0,
            "regionalCandidates": 0,
        }

    # Get user's average score and interview count
    user_stats = db.query(
        func.avg(Evaluation.overall_score).label('avg_score'),
        func.count(Evaluation.id).label('interview_count')
    ).filter(
        Evaluation.user_id == current_user.id,
        Evaluation.overall_score.isnot(None)
    ).first()

    avg_score = float(user_stats.avg_score) if user_stats and user_stats.avg_score else 0
    interview_count = user_stats.interview_count if user_stats else 0

    # Global percentile: compare against all users' average scores
    all_users_avg = db.query(
        func.avg(Evaluation.overall_score).label('avg_score')
    ).filter(
        Evaluation.overall_score.isnot(None)
    ).group_by(Evaluation.user_id).all()

    all_avgs = [float(r.avg_score) for r in all_users_avg if r.avg_score]
    global_better_than = sum(1 for a in all_avgs if avg_score > a)
    percentile_rank = round((global_better_than / len(all_avgs)) * 100, 2) if all_avgs else 0
    total_candidates = len(all_avgs)

    # Regional percentile: compare against peers in same region
    regional_percentile = percentile_rank
    regional_candidates = total_candidates
    
    if current_user.region:
        regional_users_avg = db.query(
            func.avg(Evaluation.overall_score).label('avg_score')
        ).join(User, Evaluation.user_id == User.id).filter(
            Evaluation.overall_score.isnot(None),
            User.region == current_user.region
        ).group_by(Evaluation.user_id).all()

        regional_avgs = [float(r.avg_score) for r in regional_users_avg if r.avg_score]
        regional_better_than = sum(1 for a in regional_avgs if avg_score > a)
        regional_percentile = round((regional_better_than / len(regional_avgs)) * 100, 2) if regional_avgs else 0
        regional_candidates = len(regional_avgs)

    # Experience percentile: compare against users with similar experience
    experience_percentile = percentile_rank
    
    if current_user.experience:
        exp_users_avg = db.query(
            func.avg(Evaluation.overall_score).label('avg_score')
        ).join(User, Evaluation.user_id == User.id).filter(
            Evaluation.overall_score.isnot(None),
            User.experience == current_user.experience
        ).group_by(Evaluation.user_id).all()

        exp_avgs = [float(r.avg_score) for r in exp_users_avg if r.avg_score]
        exp_better_than = sum(1 for a in exp_avgs if avg_score > a)
        experience_percentile = round((exp_better_than / len(exp_avgs)) * 100, 2) if exp_avgs else 0

    return {
        "avgScore": round(avg_score, 2),
        "percentileRank": percentile_rank,
        "regionalPercentile": regional_percentile,
        "experiencePercentile": experience_percentile,
        "totalCandidates": total_candidates,
        "regionalCandidates": regional_candidates,
        "interviewCount": interview_count,
    }
