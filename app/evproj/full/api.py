from flask import Blueprint, jsonify, request, make_response
from flask_login import login_required, current_user

from passlib.hash import sha256_crypt

from ..core import auth
from ..core import api

from ..core.exceptions import NotJsonError, NoData
from sqlalchemy.exc import IntegrityError


mod = Blueprint('api', __name__, url_prefix='/api')


def make_400(text='Invalid reqeust'):
    body = jsonify(error=text)
    return make_response(body, 400)


def make_ok(description=None, params=None):
    body = {
        'status': 'ok',
    }
    if description:
        body['description'] = description
    if params:
        body['params'] = params
    return jsonify(body)


@mod.route('/register_user', methods=['POST'])
def register_user():
    try:
        args = request.get_json()
        if not args:
            return make_400('Expected json')

        api.register_user(args['mail'], args['name'], args['surname'],
                          sha256_crypt.encrypt(str(args['password'])))
        return make_ok('User was registered')
    except KeyError:
        return make_400()
    except IntegrityError:
        return make_400('User with this login already exists')


@mod.route('/event_create', methods=['POST'])
@login_required
def event_create():
    try:
        args = request.get_json()
        if not args:
            return make_400('Expected json')

        last_id = api.create_event(args['name'], args['sm_description'],
                                   args['description'], args['date_time'],
                                   args['phone'], args['mail'])
        api.create_event_creator(current_user.id, last_id)
        if args['presenters'] != '':
            api.create_event_presenters(args['presenters'], last_id)

        return make_ok('Event was created', str(last_id))
    except KeyError:
        return make_400()
    except IntegrityError as e:
        return make_400('Something went wrong - \n{}'.format(str(e)))


@mod.route('/join', methods=['POST'])
@login_required
def join():
    try:
        args = request.get_json()
        if not args:
            return make_400('Expected json')
        if api.event_exist(int(args['event_id'])):
            api.guest_join(current_user.id, int(args['event_id']))
            return make_ok()
    except Exception as e:
        return make_400('Problem.\n{}'.format(str(e)))


@mod.route('/guest_action', methods=['POST'])
@login_required
def guest_action():
    try:
        args = request.get_json()
        if not args:
            return make_400('Expected json')
        api.guest_action(int(args['user']), int(args['event']), args['action'])
        return make_ok()
    except KeyError:
        return make_400()
    except IntegrityError:
        return make_400('Something went wrong')
