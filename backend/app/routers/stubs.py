from fastapi import APIRouter, HTTPException, Body, Depends, Header
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from typing import Any

from app.database import get_db
from app.ai_services import ai_service
from app.models import Evaluation, User
from typing import Optional
from app.routers.auth import _decode_bearer


def get_optional_user(db: Session = Depends(get_db), authorization: Optional[str] = Header(None)) -> Optional[User]:
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
		try:
			u = db.query(User).filter(User.id == int(user_id), User.email == email).first()
			if not u or not u.is_active:
				return None
			return u
		except Exception:
			return None
	except Exception:
		return None

router = APIRouter(tags=["stubs"])


@router.post("/tts")
def tts():
	raise HTTPException(status_code=501, detail="Text-to-Speech not implemented.")


@router.post("/stt")
def stt():
	raise HTTPException(status_code=501, detail="Speech-to-Text not implemented.")


@router.post("/api/interview/evaluate-answers")
def evaluate_answers_proxy(payload: dict = Body(...), db: Session = Depends(get_db), current_user: Optional[User] = Depends(get_optional_user)) -> Any:
	"""
	Compatibility proxy: expose /api/interview/evaluate-answers for clients that post there.
	This delegates to `ai_service` to generate model answers and evaluate user answers.
	It persists a best-effort `Evaluation` record and returns the same shape as the main router.
	"""
	try:
		items = payload.get("items") or []
		# Prepare minimal batch for generation (only question text)
		qlist = []
		for it in items:
			qobj = it.get("question") or {}
			qtext = qobj.get("question") or qobj.get("text") or ""
			qlist.append({"question": qtext})

		model_answers = ai_service.generate_answers_batch(qlist) if qlist else []

		results = []
		total = 0
		count = 0
		for idx, it in enumerate(items):
			qobj = it.get("question") or {}
			qtext = qobj.get("question") or qobj.get("text") or ""
			user_ans = (it.get("user_answer") or "").strip()
			# ensure skills present for frontend consumption
			skills = qobj.get("skills") or []
			if not skills:
				skills = []
				# best-effort: try to infer category/complexity based skills if available
				if isinstance(qobj.get("category"), str):
					skills = [qobj.get("category")]
			model_ans = model_answers[idx] if idx < len(model_answers) else ai_service.generate_answer(qtext, skills)
			eval_res = ai_service.evaluate_answer(qtext, user_ans, model_ans)
			score = int(eval_res.get("score") or 0)
			results.append({
				"question": qobj,
				"model_answer": model_ans,
				"score": score,
				"strengths": eval_res.get("strengths") or [],
				"weaknesses": eval_res.get("weaknesses") or [],
				"feedback": eval_res.get("feedback") or "",
			})
			total += score
			count += 1

		overall = int(round((total / count))) if count > 0 else 0

		# persist (best-effort)
		try:
			ev = Evaluation(session_id=None, user_id=(current_user.id if current_user else None), overall_score=overall, details={"per_question": results})
			db.add(ev)
			db.commit()
		except Exception as e:
			print(f"[Stubs] Failed to persist evaluation: {e}")

		resp = {"overall_score": overall, "per_question": results}
		return jsonable_encoder(resp)
	except Exception as ex:
		print(f"[Stubs] Error in proxy evaluate-answers: {ex}")
		raise HTTPException(status_code=500, detail="Evaluation proxy failed.")
