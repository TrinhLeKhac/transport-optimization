import sys
from pathlib import Path

ROOT_PATH = str(Path(__file__).parent.parent.parent)
sys.path.append(ROOT_PATH)

from scripts.utilities.helper import *
from sqlalchemy import create_engine
from config import settings


@exception_wrapper
def xu_ly_danh_gia_zns(run_date_str, from_api=True, n_days_back=30):
    run_date = datetime.strptime(run_date_str, '%Y-%m-%d')
    if not from_api:
        # 1. Đọc dữ liệu
        danh_gia_zns_df = pd.read_excel(ROOT_PATH + '/input/danh_gia_zns.xlsx')
        danh_gia_zns_df = danh_gia_zns_df[[
            'Tỉnh/Thành Phố Giao Hàng',
            'Quận/Huyện Giao Hàng',
            'Nhà Vận Chuyển',
            'Số Tin Gửi',
            'Số Sao',
            'Nhận Xét',
            'Đánh Giá',
            'Đánh Giá Lúc',
        ]]
        danh_gia_zns_df.columns = [
            'receiver_province', 'receiver_district', 'carrier',
            'n_messages', 'n_stars', 'comment', 'review', 'reviewed_at',
        ]
        danh_gia_zns_df['comment'] = danh_gia_zns_df['comment'].str.split(', ')
        danh_gia_zns_df['date'] = None

        danh_gia_zns_df['reviewed_at'] = pd.to_datetime(danh_gia_zns_df['reviewed_at'], errors='coerce')
        danh_gia_zns_df['date'] = pd.to_datetime(danh_gia_zns_df['date'], errors='coerce')

        # 2. Chuẩn hóa tên quận/huyện, tỉnh/thành
        danh_gia_zns_df = normalize_province_district(danh_gia_zns_df, tinh_thanh='receiver_province',
                                                      quan_huyen='receiver_district')

        # 3. Check tên nhà vận chuyển đã được chuẩn hóa chưa
        danh_gia_zns_df = danh_gia_zns_df.loc[danh_gia_zns_df['carrier'] != 'SuperShip']
        danh_gia_zns_df.loc[danh_gia_zns_df['carrier'] == 'Shopee Express', 'carrier'] = 'SPX Express'

        set_carrier = set(danh_gia_zns_df['carrier'].unique().tolist())
        set_norm_full_carrier = set(MAPPING_CARRIER_ID.keys())
        assert set_carrier - set_norm_full_carrier == set(), 'Ops, Tên nhà vận chuyển chưa được chuẩn hóa'

        # 4. Lưu thông tin
        danh_gia_zns_df.to_parquet(ROOT_PATH + '/processed_data/danh_gia_zns.parquet', index=False)

    else:
        port = settings.SQLALCHEMY_DATABASE_URI
        engine = create_engine(port)
        danh_gia_zns_df = pd.read_sql_query('select * from db_schema.zns', con=engine)
        danh_gia_zns_df['carrier'] = danh_gia_zns_df['carrier_id'].map(MAPPING_ID_CARRIER)
        danh_gia_zns_df = danh_gia_zns_df.rename(columns={
            'receiver_province': 'receiver_province_code',
            'receiver_district': 'receiver_district_code'
        })
        danh_gia_zns_df = (
            danh_gia_zns_df.merge(
                PROVINCE_MAPPING_DISTRICT_DF.rename(columns={
                    'province': 'receiver_province',
                    'district': 'receiver_district',
                    'province_code': 'receiver_province_code',
                    'district_code': 'receiver_district_code',
                }), on=['receiver_province_code', 'receiver_district_code'], how='left'
            )
        )
        danh_gia_zns_df = danh_gia_zns_df[[
            'receiver_province', 'receiver_district', 'carrier',
            'message_count', 'star', 'feedbacks', 'note', 'submitted_at', 'date'
        ]]
        danh_gia_zns_df.columns = [
            'receiver_province', 'receiver_district', 'carrier',
            'n_messages', 'n_stars', 'comment', 'review', 'reviewed_at', 'date'
        ]

        danh_gia_zns_df['reviewed_at'] = pd.to_datetime(danh_gia_zns_df['reviewed_at'], errors='coerce')
        danh_gia_zns_df['date'] = pd.to_datetime(danh_gia_zns_df['date'], errors='coerce')

        danh_gia_zns_df = danh_gia_zns_df.loc[
            danh_gia_zns_df['reviewed_at'] >=
            (run_date - timedelta(days=n_days_back))
            ]

        # 4. Lưu thông tin
        danh_gia_zns_df.to_parquet(ROOT_PATH + '/processed_data/danh_gia_zns.parquet', index=False)


def xu_ly_danh_gia_zns_1_sao(run_date_str):
    danh_gia_zns = pd.read_parquet(ROOT_PATH + "/processed_data/danh_gia_zns.parquet")
    run_date = datetime.strptime(run_date_str, '%Y-%m-%d')

    danh_gia_zns['n_days'] = (run_date - danh_gia_zns['date']).dt.days
    danh_gia_zns_1sao = danh_gia_zns.loc[danh_gia_zns['n_stars'] == 1]

    danh_gia_zns_1sao = danh_gia_zns_1sao[['receiver_province', 'receiver_district', 'carrier', 'n_days']]
    danh_gia_zns_1sao = danh_gia_zns_1sao.sort_values(['receiver_province', 'receiver_district', 'carrier', 'n_days'],
                                                      ascending=[True, True, True, True])
    danh_gia_zns_1sao = danh_gia_zns_1sao.drop_duplicates(['receiver_province', 'receiver_district', 'carrier'],
                                                          keep='first')
    danh_gia_zns_1sao = (
        PROVINCE_MAPPING_DISTRICT_CROSS_CARRIER_DF.merge(
            danh_gia_zns_1sao, on=['receiver_province', 'receiver_district', 'carrier'], how='left'
        )
    )
    danh_gia_zns_1sao['n_days'] = danh_gia_zns_1sao['n_days'].fillna(100).astype('int')

    danh_gia_zns_1sao = danh_gia_zns_1sao.merge(
        PROVINCE_MAPPING_DISTRICT_DF.rename(columns={
            'province': 'receiver_province',
            'district': 'receiver_district',
            'province_code': 'receiver_province_code',
            'district_code': 'receiver_district_code'
        }), on=['receiver_province', 'receiver_district'], how='inner')
    danh_gia_zns_1sao['carrier_id'] = danh_gia_zns_1sao['carrier'].map(MAPPING_CARRIER_ID)
    danh_gia_zns_1sao = danh_gia_zns_1sao[['carrier_id', 'receiver_province_code', 'receiver_district_code', 'n_days']]

    danh_gia_zns_1sao.to_parquet(ROOT_PATH + '/processed_data/danh_gia_zns_1_sao.parquet', index=False)
