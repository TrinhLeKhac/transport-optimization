from typing import Union, List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.sqltypes import Numeric
from sqlalchemy.types import ARRAY

from sqlalchemy import (
    Integer,
    PrimaryKeyConstraint,
    String, select,
)
from sqlalchemy.orm import Mapped, mapped_column
from scripts.api.base import Base


class MessageZNS(Base):
    __tablename__ = "zns"

    id: Mapped[int] = mapped_column(Integer, autoincrement=True)
    receiver_province: Mapped[str] = mapped_column(String(2))
    receiver_district: Mapped[str] = mapped_column(String(3))
    carrier_id: Mapped[int] = mapped_column(Integer)
    message_count: Mapped[int] = mapped_column(Integer)
    star: Mapped[int] = mapped_column(Integer)
    feedbacks: Mapped[Union[List[str], None]] = mapped_column(ARRAY(String(256)))
    note: Mapped[Union[str, None]] = mapped_column(String(256))
    submitted_at: Mapped[str] = mapped_column(String(20))
    date: Mapped[str] = mapped_column(String(10))

    __table_args__ = (PrimaryKeyConstraint("id", name="message_zns_pkey"), {"schema": "db_schema"})


class NGN(Base):
    __tablename__ = "tbl_ngung_giao_nhan_rev"

    id: Mapped[int] = mapped_column(Integer, autoincrement=True)
    province: Mapped[str] = mapped_column(String(2))
    district: Mapped[str] = mapped_column(String(3))
    carrier_id: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(30))

    # __table_args__ = (PrimaryKeyConstraint("id", name="tbl_ngung_giao_nhan_rev_pkey"), {"schema": "db_schema"})


class NGNLV3(Base):
    __tablename__ = "tbl_ngung_giao_nhan_level_3_rev"

    id: Mapped[int] = mapped_column(Integer, autoincrement=True)
    province: Mapped[str] = mapped_column(String(2))
    district: Mapped[str] = mapped_column(String(3))
    commune: Mapped[str] = mapped_column(String(5))
    carrier_id: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(30))

    # __table_args__ = (PrimaryKeyConstraint("id", name="tbl_ngung_giao_nhan_level_3_rev_pkey"), {"schema": "db_schema"})


class Order(Base):
    __tablename__ = "order"

    id: Mapped[int] = mapped_column(Integer, autoincrement=True)
    order_code: Mapped[str] = mapped_column(String(30))
    created_at: Mapped[str] = mapped_column(String(20))
    weight: Mapped[int] = mapped_column(Integer)
    sent_at: Mapped[str] = mapped_column(String(20))
    order_status: Mapped[str] = mapped_column(String(256))
    carrier_id: Mapped[int] = mapped_column(Integer)
    carrier_status: Mapped[str] = mapped_column(String(256))
    sender_province: Mapped[str] = mapped_column(String(2))
    sender_district: Mapped[str] = mapped_column(String(3))
    receiver_province: Mapped[str] = mapped_column(String(2))
    receiver_district: Mapped[str] = mapped_column(String(3))
    delivery_count: Mapped[int] = mapped_column(Integer)
    pickup: Mapped[str] = mapped_column(String(1))
    barter: Mapped[str] = mapped_column(String(1))
    carrier_delivered_at: Mapped[Union[str, None]] = mapped_column(String(20))
    picked_at: Mapped[str] = mapped_column(String(20))
    last_delivering_at: Mapped[Union[str, None]] = mapped_column(String(20))
    carrier_updated_at: Mapped[str] = mapped_column(String(20))
    date: Mapped[str] = mapped_column(String(10))

    __table_args__ = (PrimaryKeyConstraint("id", name="order_pkey"), {"schema": "db_schema"})


class API(Base):
    __tablename__ = "tbl_data_api"

    id: Mapped[int] = mapped_column(Integer, autoincrement=True)
    receiver_province_code: Mapped[str] = mapped_column(String(2))
    receiver_district_code: Mapped[str] = mapped_column(String(3))
    carrier_id: Mapped[int] = mapped_column(Integer)
    new_type: Mapped[str] = mapped_column(String(2))
    route_type: Mapped[str] = mapped_column(String(1))
    status: Mapped[str] = mapped_column(String(1))
    description: Mapped[str] = mapped_column(String(512))
    time_data: Mapped[float] = mapped_column(Numeric(5, 2))
    time_display: Mapped[str] = mapped_column(String(30))
    rate: Mapped[float] = mapped_column(Numeric(5, 2))
    score: Mapped[float] = mapped_column(Numeric(3, 2))
    star: Mapped[float] = mapped_column(Numeric(2, 1))
    for_shop: Mapped[int] = mapped_column(Integer)
    speed_ranking: Mapped[int] = mapped_column(Integer)
    score_ranking: Mapped[int] = mapped_column(Integer)
    # total_order: Mapped[int] = mapped_column(Integer)
    # rate_ranking: Mapped[int] = mapped_column(Integer)
    import_date: Mapped[str] = mapped_column(String(10))

    __table_args__ = (PrimaryKeyConstraint("id", name="data_api_pkey"), {"schema": "db_schema"})
