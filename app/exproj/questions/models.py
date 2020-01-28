from sqlalchemy import (Column, Integer, String, ForeignKey,
                        DateTime, Boolean, UniqueConstraint)
from sqlalchemy.dialects.postgresql import ENUM, UUID
from sqlalchemy.orm import relationship, backref

from datetime import datetime

from exproj.db import Base, get_session


Permissions = ENUM('all', 'experts', 'some_experts', name='permissions')


class Question(Base):
    __tablename__ = 'questions'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    question = Column(String(128), nullable=False)
    desc = Column(String(1024), nullable=False)
    create_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    views = Column(Integer, default=0, nullable=False)
    # answers
    # modifed (bool)
    # modify_time
    # modifed_by
    # warns
    # areas
    # files
    # voted_up
    # voted_down
    voices = Column(Integer, default=0, nullable=False)
    perms = Column(Permissions, default='all', nullable=False)  # приватность (все, только эксперты, только эксперты выбранных областей)
    archived = Column(Boolean, default=False, nullable=False)

    author = relationship('User', backref=backref('questions', lazy='dynamic'))

    def get_author_name(self):
        with get_session() as s:
            q = s.query(Question).get(self.id)
            return '{} {}'.format(q.author.name, q.author.surname)

    def increase_views(self):
        with get_session() as s:
            self.views += 1
            s.add(self)


class Answer(Base):
    __tablename__ = 'answers'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    q_id = Column(Integer, ForeignKey('questions.id'), nullable=False)
    create_time = Column(Integer, default=datetime.utcnow(), nullable=False)
    text = Column(String, nullable=False)
    voices = Column(Integer, default=0, nullable=False)