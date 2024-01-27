import psycopg2
from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session
from scripts.api import schemas
from scripts.api.database import *

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

    table_query = """
        WITH carrier_information AS (
            SELECT 
            tbl_ord.carrier_id, tbl_ord.route_type, 
            tbl_fee.price, 
            tbl_api.status, tbl_api.description, tbl_api.time_data,
            tbl_api.time_display, tbl_api.rate, tbl_api.score, tbl_api.star, 
            tbl_api.for_shop, tbl_api.speed_ranking, tbl_api.score_ranking, tbl_api.rate_ranking, 
            CAST (DENSE_RANK() OVER (
                ORDER BY tbl_fee.price ASC
            ) AS smallint) AS price_ranking
            FROM db_schema.tbl_order_type tbl_ord
            INNER JOIN (SELECT * FROM db_schema.tbl_data_api WHERE import_date = (SELECT MAX(import_date) FROM db_schema.tbl_data_api)) AS tbl_api
            ON tbl_ord.carrier_id = tbl_api.carrier_id --6
            AND tbl_ord.receiver_province_code = tbl_api.receiver_province_code
            AND tbl_ord.receiver_district_code = tbl_api.receiver_district_code --713
            AND tbl_ord.new_type = tbl_api.new_type --7
            INNER JOIN db_schema.tbl_service_fee tbl_fee
            ON tbl_ord.carrier_id = tbl_fee.carrier_id --6
            AND tbl_ord.new_type = tbl_fee.new_type  --7
            WHERE tbl_ord.sender_province_code = '{}' 
            AND tbl_ord.sender_district_code = '{}'
            AND tbl_ord.receiver_province_code = '{}' 
            AND tbl_ord.receiver_district_code = '{}' 
            AND tbl_fee.weight = CEIL({}/500.0)*500 
            AND tbl_fee.pickup = '{}'
        )
        select carrier_id, route_type, price, status::varchar(1) AS status, description, time_data, time_display,
        rate, score, star, for_shop, 
        CAST (DENSE_RANK() OVER (
            ORDER BY
                (1.4 * price_ranking + 1.2 * rate_ranking + score_ranking)
            ASC
        ) AS smallint) AS for_partner,
        price_ranking, speed_ranking, score_ranking
        FROM carrier_information
        ORDER BY carrier_id;
    """.format(
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
