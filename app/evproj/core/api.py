from .. import cfg
from ..db import *
from . import auth
from .exceptions import NotJsonError, NoData
from sqlalchemy.exc import IntegrityError
from sqlalchemy import desc
from . import util
from datetime import datetime
import requests
import logging
import os
from types import SimpleNamespace


def register_user(mail, name, surname, password, lvl=2):
    with get_session() as s:
        user = s.query(User).filter(
                User.mail == mail,
                User.status == 'deleted',
        ).one_or_none()

        # checking unique link
        confirmation_link = ''
        while True:
            confirmation_link = util.random_string_digits(50)
            exists = s.query(User).filter(
                    User.confirmation_link == confirmation_link
            ).one_or_none()
            if not exists:
                break

        if user:
            user.status = cfg.DEFAULT_USER_STATUS
            user.confirmation_link = confirmation_link
            user.lvl = lvl
        else:
            user = User(mail=mail, name=name,
                        surname=surname, password=password,
                        lvl=lvl, confirmation_link=confirmation_link)
            s.add(user)
        if cfg.DEFAULT_USER_STATUS == 'unconfirmed':
            util.send_email(mail, confirmation_link)
        logging.info('Registering new user [{}]'.format(mail))


def confirm_user(confirmation_link):
    with get_session() as s:
        user = s.query(User).filter(
                User.confirmation_link == confirmation_link,
                User.status == 'unconfirmed',
        ).one_or_none()
        if user:
            user.status = 'active'
            logging.info('User [{}] is confirmed'.format(user.mail))
            return 'user confirmed'
        else:
            return 'user is currently confirmed by this link'


def get_events():
    result = {}
    with get_session() as s:
        events = s.query(Event).all()

        for event in events:
            result[event.id] = {
                'id': event.id,
                'name': event.name,
                'sm_description': event.sm_description,
                'date_time': event.date_time,
            }
    return result


def get_id_by_mail(mail):
    with get_session() as s:
        user = s.query(User).filter(
                User.mail == mail,
                User.status == 'active'
        ).first()

        if user:
            return user.id
        else:
            return -1


def create_event(name, sm_description, description, date_time, phone, mail):
    timedate = date_time.split('-')
    time_date = datetime(int(timedate[0]), int(timedate[1]), int(timedate[2]),
                         int(timedate[3]), int(timedate[4]), 0, 0)
    with get_session() as s:
        last_event = s.query(Event).order_by(Event.id.desc()).first()
        event = Event(name=name, sm_description=sm_description,
                      description=description, date_time=time_date,
                      phone=phone, mail=mail)
        s.add(event)
        logging.info('Creating event [{}] [{}]'.format(name, sm_description))
        if last_event:
            return last_event.id + 1
        else:
            return 1


def create_event_creator(creator, last_id):
    with get_session() as s:
        participation = Participation(event=last_id, participant=creator,
                                      participation_level='creator',
                                      participation_status='confirmed')
        s.add(participation)


def create_event_presenters(presenters, last_id):
    users = presenters.replace(" ", "").split(',')
    with get_session() as s:
        for user in users:
            us = s.query(User).filter(User.mail == user).first().id
            participation = Participation(event=last_id, participant=us,
                                          participation_level='presenter',
                                          participation_status='confirmed')
            s.add(participation)


def get_event_info(id):
    with get_session() as s:
        event = s.query(Event).filter(
                Event.id == id,
        ).one_or_none()

        return event


def check_participation(user_id, event_id):
    with get_session() as s:
        participation = s.query(Participation).filter(
                Participation.event == event_id,
                Participation.participant == user_id
        ).one_or_none()
        if participation:
            return participation.participation_level
        else:
            return 'not joined'


def get_participators(id):
    result = {}
    with get_session() as s:
        users = s.query(User, Participation).filter(
                User.id == Participation.participant,
                Participation.event == id
        ).all()

        i = 1
        for user, participant in users:
            if participant.participation_level == 'creator':
                result[i] = {
                    'name': user.name,
                    'surname': user.surname,
                    'participation_level': participant.participation_level,
                }
                i += 1
        for user, participant in users:
            if participant.participation_level == 'presenter':
                result[i] = {
                    'name': user.name,
                    'surname': user.surname,
                    'participation_level': participant.participation_level,
                }
                i += 1

    return result


def get_stat(event_id):
    with get_session() as s:
        confirmed_users = s.query(Participation).filter(
                Participation.event == event_id,
                Participation.participation_level == 'guest',
                Participation.participation_status == 'confirmed'
        ).count()

        unconfirmed_users = s.query(Participation).filter(
                Participation.event == event_id,
                Participation.participation_level == 'guest',
                Participation.participation_status == 'declined'
        ).count()

        return confirmed_users, unconfirmed_users


def get_user_stat(user_id):
    result_creator = {}
    result_presenter = {}
    result_guest = {}
    with get_session() as s:
        as_creator = s.query(Participation, Event).filter(
                Participation.event == Event.id,
                Participation.participant == user_id,
                Participation.participation_level == 'creator'
        ).all()

        for participant, event in as_creator:
            result_creator[event.id] = {
                'id': event.id,
                'name': event.name,
                'date': event.date_time,
            }

        as_presenter = s.query(Participation, Event).filter(
                Participation.event == Event.id,
                Participation.participant == user_id,
                Participation.participation_level == 'presenter'
        ).all()

        for participant, event in as_presenter:
            result_presenter[event.id] = {
                'id': event.id,
                'name': event.name,
                'date': event.date_time,
            }

        as_guest = s.query(Participation, Event).filter(
                Participation.event == Event.id,
                Participation.participant == user_id,
                Participation.participation_level == 'guest',
                Participation.participation_status == 'confirmed'
        ).all()

        for participant, event in as_guest:
            result_guest[event.id] = {
                'id': event.id,
                'name': event.name,
                'date': event.date_time,
            }

    return result_creator, result_presenter, result_guest


def guest_join(user_id, event_id):
    with get_session() as s:
        is_consists = s.query(Participation).filter(
                Participation.participant == user_id,
                Participation.event == event_id
        ).one_or_none()

        if not is_consists:
            participation = Participation(event=event_id, participant=user_id,
                                          participation_level='guest',
                                          participation_status='unknown')
            s.add(participation)
        logging.info('User [id {}] joined event [id {}]'.format(user_id,
                                                                event_id))


def guest_action(user_id, event_id, action):
    with get_session() as s:
        part = s.query(Participation).filter(
            Participation.event == event_id,
            Participation.participant == user_id,
            Participation.participation_status == 'unknown'
        ).first()
        setattr(part, 'participation_status', action)
        s.commit()
        logging.info('User [id {}] is [{}] in event [id {}]'.format(user_id,
                                                                    action,
                                                                    event_id))


def get_uncorfimed_users(event_id):
    result = {}
    with get_session() as s:
        users = s.query(User, Participation).filter(
                User.id == Participation.participant,
                Participation.event == event_id,
                Participation.participation_status == 'unknown'
        ).all()

        for user, _ in users:
            result[user.id] = {
                'id': user.id,
                'name': user.name,
                'surname': user.surname,
            }

    return result


def event_exist(event_id):
    with get_session() as s:
        exists = s.query(Event).filter(
                Event.id == event_id
        ).count()
    return True if exists > 0 else False


# restapi

def event_info(id):
    with get_session() as s:
        event = s.query(Event, Participation, User).filter(
                Event.id == id,
                Participation.event == Event.id,
                Participation.participant == User.id,
                Participation.participation_level == 'creator'
        ).first()

        return {
            "creator_mail": event.User.mail,
            "creator_name": event.User.name,
            "creator_surname": event.User.surname,
            "name": event.Event.name,
            "sm_description": event.Event.sm_description,
            "description": event.Event.description,
            "date_time": event.Event.date_time,
            "phone": event.Event.phone
        }    


def get_user_info(id):
    result_creator = {}
    result_presenter = {}
    result_guest = {}
    with get_session() as s:
        as_creator = s.query(Participation, Event).filter(
                Participation.event == Event.id,
                Participation.participant == user_id,
                Participation.participation_level == 'creator'
        ).all()

        for participant, event in as_creator:
            result_creator[event.id] = {
                'id': event.id,
                'name': event.name,
                'date': event.date_time,
            }

        as_presenter = s.query(Participation, Event).filter(
                Participation.event == Event.id,
                Participation.participant == user_id,
                Participation.participation_level == 'presenter'
        ).all()

        for participant, event in as_presenter:
            result_presenter[event.id] = {
                'id': event.id,
                'name': event.name,
                'date': event.date_time,
            }

        as_guest = s.query(Participation, Event).filter(
                Participation.event == Event.id,
                Participation.participant == user_id,
                Participation.participation_level == 'guest',
                Participation.participation_status == 'confirmed'
        ).all()

        for participant, event in as_guest:
            result_guest[event.id] = {
                'id': event.id,
                'name': event.name,
                'date': event.date_time,
            }

    return result_creator, result_presenter, result_guest
