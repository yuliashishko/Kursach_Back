from datetime import datetime

import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class DeliveryHour(SqlAlchemyBase):
    __tablename__ = 'delivery_hours'

    delivery_hour_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)

    start = sqlalchemy.Column(sqlalchemy.Time, nullable=False)
    end = sqlalchemy.Column(sqlalchemy.Time, nullable=False)
    delivery_hour = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    order_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("orders.order_id"))

    order = orm.relation("Order")

    def set_delivery_hour(self, delivery_hour: str):
        begin, end = delivery_hour.split('-')
        hours, minutes = map(int, begin.split(':'))
        self.start = datetime.time(hours, minutes, 0)
        hours, minutes = map(int, end.split(':'))
        self.end = datetime.time(hours, minutes, 0)
