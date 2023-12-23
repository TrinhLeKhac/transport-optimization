import optparse
import sys
from pathlib import Path

ROOT_PATH = str(Path(__file__).parent.parent.parent)
sys.path.append(ROOT_PATH)

from scripts.output.out_data_final import *
from scripts.database.pd_sql_schemas import *
from sqlalchemy import create_engine
from config import settings


def ingest_data_to_db(init=True):
    port = settings.SQLALCHEMY_DATABASE_URI
    engine = create_engine(port)
    if init:
        print('>>> Ingest data đã qua xử lý...')
        for f, schema in TABLE_SCHEMA.items():
            if f in [
                'buu_cuc_best', 'buu_cuc_ghn', 'buu_cuc_ghtk', 'buu_cuc_ninja_van',
                'chat_luong_noi_bo_njv', 'ngung_giao_nhan', 'phan_vung_nvc',
            ]:
                tmp_df = pd.read_parquet(ROOT_PATH + '/processed_data/{}.parquet'.format(f))
                tmp_df['import_date'] = datetime.now().strftime('%F')
                tmp_df.to_sql(name=f, con=engine, schema="db_schema", if_exists="replace", index=False, dtype=schema)
        print('-' * 100)

    print('>>> Ingest output API')
    data_api_df = pd.read_parquet(ROOT_PATH + '/output/data_api.parquet')
    data_api_df = data_api_df.reset_index().rename(columns={"index": "id"})
    data_api_df['import_date'] = datetime.now().strftime('%F')
    data_api_df.to_sql(name='tbl_data_api', con=engine, schema="db_schema", if_exists="replace", index=False,
                       dtype=TABLE_SCHEMA['data_api'])
    print('-' * 100)

    if init:
        print('>>> Ingest data order_type')
        data_order_type_df = pd.read_parquet(ROOT_PATH + '/output/data_order_type.parquet')
        data_order_type_df.to_sql(name='tbl_order_type', con=engine, schema="db_schema", if_exists="replace", index=False,
                                  dtype=TABLE_SCHEMA['order_type'], chunksize=10000)
        print('-' * 100)

    if init:
        print('>>> Ingest data service_fee')
        service_fee_df = pd.read_parquet(ROOT_PATH + '/output/service_fee.parquet')
        service_fee_df.to_sql(name='tbl_service_fee', con=engine, schema="db_schema", if_exists="replace", index=False,
                                  dtype=TABLE_SCHEMA['service_fee'])
        print('-' * 100)

    print('>>> Ingest data visualization')
    if os.path.exists(ROOT_PATH + '/output/data_visualization.parquet'):
        check_df = pd.read_parquet(ROOT_PATH + '/output/data_visualization.parquet')
    else:
        print('>>>>>> Out data visualization')
        check_df = out_data_final(show_logs=False)

    print('>>> Ghi thông tin vào DB')
    check_df = check_df.reset_index().rename(columns={"index": "id"})
    check_df['import_date'] = datetime.now().strftime('%F')
    check_df.to_sql(name='tbl_data_visualization', con=engine, schema="db_schema", if_exists="replace", index=False,
                    dtype=TABLE_SCHEMA['data_visualization'])
    print('>>> Done')


if __name__ == '__main__':
    parser = optparse.OptionParser(description="Running mode")
    parser.add_option(
        '-m', '--mode',
        action="store", dest="mode",
        help="mode string", default=True
    )
    options, args = parser.parse_args()
    # print(options.mode)

    if options.mode == 'init':
        ingest_data_to_db(init=True)
    elif options.mode == 'daily':
        ingest_data_to_db(init=False)
