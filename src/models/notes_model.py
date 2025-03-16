import sqlalchemy as sa
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy_continuum import make_versioned

from database import Base

make_versioned(user_cls=None)


class Note(Base):
    __versioned__ = {}
    __tablename__ = 'notes'

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    title = sa.Column(sa.String, nullable=False, unique=True)
    content = sa.Column(sa.TEXT, nullable=False)
    priority = sa.Column(sa.Integer, nullable=False)
    user_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('users.id'),
        nullable=False)
    user = relationship('User', back_populates="notes")
    created_at = sa.Column(sa.DateTime, server_default=func.now())
    updated_at = sa.Column(
        sa.DateTime,
        server_default=func.now(),
        onupdate=func.now())


sa.orm.configure_mappers()
