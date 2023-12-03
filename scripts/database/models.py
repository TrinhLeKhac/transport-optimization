from scripts.database.database import Base
from sqlalchemy import String, Boolean, Integer, Column, Numeric, Date, TIMESTAMP


class Output29946API(Base):
    __tablename__ = "tbl_data_api"
    id = Column(Integer, primary_key=True)
    receiver_province_code = Column(String, nullable=True)
    receiver_district_code = Column(String, nullable=True)
    carrier_id = Column(Integer, nullable=False)
    new_type = Column(String, nullable=False)
    route_type = Column(String, nullable=False)
    status = Column(String, default=False)
    description = Column(String, nullable=False)
    time_data = Column(Numeric(5, 2), nullable=False)
    time_display = Column(String, nullable=False)
    speed_ranking = Column(Integer, nullable=False)
    score_ranking = Column(Integer, nullable=False)
    for_shop = Column(Integer, nullable=False)
    total_order = Column(Integer, nullable=False)
    # rate_ranking = Column(Integer, nullable=False)
    rate = Column(Numeric(5, 2), nullable=False)
    score = Column(Numeric(3, 2), nullable=False)
    star = Column(Numeric(2, 1), nullable=False)
    # import_date = Column(String, nullable=False)

    __table_args__ = {'schema': 'db_schema'}

    def __repr__(self):
        return f"<Result API from date={self.import_time}"


