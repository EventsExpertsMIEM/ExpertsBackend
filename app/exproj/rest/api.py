from flask import Blueprint, jsonify, request, make_response

from passlib.hash import sha256_crypt

from .. import core

from ..core.exceptions import NotJsonError, NoData
from sqlalchemy.exc import IntegrityError


bp = Blueprint('core', __name__)


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


def route_not_found(e):
    return jsonify(error="Unknown route!"), 404


@bp.route('/register', methods=['POST'])
def register():
    try:
        args = request.get_json()
        if not args:
            return make_400('Expected json')

        core.register_user(args['mail'], args['name'], args['surname'],
                          sha256_crypt.encrypt(str(args['password'])))
        return make_ok('User was registered')
    except KeyError as e:
        return make_400('KeyError - \n{}'.format(str(e)))
    except IntegrityError:
        return make_400('User with this login already exists')


@bp.route('/create_event', methods=['POST'])
def create_event():
    try:
        args = request.get_json()
        if not args:
            return make_400('Expected json')

        user_id = core.get_id_by_mail(args['mail'])
        if user_id == -1:
            return make_400('Unknown user')

        last_id = core.create_event(args['name'], args['sm_description'],
                                   args['description'], args['date_time'],
                                   args['phone'], args['mail'])
        core.create_event_creator(user_id, last_id)
        if args['presenters'] != '':
            core.create_event_presenters(args['presenters'], last_id)

        return make_ok('Event was created', str(last_id))
    except KeyError as e:
        return make_400('KeyError - \n{}'.format(str(e)))
    except IntegrityError as e:
        return make_400('IntegrityError - \n{}'.format(str(e)))
    except Exception as e:
        return make_400('Problem - \n{}'.format(str(e)))


@bp.route('/events', methods=['GET'])
def get_all_machines():
    try:
        return jsonify(core.get_events())
    except Exception as e:
        return make_400('Problem.\n{}'.format(str(e)))


@bp.route('/join', methods=['POST'])
def join():
    try:
        args = request.get_json()
        if not args:
            return make_400('Expected json')
        user_id = core.get_id_by_mail(args['mail'])
        if core.event_exist(int(args['event_id'])):
            if user_id != -1:
                core.guest_join(user_id, int(args['event_id']))
                return make_ok('Guest joined event')
            else:
                return make_400('No such user')
        else:
            return make_400('No such event')
    except Exception as e:
        return make_400('Problem.\n{}'.format(str(e)))


@bp.route('/event/<int:id>', methods=['GET'])
def event(id):
    try:
        if core.event_exist(id):
            return jsonify(core.event_info(id))
        else:
            return make_400('No such event')
    except Exception as e:
        return make_400('Problem. {}'.format(str(e)))


# TODO

@bp.route('/profile/<string:mail>')
def profile(mail):
    try:
        user_id = core.get_id_by_mail(mail)
        if user_id != -1:
            as_creator, as_presenter, as_guest = core.get_user_stat(user_id)
            return jsonify(creator=as_creator, presenter=as_presenter,
                           guest=as_presenter)
        else:
            return make_400('No such user')
    except Exception as e:
        return make_400('Problem. {}'.format(str(e)))


@bp.route('/guest_action', methods=['POST'])
def guest_action():
    try:
        args = request.get_json()
        if not args:
            return make_400('Expected json')
        user_id = core.get_id_by_mail(args['mail'])
        core.event_exist(int(args['event_id']))

        core.guest_action(int(args['user']), int(args['event']), args['action'])
        return make_ok()
    except KeyError as e:
        return make_400('KeyError - \n{}'.format(str(e)))
    except IntegrityError as e:
        return make_400('IntegrityError - \n{}'.format(str(e)))
    except Exception as e:
        return make_400('Problem. {}'.format(str(e)))
