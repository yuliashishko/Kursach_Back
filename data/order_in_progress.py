import sqlalchemy
from sqlalchemy import orm

from utils import BASE_COMPLETE_TIME
from .db_session import SqlAlchemyBase


class OrderInProgress(SqlAlchemyBase):
    __tablename__ = 'orders_in_progress'
    order_in_progress_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)

    order_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("orders.order_id"))
    courier_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("couriers.courier_id"))
    assign_time = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False)
    complete_time = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True)
    courier_type = sqlalchemy.Column(sqlalchemy.String)
    duration = sqlalchemy.Column(sqlalchemy.Integer, default=0)

    order = orm.relation("Order")
    courier = orm.relation("Courier")

    def set_duration(self, session):
        prev = session.query(OrderInProgress).filter(OrderInProgress.courier_id == self.courier_id,
                                                     OrderInProgress.complete_time != BASE_COMPLETE_TIME,
                                                     OrderInProgress.complete_time <= self.complete_time,
                                                     OrderInProgress.order_id != self.order_id).all()
        if prev:
            mx = max(prev, key=lambda s: s.complete_time)
            dif = self.complete_time - mx.complete_time
        else:
            dif = self.complete_time - self.assign_time
        self.duration = dif.seconds + dif.days * 3600 * 24
        print()
