from pydantic import BaseModel
from scripts.auth.security import validate_token
from fastapi import Depends
from fastapi import APIRouter
from scripts.database.helper import *


class OrderModel(BaseModel):
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
    date: str


router = APIRouter()


@router.post("", dependencies=[Depends(validate_token)])
def get_data_order(
        order_code: str,
        created_at: str, sent_at: str, order_status: str,
        carrier_id: int, carrier_status: str,
        sender_province: str, sender_district: str,
        receiver_province: str, receiver_district: str,
        delivery_count: int, pickup: str,
        barter: str, carrier_delivered_at: str,
        picked_at: str, last_delivering_at: str, carrier_updated_at: str,
        date: str,
):
    order_dict = {
        'order_code': order_code,
        'created_at': created_at,
        'sent_at': sent_at,
        'order_status': order_status,
        'carrier_id': carrier_id,
        'carrier_status': carrier_status,
        'sender_province': sender_province,
        'sender_district': sender_district,
        'receiver_province': receiver_province,
        'receiver_district': receiver_district,
        'delivery_count': delivery_count,
        'pickup': pickup,
        'barter': barter,
        'carrier_delivered_at': carrier_delivered_at,
        'picked_at': picked_at,
        'last_delivering_at': last_delivering_at,
        'carrier_updated_at': carrier_updated_at,
        'date': date,
    }

    insert_data_to_postgres(data=[order_dict], schema_name='db_schema', table_name='order')

    return {
        'error': False,
        'message': "",
        'data': {
            'count': 1,
            'order': OrderModel(**order_dict),
        },
    }
