import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase
from .region import Region
from .working_hour import WorkingHour


class Courier(SqlAlchemyBase):
    __tablename__ = 'couriers'

    courier_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)

    courier_type = sqlalchemy.Column(sqlalchemy.String, nullable=False)

    regions = orm.relation("Region", back_populates='courier')
    working_hours = orm.relation("WorkingHour", back_populates='courier')

    def update_regions(self, regions, session):
        session.query(Region).filter(Region.courier_id == self.courier_id).delete()
        for i in regions:
            session.add(Region(region=i, courier_id=self.courier_id))
        session.commit()

    def update_working_hours(self, hours, session):
        session.query(WorkingHour).filter(WorkingHour.courier_id == self.courier_id).delete()
        for i in hours:
            session.add(WorkingHour(working_hour=i, courier_id=self.courier_id))
        session.commit()

    def get_rating(self, session):
        return 0

    def get_earning(self, session):
        return 0
