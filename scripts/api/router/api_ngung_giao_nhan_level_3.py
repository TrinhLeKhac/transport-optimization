from typing import Optional

import psycopg2
from fastapi import APIRouter

from scripts.api import schemas
from scripts.api.database import *

router = APIRouter()


@router.post("")
def calculate(
    carrier_id: Optional[int] = None,
    district: Optional[str] = None,
    commune: Optional[str] = None,
):

    # Create connection
    connection = psycopg2.connect(settings.SQLALCHEMY_DATABASE_URI)
    cursor = connection.cursor()

    table_query = ""

    if district is None and commune is None:
        return {
            "error": True,
            "message": "Please choose district or commune to reduce workload of API",
            "data": [],
        }

    if district:
        if carrier_id is None and commune is None:
            table_query = f"""
                select carrier_id, 
                receiver_province_code as province, 
                receiver_district_code as district, 
                receiver_commune_code as commune,
                CASE 
                    WHEN status = 'Bình thường' THEN '0'
                    WHEN status = 'Quá tải' THEN '1' 
                END AS status
                FROM db_schema.tbl_ngung_giao_nhan_level_3
                WHERE tbl_ngung_giao_nhan_level_3.receiver_district_code = '{district}';
            """
        if carrier_id is not None and commune is None:
            table_query = f"""
                select carrier_id, 
                receiver_province_code as province, 
                receiver_district_code as district, 
                receiver_commune_code as commune,
                CASE 
                    WHEN status = 'Bình thường' THEN '0'
                    WHEN status = 'Quá tải' THEN '1' 
                END AS status
                FROM db_schema.tbl_ngung_giao_nhan_level_3
                WHERE tbl_ngung_giao_nhan_level_3.carrier_id = '{carrier_id}'
                AND tbl_ngung_giao_nhan_level_3.receiver_district_code = '{district}';
            """
        if carrier_id is None and commune is not None:
            table_query = f"""
                select carrier_id, 
                receiver_province_code as province, 
                receiver_district_code as district, 
                receiver_commune_code as commune,
                CASE 
                    WHEN status = 'Bình thường' THEN '0'
                    WHEN status = 'Quá tải' THEN '1' 
                END AS status
                FROM db_schema.tbl_ngung_giao_nhan_level_3
                WHERE tbl_ngung_giao_nhan_level_3.receiver_district_code = '{district}'
                AND tbl_ngung_giao_nhan_level_3.receiver_commune_code = '{commune}';
            """
        if carrier_id is not None and commune is not None:
            table_query = f"""
                select carrier_id, 
                receiver_province_code as province, 
                receiver_district_code as district, 
                receiver_commune_code as commune,
                CASE 
                    WHEN status = 'Bình thường' THEN '0'
                    WHEN status = 'Quá tải' THEN '1' 
                END AS status
                FROM db_schema.tbl_ngung_giao_nhan_level_3
                WHERE tbl_ngung_giao_nhan_level_3.carrier_id = '{carrier_id}'
                AND tbl_ngung_giao_nhan_level_3.receiver_district_code = '{district}'
                AND tbl_ngung_giao_nhan_level_3.receiver_commune_code = '{commune}';
            """
    if commune:
        if carrier_id is None and district is None:
            table_query = f"""
                select carrier_id, 
                receiver_province_code as province, 
                receiver_district_code as district, 
                receiver_commune_code as commune,
                CASE 
                    WHEN status = 'Bình thường' THEN '0'
                    WHEN status = 'Quá tải' THEN '1' 
                END AS status
                FROM db_schema.tbl_ngung_giao_nhan_level_3
                WHERE tbl_ngung_giao_nhan_level_3.receiver_commune_code = '{commune}';
            """
        if carrier_id is not None and district is None:
            table_query = f"""
                select carrier_id, 
                receiver_province_code as province, 
                receiver_district_code as district, 
                receiver_commune_code as commune,
                CASE 
                    WHEN status = 'Bình thường' THEN '0'
                    WHEN status = 'Quá tải' THEN '1' 
                END AS status
                FROM db_schema.tbl_ngung_giao_nhan_level_3
                WHERE tbl_ngung_giao_nhan_level_3.carrier_id = '{carrier_id}'
                AND tbl_ngung_giao_nhan_level_3.receiver_commune_code = '{commune}';
            """
        if carrier_id is None and district is not None:
            table_query = f"""
                select carrier_id, 
                receiver_province_code as province, 
                receiver_district_code as district, 
                receiver_commune_code as commune,
                CASE 
                    WHEN status = 'Bình thường' THEN '0'
                    WHEN status = 'Quá tải' THEN '1' 
                END AS status
                FROM db_schema.tbl_ngung_giao_nhan_level_3
                WHERE tbl_ngung_giao_nhan_level_3.receiver_district_code = '{district}'
                AND tbl_ngung_giao_nhan_level_3.receiver_commune_code = '{commune}';
            """
        if carrier_id is not None and district is not None:
            table_query = f"""
                select carrier_id, 
                receiver_province_code as province, 
                receiver_district_code as district, 
                receiver_commune_code as commune,
                CASE 
                    WHEN status = 'Bình thường' THEN '0'
                    WHEN status = 'Quá tải' THEN '1' 
                END AS status
                FROM db_schema.tbl_ngung_giao_nhan_level_3
                WHERE tbl_ngung_giao_nhan_level_3.carrier_id = '{carrier_id}'
                AND tbl_ngung_giao_nhan_level_3.receiver_district_code = '{district}'
                AND tbl_ngung_giao_nhan_level_3.receiver_commune_code = '{commune}';
            """

    cursor.execute(table_query)
    rows = cursor.fetchall()

    # Get the field names from the Pydantic model
    field_names = schemas.NGNLV3Model.__annotations__.keys()
    result = [schemas.NGNLV3Model(**dict(zip(field_names, row))) for row in rows]

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
