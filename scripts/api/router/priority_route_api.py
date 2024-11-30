import psycopg2
from fastapi import APIRouter
from scripts.api import schemas
from scripts.api.database import *
from scripts.utilities.helper import QUERY_SQL_API_BY_DISTRICT

router = APIRouter()


def execute_query(
        receiver_district_code,
):
    # Create connection
    connection = psycopg2.connect(
        settings.SQLALCHEMY_DATABASE_URI
    )

    cursor = connection.cursor()

    table_query = QUERY_SQL_API_BY_DISTRICT.format(receiver_district_code)

    cursor.execute(table_query)
    rows = cursor.fetchall()
    print(rows)

    # Get the field names from the Pydantic model
    field_names = schemas.APIModel.__annotations__.keys()
    result = [schemas.APIModel(**dict(zip(field_names, row))) for row in rows]

    # Commit the transaction
    connection.commit()

    cursor.close()
    connection.close()

    return result


@router.post("")
def calculate(code):
    result = execute_query(
        receiver_district_code=code,
    )

    if result is None:
        return {
            "error": True,
            "message": "Resources not found",
            "data": [],
        }
    else:
        return {
            "error": False,
            "message": "",
            "data": result,
        }
