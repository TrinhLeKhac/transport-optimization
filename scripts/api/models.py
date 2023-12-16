from sqlalchemy import String, Integer, Column, Numeric
from sqlalchemy.types import ARRAY
from scripts.api.database import Base


class MessageZNS(Base):
    __tablename__ = "zns"

    id = Column(Integer, primary_key=True, autoincrement=True)
    receiver_province = Column(String, nullable=False)
    receiver_district = Column(String, nullable=False)
    carrier_id = Column(Integer, nullable=False)
    message_count = Column(Integer, nullable=False)
    star = Column(Integer, nullable=False)
    feedbacks = Column(ARRAY(String), nullable=True)
    note = Column(String, nullable=True)
    submitted_at = Column(String, nullable=False)
    date = Column(String, nullable=False)

    __table_args__ = {"schema": "db_schema"}


class Order(Base):
    __tablename__ = "order"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_code = Column(String, nullable=False)
    created_at = Column(String, nullable=False)
    weight = Column(Integer, nullable=False)
    sent_at = Column(String, nullable=False)
    order_status = Column(String, nullable=False)
    carrier_id = Column(Integer, nullable=False)
    carrier_status = Column(String, nullable=False)
    sender_province = Column(String, nullable=False)
    sender_district = Column(String, nullable=False)
    receiver_province = Column(String, nullable=False)
    receiver_district = Column(String, nullable=False)
    delivery_count = Column(Integer, nullable=False)
    pickup = Column(String, nullable=False)
    barter = Column(String, nullable=False)
    carrier_delivered_at = Column(String, nullable=True)
    picked_at = Column(String, nullable=False)
    last_delivering_at = Column(String, nullable=True)
    carrier_updated_at = Column(String, nullable=False)
    date = Column(String, nullable=False)

    __table_args__ = {"schema": "db_schema"}


class API(Base):
    __tablename__ = "tbl_data_api"

    id = Column(Integer, primary_key=True, autoincrement=True)
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
    rate_ranking = Column(Integer, nullable=False)
    rate = Column(Numeric(5, 2), nullable=False)
    score = Column(Numeric(3, 2), nullable=False)
    star = Column(Numeric(2, 1), nullable=False)
    import_date = Column(String, nullable=False)

    __table_args__ = {'schema': 'db_schema'}
