from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from typing import List
import random

from app.db import get_db
from app.models import Question
from app.schemas import QuestionInDB

router = APIRouter()

MIN_QUESTIONS_THRESHOLD = 5
TOTAL_QUESTIONS_TO_RETURN = 10

@router.get("/api/interview/questions", response_model=List[QuestionInDB])
def get_interview_questions(company: str, role: str, db: Session = Depends(get_db)):
    company_query = select(Question).where(Question.company == company)
    company_questions = db.execute(company_query).scalars().all()
    final_questions = list(company_questions)

    if len(final_questions) < MIN_QUESTIONS_THRESHOLD:
        num_generic_needed = TOTAL_QUESTIONS_TO_RETURN - len(final_questions)
        generic_query = (
            select(Question)
            .where(Question.company == "Generic")
            .order_by(func.random())
            .limit(num_generic_needed)
        )
        generic_questions = db.execute(generic_query).scalars().all()
        final_questions.extend(generic_questions)

    random.shuffle(final_questions)
    return final_questions[:TOTAL_QUESTIONS_TO_RETURN]