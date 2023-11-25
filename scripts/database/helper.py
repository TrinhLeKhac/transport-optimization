import psycopg2
from psycopg2 import sql
from config import settings


def check_tbl_exists_in_postgres(schema_name, table_name):

    # Create connection
    connection = psycopg2.connect(
        settings.SQLALCHEMY_DATABASE_URI
    )

    cursor = connection.cursor()

    # Check if the table exists
    check_table_query = sql.SQL("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables
            WHERE table_schema = {} AND table_name = {}
        )
    """).format(sql.Literal(schema_name), sql.Literal(table_name))

    cursor.execute(check_table_query)
    table_exists = cursor.fetchone()[0]

    print(table_exists)

    # Table doesn't exist, create it
    if not table_exists:
        if table_name == 'zns':
            create_table_query = sql.SQL("""
                CREATE TABLE {}.{} (
                    receiver_province VARCHAR(30),
                    receiver_district VARCHAR(30),
                    carrier_id SMALLINT,
                    message_count INTEGER,
                    star INTEGER,
                    feedbacks TEXT [],
                    note VARCHAR(100),
                    submitted_at VARCHAR(20),
                    date VARCHAR(10)
                )
            """).format(sql.Identifier(schema_name), sql.Identifier(table_name))
            cursor.execute(create_table_query)

        elif table_name == 'order':
            create_table_query = sql.SQL("""
                CREATE TABLE {}.{} (
                    order_code VARCHAR(30),
                    created_at VARCHAR(20),
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
                )
            """).format(sql.Identifier(schema_name), sql.Identifier(table_name))
            cursor.execute(create_table_query)

        # Commit the transaction
        connection.commit()

        cursor.close()
        connection.close()


def insert_data_into_postgres(data, schema_name, table_name):

    # Create connection
    connection = psycopg2.connect(
        settings.SQLALCHEMY_DATABASE_URI
    )

    cursor = connection.cursor()
    # Assuming data is a list of dictionaries where each dictionary represents a row
    for row in data:
        columns = row.keys()
        values = [row[column] for column in columns]
        print(columns)
        print(values)
        insert_query = sql.SQL("INSERT INTO {}.{} ({}) VALUES ({})").format(
            sql.Identifier(schema_name),
            sql.Identifier(table_name),
            sql.SQL(", ").join(map(sql.Identifier, columns)),
            sql.SQL(", ").join(sql.Placeholder() for _ in values)
        )
        print(insert_query)
        cursor.execute(insert_query, values)

    connection.commit()

    cursor.close()
    connection.close()
