from pydantic import BaseModel
from scripts.auth.security import validate_token
from fastapi import Depends
from fastapi import APIRouter
from scripts.database.helper import *


class OrderModel(BaseModel):
    date: str
    order_code: str
    created_at: str
    sent_at: str
    order_status: str
    carrier_id: int
    carrier_status: str
    sender_province: str
    sender_district: str
    receiver_province: str
    receiver_district: str
    delivery_count: int
    pickup: str
    barter: str
    carrier_delivered_at: str
    picked_at: str
    last_delivering_at: str
    carrier_updated_at: str


router = APIRouter()


@router.post("", dependencies=[Depends(validate_token)])
def get_data_order(request_data: OrderModel):
    data = request_data.model_dump()
    insert_data_to_postgres(data=[data], schema_name="db_schema", table_name="order")

    return {
        "error": False,
        "message": "",
        "data": {
            "count": 1,
            "order": data,
        },
    }
