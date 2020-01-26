from flask import render_template, abort
from flask_login import current_user

from . import bp
from .helpers import *


@bp.route('/')
def questions():
    questions = get_questions()
    return render_template('questions/main.html', questions=questions)


@bp.route('/<int:id>')
def question(id):
    try:
        q = get_question(id)
        q.increase_views()
        return render_template('questions/question_page.html', question=q)
    except QuestionNotFound:
        abort(404)
