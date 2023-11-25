from pydantic import BaseModel
from scripts.auth.security import validate_token
from fastapi import Depends
from fastapi import APIRouter
from typing import List
from scripts.database.helper import *


class ZNSModel(BaseModel):
    receiver_province: str
    receiver_district: str
    carrier_id: int
    message_count: int
    star: int
    feedbacks: List[str]
    note: str
    submitted_at: str
    date: str


router = APIRouter()


@router.post("", dependencies=[Depends(validate_token)])
def get_data_zns(
    receiver_province: str, receiver_district: str,
    carrier_id: int, message_count: int,
    star: int, feedbacks: List[str],
    note: str, submitted_at: str,
    date: str,
):
    zns_dict = {
        'receiver_province': receiver_province,
        'receiver_district': receiver_district,
        'carrier_id': carrier_id,
        'message_count': message_count,
        'star': star,
        'feedbacks': feedbacks,
        'note': note,
        'submitted_at': submitted_at,
        'date': date,
    }

    insert_data_to_postgres(data=[zns_dict], schema_name='db_schema', table_name='zns')

    return {
        'error': False,
        'message': "",
        'data': {
            'count': 1,
            'zns': ZNSModel(**zns_dict),
        },
    }