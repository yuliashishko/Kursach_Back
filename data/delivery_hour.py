import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class DeliveryHour(SqlAlchemyBase):
    __tablename__ = 'delivery_hours'

    delivery_hour_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)

    delivery_hour = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    order_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("orders.order_id"))

    order = orm.relation("Order")
