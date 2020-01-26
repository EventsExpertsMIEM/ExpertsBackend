from ..db import get_session

from .models import Question
from .exceptions import QuestionNotFound


def get_questions():
    with get_session() as s:
        return s.query(Question).all()


def get_question(id):
    q = None

    with get_session() as s:
        q = s.query(Question).filter_by(id=id).one_or_none()

        if q is None:
            raise QuestionNotFound(id)

        return q


def is_question_exists(id):
    with get_session() as s:
        return s.query(Question).filter_by(id=id).one_or_none() is not None
