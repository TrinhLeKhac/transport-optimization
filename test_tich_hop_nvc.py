from typing import Literal

import pandas as pd
import psycopg2
from sqlalchemy import create_engine
from scripts.utilities.helper import *
from scripts.utilities.config import *

import sys
ROOT_PATH = str(Path(__file__).parent.parent.parent)
sys.path.append(ROOT_PATH)

from scripts.output.out_data_final import *
from scripts.database.pd_sql_schemas import *
from sqlalchemy import create_engine
from config import settings

PORT = settings.SQLALCHEMY_DATABASE_URI
ENGINE = create_engine(PORT)

# # ------------------------------------ config init ------------------------------------
#
# # (path, tbl_name, is_id_col, is_churn_size, idx_cols)
# config_init = [
#     (ROOT_PATH + '/processed_data/phan_vung_nvc.parquet', 'tbl_phan_vung_nvc', False, False, None),  # Đẩy lên database, nhưng không có trong câu query. Dùng để tổng hợp order_type, new_type trong tbl_order_type
#     # (ROOT_PATH + '/transform/buu_cuc.parquet', 'tbl_buu_cuc', False, False, None),  # Đẩy lên database, nhưng không có trong câu query.
#     # (
#     #     ROOT_PATH + '/output/data_order_type.parquet', 'tbl_order_type', False, True,  # observe, trigger run.sh mode init khi file phan_vung_ghep_supership.xlsx thay đổi => phan_vung_nvc.parquet thay đổi => data_order_type.parquet thay đổi.
#     #     'carrier_id, sender_province_code, sender_district_code, receiver_province_code, receiver_district_code'
#     # ),
#     # (
#     #     ROOT_PATH + '/output/service_fee.parquet', 'tbl_service_fee', False, False,  # observe, trigger run.sh mode init khi file bang_cuoc_phi.xlsx thay đổi.
#     #     'carrier_id, order_type, weight, pickup'
#     # ),
# ]
#
# # ------------------------------------ config daily ------------------------------------
#
# config_daily = [
#     # (ROOT_PATH + '/transform/chat_luong_noi_bo_njv.parquet', 'tbl_clnb_ninja_van', False, False, None),  # observe, run.sh script mode daily khi file rst_cao_njv.xlsx thay đổi.
#     (
#         ROOT_PATH + '/transform/ngung_giao_nhan.parquet', 'tbl_ngung_giao_nhan', False, False,  # observe, trigger rum.sh mode daily khi file ngung_giao_nhan.xlsx thay đổi.
#         'carrier_id, sender_province_code, sender_district_code'
#     ),
#     # (
#     #     ROOT_PATH + '/transform/ngung_giao_nhan_level_3.parquet', 'tbl_ngung_giao_nhan_level_3', False, False,  # observe, trigger rum.sh mode daily khi file shopee_ngung_giao_nhan.xlsx thay đổi.
#     #     'carrier_id, receiver_province_code, receiver_district_code, receiver_commune_code'
#     # ),
#     (
#         ROOT_PATH + '/output/data_api.parquet', 'tbl_data_api', True, False,
#         'carrier_id, receiver_province_code, receiver_district_code, new_type'
#     ),
#     (ROOT_PATH + '/output/total_optimal_score.parquet', 'tbl_optimal_score', False, False, None),
# ]
#
#
# def delete_repeated_partition(schema_name, tbl_name, date_str):
#     # Create connection
#     connection = psycopg2.connect(
#         settings.SQLALCHEMY_DATABASE_URI
#     )
#
#     cursor = connection.cursor()
#
#     delete_query = """
#         DELETE FROM {}.{} WHERE import_date = '{}';
#     """.format(
#         schema_name, tbl_name, date_str
#     )
#
#     cursor.execute(delete_query)
#
#     # Commit the transaction
#     connection.commit()
#
#     cursor.close()
#     connection.close()
#
#
# def create_index_of_table(
#     schema_name,
#     tbl_name,
#     idx_cols=None
# ):
#     # Create connection
#     connection = psycopg2.connect(
#         settings.SQLALCHEMY_DATABASE_URI
#     )
#
#     cursor = connection.cursor()
#
#     create_idx_query = f"CREATE UNIQUE INDEX {tbl_name}_idx ON {schema_name}.{tbl_name}({idx_cols})"
#
#     cursor.execute(create_idx_query)
#
#     # Commit the transaction
#     connection.commit()
#
#     cursor.close()
#     connection.close()
#
#
# def ingest_tbl_to_db(
#         schema_name,
#         path,
#         tbl_name,
#         date_str,
#         is_id_col=False,
#         is_churn_size=False,
#         mode: Literal["fail", "replace", "append"] = "append",
# ):
#     # Replace repeated partition
#     if mode == "append":
#         try:
#             delete_repeated_partition(schema_name, tbl_name, date_str)
#             print(f'Delete repeated partition from import_date={date_str}')
#         except:
#             print("Table '{}' does not exist in schema '{}'.".format(tbl_name, schema_name))
#
#     print(f'>>> Ingest data into {tbl_name}')
#     tmp_df = pd.read_parquet(path)
#     print('Shape: ', len(tmp_df))
#     if is_id_col:
#         tmp_df = tmp_df.reset_index().rename(columns={"index": "id"})
#     tmp_df['import_date'] = date_str
#
#     if is_churn_size:
#         tmp_df.to_sql(
#             name=tbl_name,
#             con=ENGINE,
#             schema=schema_name,
#             chunksize=10000,
#             if_exists=mode,
#             index=False,
#             dtype=TABLE_SCHEMA[tbl_name]
#         )
#     else:
#         tmp_df.to_sql(
#             name=tbl_name,
#             con=ENGINE,
#             schema=schema_name,
#             if_exists=mode,
#             index=False,
#             dtype=TABLE_SCHEMA[tbl_name]
#         )
#
#     print('-' * 100)
#
#
# def ingest_data_to_db(date_str, schema_name="db_schema", init=True):
#     if init:
#         for path, tbl_name, is_id_col, is_churn_size, idx_cols in config_init:
#             ingest_tbl_to_db(
#                 schema_name,
#                 path,
#                 tbl_name,
#                 date_str,
#                 is_id_col=is_id_col,
#                 is_churn_size=is_churn_size,
#                 mode="replace",
#             )
#             if idx_cols is not None:
#                 create_index_of_table(schema_name, tbl_name, idx_cols)
#
#     for path, tbl_name, is_id_col, is_churn_size, idx_cols in config_daily:
#         if tbl_name not in ['tbl_optimal_score']:
#             ingest_tbl_to_db(
#                 schema_name,
#                 path,
#                 tbl_name,
#                 date_str,
#                 is_id_col=is_id_col,
#                 is_churn_size=is_churn_size,
#                 mode="replace",
#             )
#             if idx_cols is not None:
#                 create_index_of_table(schema_name, tbl_name, idx_cols)
#         else:
#             ingest_tbl_to_db(
#                 schema_name,
#                 path,
#                 tbl_name,
#                 date_str,
#                 is_id_col=is_id_col,
#                 is_churn_size=is_churn_size,
#                 mode="append",
#             )
#
#
# if __name__ == '__main__':
#     parser = optparse.OptionParser(description="Running mode")
#     parser.add_option(
#         '-m', '--mode',
#         action="store", dest="mode",
#         help="mode string", default="init"
#     )
#     parser.add_option(
#         '-d', '--run_date',
#         action="store", dest="run_date",
#         help="run_date string", default=f"{datetime.now().strftime('%Y-%m-%d')}"
#     )
#     options, args = parser.parse_args()
#     # print(options.mode)
#     # print(options.run_date)
#
#     print(f'Ingesting data on date = {options.run_date}...')
#     if options.mode == 'init':
#         ingest_data_to_db(options.run_date, schema_name="db_schema", init=True)
#
# #



# from config import settings
# from scripts.utilities.helper import *
# from scripts.utilities.config import *
# from sqlalchemy.types import SMALLINT, INTEGER, VARCHAR, ARRAY
#
#
# port = settings.SQLALCHEMY_DATABASE_URI
# engine = create_engine(port)
#
# from sqlalchemy.types import NUMERIC, SMALLINT, INTEGER, VARCHAR, Boolean, TEXT, TIMESTAMP
#
# SCHEMA_TEST = {
#     'tbl_data_test_api': {
#         'order_id': VARCHAR(length=30),
#         'carrier_actually_sent': VARCHAR(length=10),
#         'sender_province_code': VARCHAR(length=2),
#         'sender_district_code': VARCHAR(length=3),
#         'receiver_province_code': VARCHAR(length=2),
#         'receiver_district_code': VARCHAR(length=3),
#         'weight': SMALLINT,
#         'collection': INTEGER,
#         'value': INTEGER,
#         'barter': VARCHAR(length=10),
#         'pickup': VARCHAR(length=1),
#         "import_time": TIMESTAMP,
#     },
# }
#
# connection = psycopg2.connect(
#     settings.SQLALCHEMY_DATABASE_URI
# )
#
# cursor = connection.cursor()
#
# tmp_df = pd.read_parquet(ROOT_PATH + '/output/data_test_api_v2.parquet')
# tmp_df['weight'] = (np.ceil(tmp_df['weight']/500)*500).astype(int)
# tmp_df['barter'] = tmp_df['barter'].map({'0': 'Không', '1': 'Có'})
# tmp_df = tmp_df.reset_index().rename(columns={"index": "id"})
# tmp_df['import_date'] = '2024-06-18'
# print(tmp_df.head())
# print(len(tmp_df))
# tmp_df.to_sql(
#     name='tbl_data_test_api',
#     con=engine,
#     schema='db_schema',
#     if_exists='replace',
#     index=False,
#     dtype=SCHEMA_TEST['tbl_data_test_api']
# )


# # >>>> Lưu file từ database vào server cũ
# print('Saving data zns...')
# zns_chunks = pd.read_sql_query('select * from db_schema.zns', con=engine, chunksize=10000)
# danh_gia_zns = pd.concat(chunk for chunk in zns_chunks)
# danh_gia_zns.to_parquet(ROOT_PATH + '/processed_data/total_zns.parquet', index=False)
#
# print('Saving data order...')
# order_chunks = pd.read_sql_query('select * from db_schema.order', con=engine, chunksize=5000)
# order = pd.concat(chunk for chunk in order_chunks)
# order.to_parquet(ROOT_PATH + '/processed_data/total_order.parquet', index=False)


# >>>> Copy về local
# scp -r root@103.20.102.189:/root/superai/processed_data/total_zns.parquet ./processed_data
# scp -r root@103.20.102.189:/root/superai/processed_data/total_order.parquet ./processed_data


# >>>> Chuyển file từ local qua server mới
# scp -r ./processed_data/total_zns.parquet root@103.20.102.152:/root/superai/processed_data
# scp -r ./processed_data/total_order.parquet root@103.20.102.152:/root/superai/processed_data


# >>>> Đẩy file từ server mới lên database
# SCHEMA = {
#     'zns': {
#         'id': INTEGER,
#         'receiver_province': VARCHAR(length=2),
#         'receiver_district': VARCHAR(length=3),
#         'carrier_id': SMALLINT,
#         'message_count': INTEGER,
#         'star': INTEGER,
#         'feedbacks': ARRAY(VARCHAR(256)),
#         'note': VARCHAR(length=256),
#         'submitted_at': VARCHAR(length=20),
#         'date': VARCHAR(length=10),
#     },
#     'order': {
#         'id': INTEGER,
#         'order_code': VARCHAR(length=30),
#         'created_at': VARCHAR(length=20),
#         'weight': INTEGER,
#         'sent_at': VARCHAR(length=20),
#         'order_status': VARCHAR(length=256),
#         'carrier_id': SMALLINT,
#         'carrier_status': VARCHAR(length=256),
#         'sender_province': VARCHAR(length=2),
#         'sender_district': VARCHAR(length=3),
#         'receiver_province': VARCHAR(length=2),
#         'receiver_district': VARCHAR(length=3),
#         "delivery_count": INTEGER,
#         'pickup': VARCHAR(length=1),
#         'barter': VARCHAR(length=1),
#         'carrier_delivered_at': VARCHAR(length=20),
#         'picked_at': VARCHAR(length=20),
#         'last_delivering_at': VARCHAR(length=20),
#         'carrier_updated_at': VARCHAR(length=20),
#         "date": VARCHAR(length=10),
#     },
# }
#
# # zns lấy toàn bộ data
# total_zns = pd.read_parquet(ROOT_PATH + '/processed_data/total_zns.parquet').drop('id', axis=1)
# print('Shape before: ', len(total_zns))
#
# # data có duplicates sẽ không ínsert được
# total_zns = total_zns.drop_duplicates(subset=[c for c in total_zns.columns if 'feedbacks' not in c]).reset_index(drop=True)
# print('Shape: ', len(total_zns))
# total_zns = total_zns.loc[total_zns['date'] >= '2024-04-01']
# print('Shape after: ', len(total_zns))
#
# # vì lúc test API đã sinh ra 1 dòng có id = 1, nên id chỗ này start từ giá trị 2
# # filter lấy từ đầu tháng 4/2024 => id=1 không bị trùng
# total_zns = total_zns.reset_index().rename(columns={"index": "id"})
# print(total_zns['id'].min())
# print(total_zns['id'].max())
# print(total_zns['id'].nunique())
# print(total_zns['date'].min())
# print(total_zns['date'].max())
#
# # total_zns.to_sql(
# #     name='zns',
# #     con=engine,
# #     schema='db_schema',
# #     if_exists='append',
# #     index=False,
# #     dtype=SCHEMA['zns']
# # )
#
# total_order = pd.read_parquet(ROOT_PATH + '/processed_data/total_order.parquet').drop('id', axis=1)
# print('Shape before: ', len(total_order))
#
# # data có duplicates sẽ không insert được
# total_order = total_order.drop_duplicates(subset=total_order.columns).reset_index(drop=True)
# total_order = total_order.reset_index().rename(columns={"index": "id"})
#
# # vì lúc test API đã sinh ra 1 dòng có id = 1, nên id chỗ này start từ giá trị 2
# total_order['id'] = total_order['id'] + 2
# print('Shape after: ', len(total_order))
# #
# # total_order.to_sql(
# #     name='order',
# #     con=engine,
# #     schema='db_schema',
# #     if_exists='append',
# #     index=False,
# #     dtype=SCHEMA['order']
# # )


# print(os.path.abspath('./watchdog/source1.txt'))
