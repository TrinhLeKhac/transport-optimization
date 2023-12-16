from typing import Union
from pydantic import BaseModel, conint, constr, confloat
from typing import List


class LoginModel(BaseModel):
    username: constr(strict=True)
    password: constr(strict=True)


class MessageZNSModel(BaseModel):
    date: constr(strict=True)
    receiver_province: constr(strict=True)
    receiver_district: constr(strict=True)
    carrier_id: conint(strict=True)
    message_count: conint(strict=True)
    star: conint(ge=0, le=5, strict=True)
    feedbacks: Union[List[constr(strict=True)], None] = None
    note: Union[constr(strict=True), None] = None
    submitted_at: constr(strict=True)

    class Config:
        orm_mode = True


class OrderModel(BaseModel):
    date: constr(strict=True)
    order_code: constr(strict=True)
    created_at: constr(strict=True)
    weight: conint(gt=0, strict=True)
    sent_at: constr(strict=True)
    order_status: constr(strict=True)
    carrier_id: conint(strict=True)
    carrier_status: constr(strict=True)
    sender_province: constr(strict=True)
    sender_district: constr(strict=True)
    receiver_province: constr(strict=True)
    receiver_district: constr(strict=True)
    delivery_count: conint(strict=True)
    pickup: constr(strict=True)
    barter: constr(strict=True)
    carrier_delivered_at: Union[constr(strict=True), None] = None
    picked_at: constr(strict=True)
    last_delivering_at: Union[constr(strict=True), None] = None
    carrier_updated_at: constr(strict=True)

    class Config:
        orm_mode = True


class APIRequestModel(BaseModel):
    sender_province: constr(strict=True)
    sender_district: constr(strict=True)
    receiver_province: constr(strict=True)
    receiver_district: constr(strict=True)
    weight: conint(strict=True, gt=0, le=50000)
    pickup: constr(strict=True)


class APIResultModel(BaseModel):
    carrier_id: int
    route_type: constr(strict=True)
    price: int
    status: constr(strict=True)
    description: constr(strict=True)
    time_data: confloat(strict=True)
    time_display: constr(strict=True)
    rate: confloat(strict=True)
    score: confloat(strict=True)
    star: confloat(strict=True)
    for_shop: int
    for_partner: int
    price_ranking: int
    speed_ranking: int
    score_ranking: int

    class Config:
        orm_mode = True