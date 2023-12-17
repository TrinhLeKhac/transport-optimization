import psycopg2
from psycopg2 import sql
from config import settings


def create_tbl_if_not_exists(schema_name, table_name):
    # Create connection
    connection = psycopg2.connect(
        settings.SQLALCHEMY_DATABASE_URI
    )

    # Create cursor
    cursor = connection.cursor()

    # Create query
    table_query = ""
    if table_name == 'zns':
        table_query = f"""
            CREATE TABLE {schema_name}.{table_name} (
                id SERIAL PRIMARY KEY,
                receiver_province VARCHAR(30),
                receiver_district VARCHAR(30),
                carrier_id SMALLINT,
                message_count INTEGER,
                star INTEGER,
                feedbacks TEXT [],
                note VARCHAR(100),
                submitted_at VARCHAR(20),
                date VARCHAR(10)
            );
            ALTER TABLE {schema_name}.{table_name} ADD CONSTRAINT constraint_dup_{table_name} UNIQUE (
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

    elif table_name == 'order':
        table_query = f"""
            CREATE TABLE {schema_name}.{table_name} (
                id SERIAL PRIMARY KEY,
                order_code VARCHAR(30),
                created_at VARCHAR(20),
                weight INTEGER,
                sent_at VARCHAR(20),
                order_status VARCHAR(30),
                carrier_id SMALLINT,
                carrier_status VARCHAR(30),
                sender_province VARCHAR(30),
                sender_district VARCHAR(30),
                receiver_province VARCHAR(30),
                receiver_district VARCHAR(30),
                delivery_count INTEGER,
                pickup VARCHAR(1),
                barter VARCHAR(1),
                carrier_delivered_at VARCHAR(20),
                picked_at VARCHAR(20),
                last_delivering_at VARCHAR(20),
                carrier_updated_at VARCHAR(20),
                date VARCHAR(10)
            );
            ALTER TABLE {schema_name}.{table_name} ADD CONSTRAINT constraint_dup_{table_name} UNIQUE (
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

    create_table_query = sql.SQL(table_query)
    cursor.execute(create_table_query)

    # Commit the transaction
    connection.commit()

    cursor.close()
    connection.close()
