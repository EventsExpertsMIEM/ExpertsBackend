from datetime import datetime

from exproj.db import get_session
from exproj.db.models import User

from .models import Question
from .exceptions import QuestionNotFound


def get_questions():
    with get_session() as s:
        return s.query(Question).order_by(Question.create_time.desc()).all()


def get_question(id):
    with get_session() as s:
        q = s.query(Question).get(id)
        if q is None:
            raise QuestionNotFound(id)
        return q


def get_user_questions(user_id):
    with get_session() as s:
        return s.query(User).get(user_id).questions


def is_question_exists(id):
    with get_session() as s:
        return s.query(Question).filter_by(id=id).one_or_none() is not None


def new_question(user_id, question, desc):
    question = Question(
        user_id=user_id,
        question=question,
        desc=desc
    )
    with get_session() as s:
        s.add(question)
        return s.query(Question).order_by(-Question.id).first().id


def delete_question(id):
    with get_session() as s:
        q = s.query(Question).get(id)
        if q is None:
            raise QuestionNotFound(id)
        s.delete(q)
