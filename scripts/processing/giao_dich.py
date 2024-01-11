import sys
from pathlib import Path

ROOT_PATH = str(Path(__file__).parent.parent.parent)
sys.path.append(ROOT_PATH)

from scripts.utilities.helper import *
from sqlalchemy import create_engine
from config import settings

OLD_DATA_COLS = [
    'Tạo Lúc', 'Mã Đơn Hàng', 'Nhà Vận Chuyển', 'Trạng Thái Vận Đơn',
    'Tỉnh/Thành Phố Giao', 'Quận/Huyện Giao', 'Số Lần Giao',
    'Hình Thức Gửi Hàng', 'Có Hàng Đổi Trả', 'Giao lúc',
]

NEW_DATA_COLS = [
    'created_at', 'order_code', 'carrier', 'carrier_status',
    'receiver_province', 'receiver_district', 'delivery_count',
    'delivery_type', 'is_returned', 'carrier_delivered_at',
]


def convert_datetime_type1(s):
    try:
        result = datetime.strptime(s, "%Y-%d-%m %H:%M:%S")
    except ValueError:
        result = None
    return result


def convert_datetime_type2(s):
    try:
        result = datetime.strptime(s, "%Y-%d-%m %H:%M:%S")
    except ValueError:
        try:
            result = datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            result = None
    return result


def xu_ly_giao_dich():
    print('Xử lý giao dịch BEST Express...')
    best_df = pd.read_excel(ROOT_PATH + '/input/Giao Dịch Nhà Vận Chuyển.xlsx', sheet_name='BEST')
    best_df = best_df[OLD_DATA_COLS]
    best_df.columns = NEW_DATA_COLS
    best_df['carrier'] = 'BEST Express'

    best_df.loc[best_df['is_returned'] == '✅', 'is_returned'] = True
    best_df['is_returned'] = best_df['is_returned'].fillna(False)
    best_df['created_at'] = pd.to_datetime(best_df['created_at'], errors='coerce')
    best_df['carrier_delivered_at'] = pd.to_datetime(best_df['carrier_delivered_at'], errors='coerce')

    best_df['carrier_delivered_at'] = best_df['carrier_delivered_at'].apply(lambda x: str(x)).apply(convert_datetime_type1)
    best_df['created_at'] = best_df['created_at'].apply(lambda x: str(x)).apply(convert_datetime_type2)

    print('Xử lý giao dịch Ninja Van...')
    njv_df = pd.read_excel(ROOT_PATH + '/input/Giao Dịch Nhà Vận Chuyển.xlsx', sheet_name='NJV')
    njv_df = njv_df[OLD_DATA_COLS]
    njv_df.columns = NEW_DATA_COLS
    njv_df['carrier'] = 'Ninja Van'

    njv_df.loc[njv_df['is_returned'] == '✅', 'is_returned'] = True
    njv_df['is_returned'] = njv_df['is_returned'].fillna(False)

    njv_df['created_at'] = pd.to_datetime(njv_df['created_at'], errors='coerce')
    njv_df['carrier_delivered_at'] = pd.to_datetime(njv_df['carrier_delivered_at'], errors='coerce')

    njv_df['carrier_delivered_at'] = njv_df['carrier_delivered_at'].apply(lambda x: str(x)).apply(convert_datetime_type1)

    print('Xử lý giao dịch GHN...')
    ghn_df = pd.read_excel(ROOT_PATH + '/input/Giao Dịch Nhà Vận Chuyển.xlsx', sheet_name='GHN')
    ghn_df = ghn_df[OLD_DATA_COLS]
    ghn_df.columns = NEW_DATA_COLS
    ghn_df['carrier'] = 'GHN'

    ghn_df.loc[ghn_df['is_returned'] == '✅', 'is_returned'] = True
    ghn_df['is_returned'] = ghn_df['is_returned'].fillna(False)

    ghn_df['created_at'] = pd.to_datetime(ghn_df['created_at'], errors='coerce')
    ghn_df['carrier_delivered_at'] = pd.to_datetime(ghn_df['carrier_delivered_at'], errors='coerce')

    ghn_df['carrier_delivered_at'] = ghn_df['carrier_delivered_at'].apply(lambda x: str(x)).apply(convert_datetime_type1)

    print('Xử lý giao dịch Viettel Post...')
    vtp_df = pd.read_excel(ROOT_PATH + '/input/Giao Dịch Nhà Vận Chuyển.xlsx', sheet_name='VTP')
    vtp_df = vtp_df[OLD_DATA_COLS]
    vtp_df.columns = NEW_DATA_COLS
    vtp_df['carrier'] = 'Viettel Post'

    vtp_df.loc[vtp_df['is_returned'] == '✅', 'is_returned'] = True
    vtp_df['is_returned'] = vtp_df['is_returned'].fillna(False)

    vtp_df['created_at'] = pd.to_datetime(vtp_df['created_at'], errors='coerce')
    vtp_df['carrier_delivered_at'] = pd.to_datetime(vtp_df['carrier_delivered_at'], errors='coerce')

    vtp_df['carrier_delivered_at'] = vtp_df['carrier_delivered_at'].apply(lambda x: str(x)).apply(convert_datetime_type1)

    print('Xử lý giao dịch SPX Express...')
    spx_df = pd.read_excel(ROOT_PATH + '/input/Giao Dịch Nhà Vận Chuyển.xlsx', sheet_name='SPX')
    spx_df = spx_df[OLD_DATA_COLS]
    spx_df.columns = NEW_DATA_COLS
    spx_df['carrier'] = 'SPX Express'

    spx_df.loc[spx_df['is_returned'] == '✅', 'is_returned'] = True
    spx_df['is_returned'] = spx_df['is_returned'].fillna(False)

    spx_df['created_at'] = pd.to_datetime(spx_df['created_at'], errors='coerce')
    spx_df['carrier_delivered_at'] = pd.to_datetime(spx_df['carrier_delivered_at'], errors='coerce')

    spx_df['carrier_delivered_at'] = spx_df['carrier_delivered_at'].apply(lambda x: str(x)).apply(convert_datetime_type1)

    print('Xử lý giao dịch GHTK...')
    ghtk_df = pd.read_excel(ROOT_PATH + '/input/Giao Dịch Nhà Vận Chuyển.xlsx', sheet_name='GHTK')
    ghtk_df = ghtk_df[OLD_DATA_COLS]
    ghtk_df.columns = NEW_DATA_COLS
    ghtk_df['carrier'] = 'GHTK'

    ghtk_df.loc[ghtk_df['is_returned'] == '✅', 'is_returned'] = True
    ghtk_df['is_returned'] = ghtk_df['is_returned'].fillna(False)

    ghtk_df['created_at'] = pd.to_datetime(ghtk_df['created_at'], errors='coerce')
    ghtk_df['carrier_delivered_at'] = pd.to_datetime(ghtk_df['carrier_delivered_at'], errors='coerce')

    ghtk_df['carrier_delivered_at'] = ghtk_df['carrier_delivered_at'].apply(lambda x: str(x)).apply(convert_datetime_type1)

    print('Tổng hợp giao dịch...')
    raw_order_df = pd.concat([best_df, njv_df, ghn_df, vtp_df, spx_df, ghtk_df], ignore_index=True)

    print('Lưu thông tin...')
    raw_order_df.to_parquet(ROOT_PATH + '/processed_data/raw_order.parquet', index=False)


def xu_ly_giao_dich_co_khoi_luong():
    order_with_weight_df = pd.read_excel(ROOT_PATH + '/input/Đơn Có Khối Lượng.xlsx', sheet_name='Combined')

    order_with_weight_df = order_with_weight_df[['Mã Đơn SuperShip', 'Khối Lượng', 'Kho Hàng']]
    order_with_weight_df.columns = ['order_code', 'weight', 'storage_address']

    print('Lưu thông tin...')
    order_with_weight_df.to_parquet(ROOT_PATH + '/processed_data/order_with_weight.parquet', index=False)


def tong_hop_thong_tin_giao_dich(run_date_str, from_api=True, n_days_back=30):
    run_date = datetime.strptime(run_date_str, '%Y-%m-%d')
    if not from_api:
        print('Đọc thông tin giao dịch và giao dịch có khối lượng...')
        raw_order_df = pd.read_parquet(ROOT_PATH + '/processed_data/raw_order.parquet')
        order_with_weight_df = pd.read_parquet(ROOT_PATH + '/processed_data/order_with_weight.parquet')

        print('Combine thông tin giao dịch')
        order_df = raw_order_df.merge(order_with_weight_df, on='order_code', how='inner')
        print('Số giao dịch hợp lệ: ', len(order_df))

        print('Tách địa chỉ tỉnh/thành, quận/huyện lấy hàng từ kho nhận')
        order_df['sender_province'] = order_df['storage_address'].str.split(', ').str[-1]
        order_df['sender_district'] = order_df['storage_address'].str.split(', ').str[-2]

        print('Chuẩn hóa thông tin tỉnh/thành, quận/huyện lấy hàng...')
        order_df = normalize_province_district(order_df, tinh_thanh='sender_province',
                                                      quan_huyen='sender_district')

        print('Chuẩn hóa thông tin tỉnh/thành, quận/huyện giao hàng...')
        order_df = normalize_province_district(order_df, tinh_thanh='receiver_province',
                                                      quan_huyen='receiver_district')

        valid_order_df = order_df[
            order_df['sender_province'].notna()
            & order_df['sender_district'].notna()
            & order_df['receiver_province'].notna()
            & order_df['receiver_district'].notna()
            ]
        print('Số giao dịch sau khi chuẩn hóa tỉnh/thành, quận/huyện: ', len(valid_order_df))

        print('Tính toán loại vận chuyển từ địa chỉ giao và nhận...')
        phan_vung_nvc = pd.read_parquet(ROOT_PATH + '/processed_data/phan_vung_nvc.parquet')
        phan_vung_nvc = phan_vung_nvc[['carrier', 'receiver_province', 'receiver_district', 'outer_region', 'inner_region']]
        valid_order_df = (
            valid_order_df.merge(
                phan_vung_nvc.rename(columns={
                    'receiver_province': 'sender_province',
                    'receiver_district': 'sender_district',
                    'outer_region': 'sender_outer_region',
                    'inner_region': 'sender_inner_region',
                }), on=['carrier', 'sender_province', 'sender_district'], how='left').merge(
                phan_vung_nvc.rename(columns={
                    'outer_region': 'receiver_outer_region',
                    'inner_region': 'receiver_inner_region',
                }), on=['carrier', 'receiver_province', 'receiver_district'], how='left')
        )
        valid_order_df['order_type'] = valid_order_df.apply(type_of_delivery, axis=1)
        valid_order_df['order_type_id'] = valid_order_df['order_type'].map(MAPPING_ORDER_TYPE_ID)
        valid_order_df['sys_order_type_id'] = valid_order_df.apply(type_of_system_delivery, axis=1)

        valid_order_df['sent_at'] = None
        valid_order_df['order_status'] = None
        valid_order_df['picked_at'] = None
        valid_order_df['carrier_updated_at'] = None
        valid_order_df['last_delivering_at'] = None
        valid_order_df['date'] = None

        valid_order_df['created_at'] = pd.to_datetime(valid_order_df['created_at'], errors='coerce')
        valid_order_df['sent_at'] = pd.to_datetime(valid_order_df['sent_at'], errors='coerce')
        valid_order_df['picked_at'] = pd.to_datetime(valid_order_df['picked_at'], errors='coerce')
        valid_order_df['carrier_updated_at'] = pd.to_datetime(valid_order_df['carrier_updated_at'], errors='coerce')
        valid_order_df['last_delivering_at'] = pd.to_datetime(valid_order_df['last_delivering_at'], errors='coerce')
        valid_order_df['carrier_delivered_at'] = pd.to_datetime(valid_order_df['carrier_delivered_at'],
                                                                 errors='coerce')
        valid_order_df['date'] = pd.to_datetime(valid_order_df['date'], errors='coerce')
        valid_order_df = valid_order_df[[
            'created_at', 'order_code', 'carrier', 'weight',
            'sender_province', 'sender_district', 'receiver_province', 'receiver_district',
            'sent_at', 'order_status', 'carrier_status',
            'order_type', 'order_type_id', 'sys_order_type_id',
            'delivery_count', 'delivery_type', 'is_returned',
            'picked_at', 'carrier_updated_at', 'last_delivering_at', 'carrier_delivered_at', 'date',
        ]]

        set_carrier = set(valid_order_df['carrier'].unique().tolist())
        set_norm_full_carrier = set(MAPPING_CARRIER_ID.keys())
        assert set_carrier - set_norm_full_carrier == set(), 'Ops, Tên nhà vận chuyển chưa được chuẩn hóa'

        print('Lưu thông tin...')
        valid_order_df.to_parquet(ROOT_PATH + '/processed_data/order.parquet', index=False)
    else:
        port = settings.SQLALCHEMY_DATABASE_URI
        engine = create_engine(port)
        valid_order_df = pd.read_sql_query('select * from db_schema.order', con=engine)

        valid_order_df['carrier'] = valid_order_df['carrier_id'].map(MAPPING_ID_CARRIER)
        valid_order_df['delivery_type'] = valid_order_df['pickup'].map({'0': 'Gửi Bưu Cục', '1': 'Lấy Tận Nơi'})
        valid_order_df['is_returned'] = valid_order_df['barter'].map({'0': False, '1': True})

        valid_order_df = valid_order_df.rename(columns={
            'sender_province': 'sender_province_code',
            'sender_district': 'sender_district_code',
            'receiver_province': 'receiver_province_code',
            'receiver_district': 'receiver_district_code'
        })
        valid_order_df = (
            valid_order_df.merge(
                PROVINCE_MAPPING_DISTRICT_DF.rename(columns={
                    'province': 'sender_province',
                    'district': 'sender_district',
                    'province_code': 'sender_province_code',
                    'district_code': 'sender_district_code',
                }), on=['sender_province_code', 'sender_district_code'], how='left'
            ).merge(
                PROVINCE_MAPPING_DISTRICT_DF.rename(columns={
                    'province': 'receiver_province',
                    'district': 'receiver_district',
                    'province_code': 'receiver_province_code',
                    'district_code': 'receiver_district_code',
                }), on=['receiver_province_code', 'receiver_district_code'], how='left'
            )
        )

        phan_vung_nvc = pd.read_parquet(ROOT_PATH + '/processed_data/phan_vung_nvc.parquet')
        phan_vung_nvc = phan_vung_nvc[
            ['carrier', 'receiver_province', 'receiver_district', 'outer_region', 'inner_region']]

        valid_order_df = (
            valid_order_df.merge(
                phan_vung_nvc.rename(columns={
                    'receiver_province': 'sender_province',
                    'receiver_district': 'sender_district',
                    'outer_region': 'sender_outer_region',
                    'inner_region': 'sender_inner_region',
                }), on=['carrier', 'sender_province', 'sender_district'], how='left').merge(
                phan_vung_nvc.rename(columns={
                    'outer_region': 'receiver_outer_region',
                    'inner_region': 'receiver_inner_region',
                }), on=['carrier', 'receiver_province', 'receiver_district'], how='left')
        )

        valid_order_df['order_type'] = valid_order_df.apply(type_of_delivery, axis=1)
        valid_order_df['order_type_id'] = valid_order_df['order_type'].map(MAPPING_ORDER_TYPE_ID)
        valid_order_df['sys_order_type_id'] = valid_order_df.apply(type_of_system_delivery, axis=1)

        valid_order_df['created_at'] = pd.to_datetime(valid_order_df['created_at'], errors='coerce')
        valid_order_df['sent_at'] = pd.to_datetime(valid_order_df['sent_at'], errors='coerce')
        valid_order_df['picked_at'] = pd.to_datetime(valid_order_df['picked_at'], errors='coerce')
        valid_order_df['carrier_updated_at'] = pd.to_datetime(valid_order_df['carrier_updated_at'], errors='coerce')
        valid_order_df['last_delivering_at'] = pd.to_datetime(valid_order_df['last_delivering_at'], errors='coerce')
        valid_order_df['carrier_delivered_at'] = pd.to_datetime(valid_order_df['carrier_delivered_at'],
                                                                 errors='coerce')
        valid_order_df['date'] = pd.to_datetime(valid_order_df['date'], errors='coerce')
        valid_order_df = valid_order_df[[
            'created_at', 'order_code', 'carrier', 'weight',
            'sender_province', 'sender_district', 'receiver_province', 'receiver_district',
            'sent_at', 'order_status', 'carrier_status',
            'order_type', 'order_type_id', 'sys_order_type_id',
            'delivery_count', 'delivery_type', 'is_returned',
            'picked_at', 'carrier_updated_at', 'last_delivering_at', 'carrier_delivered_at', 'date',
        ]]

        # Chỉ lấy thông tin giao dịch từ n_days_back trở lại
        valid_order_df = valid_order_df.loc[
            valid_order_df['created_at'] >=
            (run_date - timedelta(days=n_days_back))
        ]
        valid_order_df = valid_order_df.sort_values('date', ascending=False).drop_duplicates('order_code', keep='first')

        # 4. Lưu thông tin
        valid_order_df.to_parquet(ROOT_PATH + '/processed_data/order.parquet', index=False)
