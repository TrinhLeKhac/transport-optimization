import sys
from pathlib import Path

ROOT_PATH = str(Path(__file__).parent.parent.parent)
sys.path.append(ROOT_PATH)

from scripts.utilities.helper import *
from sqlalchemy import create_engine
from config import settings


def xu_ly_danh_gia_zns(from_api=True):
    if not from_api:
        # 1. Đọc dữ liệu
        danh_gia_zns_df = pd.read_excel(ROOT_PATH + '/input/Đánh Giá ZNS.xlsx')
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

        # 2. Chuẩn hóa tên quận/huyện, tỉnh/thành
        danh_gia_zns_df = normalize_province_district(danh_gia_zns_df, tinh_thanh='receiver_province',
                                                      quan_huyen='receiver_district')

        # 3. Check tên nhà vận chuyển đã được chuẩn hóa chưa
        danh_gia_zns_df = danh_gia_zns_df.loc[danh_gia_zns_df['carrier'] != 'SuperShip']
        danh_gia_zns_df.loc[danh_gia_zns_df['carrier'] == 'Shopee Express', 'carrier'] = 'SPX Express'

        danh_gia_zns_df['reviewed_at'] = pd.to_datetime(danh_gia_zns_df['reviewed_at'], errors='coerce')

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

        # 4. Lưu thông tin
        danh_gia_zns_df.to_parquet(ROOT_PATH + '/processed_data/danh_gia_zns_from_api.parquet', index=False)

