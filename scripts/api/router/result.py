import psycopg2
from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session
from scripts.api import schemas
from scripts.api.database import *
from scripts.utilities.helper import QUERY_SQL_COMMAND_API

router = APIRouter()


def execute_query(
    sender_province_code, sender_district_code,
    receiver_province_code, receiver_district_code,
    weight, pickup
):

    # Create connection
    connection = psycopg2.connect(
        settings.SQLALCHEMY_DATABASE_URI
    )

    cursor = connection.cursor()

    table_query = QUERY_SQL_COMMAND_API.format(
        sender_province_code, sender_district_code,
        receiver_province_code, receiver_district_code,
        weight, pickup
    )

    cursor.execute(table_query)
    rows = cursor.fetchall()
    print(rows)

    # Get the field names from the Pydantic model
    field_names = schemas.APIResultModel.__annotations__.keys()
    result = [schemas.APIResultModel(**dict(zip(field_names, row))) for row in rows]

    # Commit the transaction
    connection.commit()

    cursor.close()
    connection.close()

    return result


@router.post("")
def calculate(data: schemas.APIRequestModel, db: Session = Depends(get_db)):
    sender_province_code = data.sender_province
    sender_district_code = data.sender_district
    receiver_province_code = data.receiver_province
    receiver_district_code = data.receiver_district
    weight = data.weight
    pickup = data.pickup

    result = execute_query(
        sender_province_code, sender_district_code,
        receiver_province_code, receiver_district_code,
        weight, pickup
    )

    return {
        "error": False,
        "message": "",
        "data": result
    }
