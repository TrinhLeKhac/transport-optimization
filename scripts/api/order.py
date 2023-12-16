from fastapi import Depends
from fastapi import APIRouter
from scripts.database.helper import *
from scripts.auth.security import validate_token
from scripts.api import schemas

router = APIRouter()


@router.post("", dependencies=[Depends(validate_token)])
def get_data_order(request_data: schemas.OrderModel):
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
