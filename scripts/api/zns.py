from fastapi import Depends
from fastapi import APIRouter
from scripts.auth.security import validate_token
from scripts.database.helper import *
from scripts.api import schemas


router = APIRouter()


@router.post("", dependencies=[Depends(validate_token)])
def get_data_zns(request_data: schemas.MessageZNSModel):
    data = request_data.model_dump()
    insert_data_to_postgres(data=[data], schema_name="db_schema", table_name="zns")

    return {
        "error": False,
        "message": "",
        "data": {
            "count": 1,
            "zns": data,
        },
    }
