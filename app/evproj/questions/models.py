from sqlalchemy import (Column, Integer, String, ForeignKey,
                        DateTime, Boolean, UniqueConstraint)
from sqlalchemy.dialects.postgresql import ENUM, UUID

from datetime import datetime

from ..db import get_session, Base
from ..db.models import User


Permissions = ENUM('all', 'experts', 'some_experts', name='permissions')


class Question(Base):
    __tablename__ = 'questions'

    id = Column(Integer, primary_key=True)
    author = Column(Integer, ForeignKey('users.id'), nullable=False)
    question = Column(String(128), nullable=False)
    desc = Column(String(1024), nullable=False)
    created = Column(DateTime, default=datetime.utcnow, nullable=False)
    views = Column(Integer, default=0, nullable=False)
    # comments
    # modifed
    # modifed_date
    # modifed_by
    # warns
    # areas
    # files
    rating = Column(Integer, default=0, nullable=False)
    perms = Column(Permissions, default='all', nullable=False)  # приватность (все, только эксперты, только эксперты выбранных областей)
    archived = Column(Boolean, default=False, nullable=False)

    def get_author_name(self):
        author = None
        with get_session() as s:
            author = s.query(User).filter_by(id=self.author).first()
        return '{} {}'.format(author.name, author.surname)

    def increase_views(self):
        with get_session() as s:
            self.views += 1
            s.add(self)
