import sqlalchemy as sa

from database import Base


class User(Base):
    __tablename__ = 'users'

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    username = sa.Column(sa.String, nullable=False)
    email = sa.Column(sa.String, nullable=False, unique=True)
    hashed_password = sa.Column(sa.String, nullable=False)
    created_at = sa.Column(sa.DateTime)
    updated_at = sa.Column(sa.DateTime)