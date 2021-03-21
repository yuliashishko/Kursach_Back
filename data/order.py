import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase



class Order(SqlAlchemyBase):
    __tablename__ = 'orders'
    order_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)

    weight = sqlalchemy.Column(sqlalchemy.Float, nullable=False)
    region = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)

    delivery_hours = orm.relation("DeliveryHour", back_populates='order')
