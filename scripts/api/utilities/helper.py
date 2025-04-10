import psycopg2
from psycopg2 import sql

from config import settings


def create_tbl_if_not_exists(schema_name, table_name):
    # Create connection
    connection = psycopg2.connect(settings.SQLALCHEMY_DATABASE_URI)

    # Create cursor
    cursor = connection.cursor()

    # Create query
    table_query = ""
    if table_name == "zns":
        table_query = f"""
            CREATE TABLE {schema_name}.{table_name} (
                id SERIAL PRIMARY KEY,
                receiver_province VARCHAR(2),
                receiver_district VARCHAR(3),
                carrier_id SMALLINT,
                message_count INTEGER,
                star INTEGER,
                feedbacks TEXT [],
                note VARCHAR(256),
                submitted_at VARCHAR(20),
                date VARCHAR(10)
            );
            ALTER TABLE {schema_name}.{table_name} ADD CONSTRAINT constraint_dup_{table_name} UNIQUE NULLS NOT DISTINCT (
                receiver_province, 
                receiver_district, 
                carrier_id, 
                message_count, 
                star, 
                feedbacks, 
                note, 
                submitted_at, 
                date
            );
        """

    elif table_name == "order":
        table_query = f"""
            CREATE TABLE {schema_name}.{table_name} (
                id SERIAL PRIMARY KEY,
                order_code VARCHAR(30),
                created_at VARCHAR(20),
                weight INTEGER,
                sent_at VARCHAR(20),
                order_status VARCHAR(256),
                carrier_id SMALLINT,
                carrier_status VARCHAR(256),
                sender_province VARCHAR(2),
                sender_district VARCHAR(3),
                receiver_province VARCHAR(2),
                receiver_district VARCHAR(3),
                delivery_count INTEGER,
                pickup VARCHAR(1),
                barter VARCHAR(1),
                carrier_delivered_at VARCHAR(20),
                picked_at VARCHAR(20),
                last_delivering_at VARCHAR(20),
                carrier_updated_at VARCHAR(20),
                date VARCHAR(10)
            );
            ALTER TABLE {schema_name}.{table_name} ADD CONSTRAINT constraint_dup_{table_name} UNIQUE NULLS NOT DISTINCT (
                order_code, 
                created_at, 
                weight, 
                sent_at, 
                order_status, 
                carrier_id, 
                carrier_status, 
                sender_province,
                sender_district,
                receiver_province,
                receiver_district,
                delivery_count,
                pickup,
                barter,
                carrier_delivered_at,
                picked_at,
                last_delivering_at,
                carrier_updated_at,
                date
            );
        """
    elif table_name == "tbl_ngung_giao_nhan_rev":
        table_query = f"""
            CREATE TABLE {schema_name}.{table_name} (
                id SERIAL PRIMARY KEY,
                province VARCHAR(2),
                district VARCHAR(3),
                carrier_id SMALLINT,
                status VARCHAR(30)
            );
        """
    elif table_name == "tbl_ngung_giao_nhan_level_3_rev":
        table_query = f"""
            CREATE TABLE {schema_name}.{table_name} (
                id SERIAL PRIMARY KEY,
                province VARCHAR(2),
                district VARCHAR(3),
                commune VARCHAR(5),
                carrier_id SMALLINT,
                status VARCHAR(30)
            );
        """

    create_table_query = sql.SQL(table_query)
    cursor.execute(create_table_query)

    # Commit the transaction
    connection.commit()

    cursor.close()
    connection.close()
