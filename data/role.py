import sqlalchemy
from sqlalchemy import orm, func
from werkzeug.security import generate_password_hash, check_password_hash

from .db_session import SqlAlchemyBase


class Role(SqlAlchemyBase):
    __tablename__ = 'roles'

    role = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False, unique=True)
