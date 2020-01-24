from sqlalchemy import (Column, Integer, String, ForeignKey,
                        DateTime, Boolean, UniqueConstraint)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import ENUM, UUID
from flask_login import UserMixin

from datetime import datetime
import uuid

from .. import cfg


Base = declarative_base()


Status = ENUM('active', 'deleted',
              name='status')
User_status = ENUM('unconfirmed', 'active', 'deleted', 'banned',
                   name='user_status')
Event_status = ENUM('unconfirmed', 'future', 'past',
                    name='event_status')
Participation_level = ENUM('creator', 'presenter', 'guest',
                           name='participation_level')
Participation_status = ENUM('unknown', 'confirmed', 'declined',
                            name='participation_status')


class User(Base, UserMixin):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    mail = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    password = Column(String, nullable=False)
    cookie_id = Column(UUID(as_uuid=True), default=uuid.uuid4,
                       unique=True, nullable=False)
    lvl = Column(Integer, default=2, nullable=False)
    status = Column(User_status, default=cfg.DEFAULT_USER_STATUS, nullable=False)
    confirmation_link = Column(String, nullable=False)

    def get_id(self):
        return self.cookie_id


class Event(Base):
    __tablename__ = 'events'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    sm_description = Column(String, nullable=False)
    description = Column(String, nullable=False)
    created = Column(DateTime, default=datetime.utcnow, nullable=False)
    date_time = Column(DateTime, nullable=False)
    # questionable
    phone = Column(String, nullable=False)
    mail = Column(String, nullable=False)


class Participation(Base):
    __tablename__ = 'participations'

    id = Column(Integer, primary_key=True)
    event = Column(Integer, ForeignKey('events.id'), nullable=False)
    participant = Column(Integer, ForeignKey('users.id'), nullable=False)
    participation_level = Column(Participation_level, default='guest', nullable=False)
    participation_status = Column(Participation_status, default='unknown', nullable=False)
