import psycopg2
from fastapi import APIRouter
from scripts.api import schemas
from scripts.api.database import *

router = APIRouter()


@router.post("")
def calculate(carrier_id):

    # Create connection
    connection = psycopg2.connect(
        settings.SQLALCHEMY_DATABASE_URI
    )
    cursor = connection.cursor()

    if carrier_id is None:
        table_query = """
            select carrier_id, 
            receiver_province_code as province, 
            receiver_district_code as district, 
            CASE 
                WHEN status = 'Bình thường' THEN '0'
                WHEN status = 'Quá tải' THEN '1' 
            END AS status
            FROM db_schema.tbl_ngung_giao_nhan;
        """
    else:
        table_query = f"""
            select carrier_id, 
            receiver_province_code as province, 
            receiver_district_code as district, 
            CASE 
                WHEN status = 'Bình thường' THEN '0'
                WHEN status = 'Quá tải' THEN '1' 
            END AS status
            FROM db_schema.tbl_ngung_giao_nhan
            WHERE tbl_ngung_giao_nhan.carrier_id = '{carrier_id}';
        """
    cursor.execute(table_query)
    rows = cursor.fetchall()

    # Get the field names from the Pydantic model
    field_names = schemas.NGNModel.__annotations__.keys()
    result = [schemas.NGNModel(**dict(zip(field_names, row))) for row in rows]

    # Commit the transaction
    connection.commit()

    cursor.close()
    connection.close()

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
