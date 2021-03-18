import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class WorkingHour(SqlAlchemyBase):
    __tablename__ = 'working_hours'

    working_hour_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)

    working_hour = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    courier_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("couriers.courier_id"))

    courier = orm.relation("Courier")
