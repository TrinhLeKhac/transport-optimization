from typing import Union
from pydantic import BaseModel, conint, constr, confloat
from typing import List


class LoginModel(BaseModel):
    username: constr(strict=True)
    password: constr(strict=True)


class MessageZNSModel(BaseModel):
    receiver_province: constr(max_length=2, strict=True)
    receiver_district: constr(max_length=3, strict=True)
    carrier_id: conint(strict=True)
    message_count: conint(strict=True)
    star: conint(ge=0, le=5, strict=True)
    feedbacks: Union[List[constr(max_length=256, strict=True)], None] = None
    note: Union[constr(max_length=256, strict=True), None] = None
    submitted_at: constr(max_length=20, strict=True)
    date: constr(max_length=10, strict=True)

    class Config:
        from_attributes = True


class OrderModel(BaseModel):
    order_code: constr(max_length=30, strict=True)
    created_at: constr(max_length=20, strict=True)
    weight: conint(gt=0, strict=True)
    sent_at: constr(max_length=20, strict=True)
    order_status: constr(max_length=256, strict=True)
    carrier_id: conint(strict=True)
    carrier_status: constr(max_length=256, strict=True)
    sender_province: constr(max_length=2, strict=True)
    sender_district: constr(max_length=3, strict=True)
    receiver_province: constr(max_length=2, strict=True)
    receiver_district: constr(max_length=3, strict=True)
    delivery_count: conint(strict=True)
    pickup: constr(max_length=1, strict=True)
    barter: constr(max_length=1, strict=True)
    carrier_delivered_at: Union[constr(max_length=20, strict=True), None] = None
    picked_at: constr(max_length=20, strict=True)
    last_delivering_at: Union[constr(max_length=20, strict=True), None] = None
    carrier_updated_at: constr(max_length=20, strict=True)
    date: constr(max_length=10, strict=True)

    class Config:
        from_attributes = True


class APIModel(BaseModel):
    province_code: constr(max_length=2, strict=True)
    district_code: constr(max_length=3, strict=True)
    carrier_id: conint(strict=True)
    route_type: constr(max_length=1, strict=True)
    new_type: constr(max_length=2, strict=True)
    status: constr(max_length=1, strict=True)
    description: constr(max_length=512, strict=True)
    time_data: confloat(ge=0, le=100.00, strict=True)
    time_display: constr(max_length=30, strict=True)
    rate: confloat(ge=0, le=100.00, strict=True)
    score: confloat(ge=0, le=5.00, strict=True)
    star: confloat(ge=0, le=5.0, strict=True)
    for_shop: conint(strict=True)
    for_partner: conint(strict=True)
    speed_ranking: conint(strict=True)
    score_ranking: conint(strict=True)

    class Config:
        from_attributes = True


class SuggestCarrierInput(BaseModel):
    sender_province: constr(max_length=2, strict=True)
    sender_district: constr(max_length=3, strict=True)
    receiver_province: constr(max_length=2, strict=True)
    receiver_district: constr(max_length=3, strict=True)
    weight: conint(gt=0, le=50000, strict=True)
    pickup: constr(max_length=1, strict=True)


class SuggestCarrierInputFinal(BaseModel):
    sender_province: constr(max_length=2, strict=True)
    sender_district: constr(max_length=3, strict=True)
    receiver_province: constr(max_length=2, strict=True)
    receiver_district: constr(max_length=3, strict=True)
    weight: conint(gt=0, le=50000, strict=True)
    collection: conint(ge=0, strict=True)
    value: conint(ge=0, strict=True)
    barter: constr(max_length=1, strict=True)
    pickup: constr(max_length=1, strict=True)


class Price(BaseModel):
    id: constr(max_length=2, strict=True)
    value: conint(gt=0, strict=True)


class PriceList(BaseModel):
    items: List[Price]


class SuggestCarrierInputSuper(BaseModel):
    sender_province: constr(max_length=2, strict=True)
    sender_district: constr(max_length=3, strict=True)
    receiver_province: constr(max_length=2, strict=True)
    receiver_district: constr(max_length=3, strict=True)
    price: PriceList
    weight: conint(gt=0, le=50000, strict=True)
    pickup: constr(max_length=1, strict=True)


class SuggestCarrierOutput(BaseModel):
    carrier_id: int
    route_type: constr(max_length=1, strict=True)
    price: int
    status: constr(max_length=1, strict=True)
    description: constr(max_length=512, strict=True)
    time_data: confloat(ge=0, le=100.00, strict=True)
    time_display: constr(max_length=30, strict=True)
    rate: confloat(ge=0, le=100.00, strict=True)
    score: confloat(ge=0, le=5.00, strict=True)
    star: confloat(ge=0, le=5.0, strict=True)
    for_shop: int
    for_partner: int
    price_ranking: int
    speed_ranking: int
    score_ranking: int
