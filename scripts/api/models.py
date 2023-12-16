from sqlalchemy import String, Integer, Column, Numeric
from sqlalchemy.types import ARRAY
from scripts.api.database import Base


class MessageZNS(Base):
    __table__ = "zns"
    id = Column(Integer, primary_key=True, index=True)
    receiver_province = Column(String, nullable=False)
    receiver_district = Column(String, nullable=False)
    carrier_id = Column(Integer, nullable=False)
    message_count = Column(Integer, nullable=False)
    star = Column(Integer, nullable=False)
    feedbacks = Column(ARRAY[String], nullable=True)
    note = Column(String, nullable=True)
    submitted_at = Column(String, nullable=False)
    date = Column(String, nullable=False)


class Order(Base):
    __table__ = "order"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(String, nullable=False)
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

