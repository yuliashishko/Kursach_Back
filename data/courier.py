import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Courier(SqlAlchemyBase):
    __tablename__ = 'couriers'

    courier_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)

    courier_type = sqlalchemy.Column(sqlalchemy.String, nullable=False)

    regions = orm.relation("Region", back_populates='courier')
    working_hours = orm.relation("WorkingHour", back_populates='courier')

