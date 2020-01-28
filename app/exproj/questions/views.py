from flask import render_template, abort, request, redirect, url_for
from flask_login import login_required, current_user

from . import bp, forms, helpers
from .exceptions import QuestionNotFound


@bp.route('/')
@login_required
def questions():
    questions = helpers.get_questions()
    return render_template('questions/main.html', questions=questions)


@bp.route('/new', methods=['GET', 'POST'])
@login_required
def ask_question():
    form = forms.NewQuestion(request.form)
    if request.method == 'POST' and form.validate_on_submit():
        new_q_id = helpers.new_question(current_user.id, form.question.data, form.desc.data)
        return redirect(url_for('questions.question', id=new_q_id))
    return render_template('questions/new.html', form=form)


@bp.route('/<int:id>')
@login_required
def question(id):
    try:
        q = helpers.get_question(id)
        q.increase_views()
        return render_template('questions/question_page.html', question=q)
    except QuestionNotFound:
        abort(404)


@bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_question(id):
    # todo
    # improvement safety
    helpers.delete_question(id)
    return redirect(url_for('general.cabinet'))