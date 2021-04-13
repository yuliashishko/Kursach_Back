import sqlalchemy
from sqlalchemy import orm, func

from utils import BASE_COMPLETE_TIME
from .db_session import SqlAlchemyBase
from .order import Order
from .order_in_progress import OrderInProgress
from .region import Region
from .working_hour import WorkingHour


class Courier(SqlAlchemyBase):
    __tablename__ = 'couriers'

    courier_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)

    courier_type = sqlalchemy.Column(sqlalchemy.String, nullable=False)

    regions = orm.relation("Region", back_populates='courier')
    working_hours = orm.relation("WorkingHour", back_populates='courier')
    orders = orm.relation("OrderInProgress", back_populates='courier')

    def update_regions(self, regions, session):
        session.query(Region).filter(Region.courier_id == self.courier_id).delete()
        for i in regions:
            session.add(Region(region=i, courier_id=self.courier_id))
        session.commit()

    def update_working_hours(self, hours, session):
        session.query(WorkingHour).filter(WorkingHour.courier_id == self.courier_id).delete()
        for i in hours:
            hour = WorkingHour(courier_id=self.courier_id)
            hour.set_working_hour(i)
            session.add(hour)
        session.commit()

    def get_rating(self, session):
        res = session.query(func.avg(OrderInProgress.duration)).join(Order).filter(
            OrderInProgress.complete_time != BASE_COMPLETE_TIME,
            OrderInProgress.courier_id == self.courier_id).group_by(Order.region).all()
        mn = min(res)[0]
        rating = (60 * 60 - min(mn, 60 * 60)) / (60 * 60) * 5
        return rating

    def get_earning(self, session):
        coeff = {'foot': 2, 'bike': 5, 'car': 9}
        earning = 0
        complete_orders = session.query(OrderInProgress).filter(OrderInProgress.courier_id == self.courier_id,
                                                                OrderInProgress.complete_time != BASE_COMPLETE_TIME).all()
        for order in complete_orders:
            earning += 500 * coeff[order.courier_type]
        return earning
