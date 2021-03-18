import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class Region(SqlAlchemyBase):
    __tablename__ = 'regions'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)

    region = sqlalchemy.Column(sqlalchemy.Integer)
    courier_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("couriers.courier_id"))

    courier = orm.relation("Courier")
