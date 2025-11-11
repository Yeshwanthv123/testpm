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
TOTAL_QUESTIONS_TO_RETURN = 10
# Avoid repeating questions for the same browser session for N days
NO_REPEAT_DAYS_DEFAULT = 90


# -------------- Experience Level normalization (no longer using role) -------- #
def normalize_experience(experience: Optional[str]) -> Optional[str]:
    """
    Normalize experience level string (e.g., '0-2', '2-4', '5-8', '8+')
    to match the Years of Experience column in the CSV.
    """
    if not experience:
        return None
    exp = experience.strip().lower()
    # Map common patterns to the CSV format
    exp_map = {
        "0-1": "0-2",
        "0-2": "0-2",
        "1-2": "0-2",
        "2-4": "2-4",
        "2-5": "2-4",
        "4-5": "2-4",
        "5-8": "5-8",
        "5-7": "5-8",
        "7-8": "5-8",
        "8+": "8+",
        "8 years": "8+",
        "9+": "8+",
    }
    return exp_map.get(exp, experience.strip())


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
    wanted_experience = normalize_experience(experience)
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

    # 1. Try to match both company and experience level (most specific)
    if wanted_company and wanted_experience:
        remaining = add_from_query(
            db.query(Question).filter(and_(Question.company == wanted_company,
                                          Question.years_of_experience == wanted_experience)),
            sanitize_to=wanted_company, remaining=remaining)

    # 2. Try company + any experience (company is important)
    if remaining > 0 and wanted_company:
        remaining = add_from_query(
            db.query(Question).filter(Question.company == wanted_company),
            sanitize_to=wanted_company, remaining=remaining)

    # 3. Try desired experience + generic/any company (experience is important)
    if remaining > 0 and wanted_experience:
        remaining = add_from_query(
            db.query(Question).filter(Question.years_of_experience == wanted_experience),
            sanitize_to=wanted_company or "Generic", remaining=remaining)

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
    if older_avg > 0:
        # Standard percentage improvement calculation
        raw_improvement = ((recent_avg - older_avg) / older_avg) * 100
        # Cap improvement rate to reasonable range: -100% to +100%
        improvementRate = round(max(min(raw_improvement, 100), -100), 2)
    elif recent_avg > 0 and older_avg == 0:
        # Only have recent scores, not enough history for improvement calculation
        improvementRate = 0
    else:
        # No scores available
        improvementRate = 0

    # Percentile rank: compute average score per user and compare (aggregate)
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

    question_ids: List[int] = []
    # Prefer ServedQuestion mapping when session_id exists
    if evaluation.session_id:
        rows = db.query(ServedQuestion).filter(ServedQuestion.session_key == evaluation.session_id).order_by(ServedQuestion.served_at.asc()).all()
        question_ids = [r.question_id for r in rows]

    # Fallback: try to extract from evaluation.details per_question
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
