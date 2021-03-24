import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class OrderInProgress(SqlAlchemyBase):
    __tablename__ = 'orders_in_progress'
    order_in_progress_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)

    order_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("orders.order_id"))
    courier_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("couriers.courier_id"))
    assign_time = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False)
    complete_time = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True)

    order = orm.relation("Order")
    courier = orm.relation("Courier")
