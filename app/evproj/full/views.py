from flask import (Blueprint, request, redirect, url_for,
                   render_template, jsonify, abort)
from flask_login import (login_required, login_user, logout_user,
                         login_fresh, current_user)

from passlib.hash import sha256_crypt

from .. import core
from ..core import auth
from . import forms


bp = Blueprint('general', __name__)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('general.home'))
    form = forms.AuthForm(request.form)
    message = ''
    if request.method == "POST" and form.validate_on_submit():
        user = auth.check_user(form.mail.data)
        if user:
            if sha256_crypt.verify(form.password.data, user.password):
                login_user(user)
                return redirect(url_for('general.home'))
            else:
                message = 'Invalid password'
        else:
            message = 'Invalid user'
    return render_template('login.html', form=form, message=message)


@bp.route('/register')
def register():
    if current_user.is_authenticated:
        return redirect(url_for('general.home'))
    form = forms.RegisterForm(request.form)
    message = ''
    return render_template('register.html', form=form, message=message)


@bp.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('general.home'))


@bp.route('/confirm/<string:link>')
def confirm(link):
    message = core.confirm_user(link)
    return render_template(
        'conf.html',
        message=message
    )


@bp.route('/')
@bp.route('/home')
def home():
    events = core.get_events()
    return render_template(
        'home.html',
        events=events,
        current_user=current_user,
    )


@bp.route('/cabinet')
@login_required
def cabinet():
    as_creator, as_presenter, as_guest = core.get_user_stat(current_user.id)
    return render_template(
        '/cabinet.html',
        user=current_user,
        as_creator=as_creator,
        as_presenter=as_presenter,
        as_guest=as_guest,
    )


@bp.route('/create_event')
@login_required
def create_event():
    form = forms.CreateEvent(request.form)
    message = ''
    return render_template(
        '/create_event.html',
        form=form,
        message=message,
    )


@bp.route('/event/<string:id>')
def event(id):
    if core.event_exist(id):
        event = core.get_event_info(id)
        users = core.get_participators(id)
        entering = 'not joined'
        if current_user.is_authenticated:
            entering = core.check_participation(current_user.id, id)
        conf, unconf = core.get_stat(id)
        unc_users = core.get_uncorfimed_users(id)

        return render_template(
            '/event_page.html',
            event=event,
            users=users,
            entering=entering,
            conf=conf,
            unconf=unconf,
            unc_users=unc_users,
            current_user=current_user,
        )
    else:
        abort(404)


def page_not_found(e):
    if current_user.is_authenticated:
        return render_template(
            '404.html',
            login=current_user.mail
        ), 404
    else:
        return render_template(
            '404.html',
            login=''
        ), 404
