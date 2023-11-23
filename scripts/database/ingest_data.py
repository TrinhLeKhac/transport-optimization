import sys
from pathlib import Path
ROOT_PATH = str(Path(__file__).parent.parent.parent)
sys.path.append(ROOT_PATH)

from scripts.api.out_data_final import *
from scripts.database.schemas import *
from sqlalchemy import create_engine
# from config import Config


def ingest_data_to_db():
   
    # engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
    port = 'postgresql://postgres:123456@localhost:5432/db_supership_ai'
    engine = create_engine(port)
    print('>>> Ingest data đã qua xử lý...')
    for f, schema in TABLE_SCHEMA.items():
        if f not in ['data_api', 'data_api_full', 'data_check_output']:
            tmp_df = pd.read_parquet(ROOT_PATH + '/processed_data/{}.parquet'.format(f))
            tmp_df['import_date'] = datetime.now().strftime('%F')
            tmp_df.to_sql(name=f, con=engine, schema="db_schema", if_exists="replace", index=False, dtype=schema)
    print('-' * 100)

    print('>>> Ingest output API')
    data_api_df = pd.read_parquet(ROOT_PATH + '/output/data_api.parquet')
    data_api_df = data_api_df.reset_index().rename(columns={"index": "id"})
    data_api_df['import_date'] = datetime.now().strftime('%F')
    data_api_df.to_sql(name='data_api', con=engine, schema="db_schema", if_exists="replace", index=False,
                       dtype=TABLE_SCHEMA['data_api'])
    print('-' * 100)

    print('>>> Ingest output API full')
    data_api_full_df = out_data_api(return_full_cols_df=True, show_logs=False)
    data_api_full_df = data_api_full_df.reset_index().rename(columns={"index": "id"})
    data_api_full_df['import_date'] = datetime.now().strftime('%F')
    data_api_full_df.to_sql(name='data_api_full', con=engine, schema="db_schema", if_exists="replace", index=False,
                            dtype=TABLE_SCHEMA['data_api_full'])
    print('-' * 100)

    print('>>> Ingest data check output')
    if os.path.exists(ROOT_PATH + '/output/data_check_output.parquet'):
        check_df = pd.read_parquet(ROOT_PATH + '/output/data_check_output.parquet')
    else:
        print('>>>>>> Out data check output')
        check_df = out_data_final(show_logs=False)

    print('>>> Ghi thông tin vào DB')
    check_df = check_df.reset_index().rename(columns={"index": "id"})
    check_df['import_date'] = datetime.now().strftime('%F')
    check_df.to_sql(name='data_check_output', con=engine, schema="db_schema", if_exists="replace", index=False,
                    dtype=TABLE_SCHEMA['data_check_output'])
    print('>>> Done')


if __name__ == '__main__':
    ingest_data_to_db()
