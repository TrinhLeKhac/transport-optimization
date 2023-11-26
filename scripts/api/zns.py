from pydantic import BaseModel
from scripts.auth.security import validate_token
from fastapi import Depends
from fastapi import APIRouter
from typing import List
from scripts.database.helper import *


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
def get_data_zns(request_data: ZNSModel):
    data = request_data.model_dump()  # invert method: ZNSModel(**data)
    insert_data_to_postgres(data=[data], schema_name="db_schema", table_name="zns")

    return {
        "error": False,
        "message": "",
        "data": {
            "count": 1,
            "zns": data,  # can show ZNSModel or dict
        },
    }
