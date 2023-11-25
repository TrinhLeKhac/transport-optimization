from pydantic import BaseModel
from scripts.auth.security import validate_token
from fastapi import Depends
from fastapi import APIRouter
from typing import List


class ZNSModel(BaseModel):
    date: str
    receiver_province: str
    receiver_district: str
    carrier_id: int
    message_count: int
    star: int
    feedbacks: List[str]
    note: str
    submitted_at: str


router = APIRouter()


@router.post("", dependencies=[Depends(validate_token)])
def get_data_zns(
    date: str,
    receiver_province: str, receiver_district: str,
    carrier_id: int, message_count: int,
    star: int, feedbacks: List[str],
    note: str, submitted_at: str
):
    zns_dict = {
        'date': date,
        'receiver_province': receiver_province,
        'receiver_district': receiver_district,
        'carrier_id': carrier_id,
        'message_count': message_count,
        'star': star,
        'feedbacks': feedbacks,
        'note': note,
        'submitted_at': submitted_at
    }

    return {
        'error': False,
        'message': "",
        'data': {
            'count': 1,
            'zns': ZNSModel(**zns_dict),
        },
    }