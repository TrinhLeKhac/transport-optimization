import optparse
import sys
from pathlib import Path
from typing import Literal

import psycopg2

ROOT_PATH = str(Path(__file__).parent.parent.parent)
sys.path.append(ROOT_PATH)

from scripts.output.out_data_final import *
from scripts.database.pd_sql_schemas import *
from sqlalchemy import create_engine
from config import settings

PORT = settings.SQLALCHEMY_DATABASE_URI
ENGINE = create_engine(PORT)

# ------------------------------------ config init ------------------------------------

# (path, tbl_name, is_id_col, is_churn_size)
config_init = [
    (ROOT_PATH + '/processed_data/phan_vung_nvc.parquet', 'tbl_phan_vung_nvc', False, False),
    (ROOT_PATH + '/transform/buu_cuc.parquet', 'tbl_buu_cuc', False, False),
    (ROOT_PATH + '/output/data_order_type.parquet', 'tbl_order_type', False, True),
    (ROOT_PATH + '/output/service_fee.parquet', 'tbl_service_fee', False, False),
]

# ------------------------------------ config daily ------------------------------------

config_daily = [
    (ROOT_PATH + '/transform/chat_luong_noi_bo_njv.parquet', 'tbl_clnb_ninja_van', False, False),
    (ROOT_PATH + '/transform/ngung_giao_nhan.parquet', 'tbl_ngung_giao_nhan', False, False),
    (ROOT_PATH + '/output/data_api.parquet', 'tbl_data_api', True, False),
    (ROOT_PATH + '/output/total_optimal_score.parquet', 'tbl_optimal_score', False, False),
    # (ROOT_PATH + '/output/data_visualization.parquet', 'tbl_data_visualization', True, True),
]


def delete_partition_by_import_date(schema_name, tbl_name, date_str):
    # Create connection
    connection = psycopg2.connect(
        settings.SQLALCHEMY_DATABASE_URI
    )

    cursor = connection.cursor()

    delete_query = """
        DELETE FROM {}.{} WHERE import_date = '{}';
    """.format(
        schema_name, tbl_name, date_str
    )

    cursor.execute(delete_query)

    # Commit the transaction
    connection.commit()

    cursor.close()
    connection.close()


def ingest_tbl_to_db(
        schema_name,
        path,
        tbl_name,
        date_str,
        is_id_col=False,
        is_churn_size=False,
        mode: Literal["fail", "replace", "append"] = "append",
):
    # Replace partition if exists
    if mode == "append":
        try:
            delete_partition_by_import_date(schema_name, tbl_name, date_str)
            print(f'Delete rows from partition import_date={date_str}')
        except:
            print("Table '{}' does not exist in schema '{}'.".format(tbl_name, schema_name))

    print(f'>>> Ingest data into {tbl_name}')
    tmp_df = pd.read_parquet(path)
    if is_id_col:
        tmp_df = tmp_df.reset_index().rename(columns={"index": "id"})
    tmp_df['import_date'] = date_str

    if is_churn_size:
        tmp_df.to_sql(
            name=tbl_name,
            con=ENGINE,
            schema=schema_name,
            chunksize=10000,
            if_exists=mode,
            index=False,
            dtype=TABLE_SCHEMA[tbl_name]
        )
    else:
        tmp_df.to_sql(
            name=tbl_name,
            con=ENGINE,
            schema=schema_name,
            if_exists=mode,
            index=False,
            dtype=TABLE_SCHEMA[tbl_name]
        )

    print('-' * 100)


def ingest_data_to_db(date_str, schema_name="db_schema", init=True):

    if init:
        for path, tbl_name, is_id_col, is_churn_size in config_init:
            ingest_tbl_to_db(
                schema_name,
                path,
                tbl_name,
                date_str,
                is_id_col=is_id_col,
                is_churn_size=is_churn_size,
                mode="replace",
            )

    for path, tbl_name, is_id_col, is_churn_size in config_daily:
        if tbl_name not in ['tbl_optimal_score', 'tbl_data_visualization']:
            ingest_tbl_to_db(
                schema_name,
                path,
                tbl_name,
                date_str,
                is_id_col=is_id_col,
                is_churn_size=is_churn_size,
                mode="append",
            )
        else:
            ingest_tbl_to_db(
                schema_name,
                path,
                tbl_name,
                date_str,
                is_id_col=is_id_col,
                is_churn_size=is_churn_size,
                mode="replace",
            )


if __name__ == '__main__':
    parser = optparse.OptionParser(description="Running mode")
    parser.add_option(
        '-m', '--mode',
        action="store", dest="mode",
        help="mode string", default="init"
    )
    parser.add_option(
        '-d', '--run_date',
        action="store", dest="run_date",
        help="run_date string", default=f"{datetime.now().strftime('%Y-%m-%d')}"
    )
    options, args = parser.parse_args()
    # print(options.mode)
    # print(options.run_date)

    print(f'Ingesting data on date = {options.run_date}...')
    if options.mode == 'init':
        try:
            ingest_data_to_db(options.run_date, schema_name="db_schema", init=True)
        except Exception as e:
            error = type(e).__name__ + " – " + str(e)
            telegram_bot_send_error_message(error)
    elif options.mode == 'daily':
        try:
            ingest_data_to_db(options.run_date, schema_name="db_schema", init=False)
        except Exception as e:
            error = type(e).__name__ + " – " + str(e)
            telegram_bot_send_error_message(error)
