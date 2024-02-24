import optparse
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


def tong_hop_thong_tin_giao_dich_full(run_date_str, n_days_back=30):
    run_date = datetime.strptime(run_date_str, '%Y-%m-%d')

    port = settings.SQLALCHEMY_DATABASE_URI
    engine = create_engine(port)

    print('Get order transaction...')
    valid_order_df = pd.read_sql_query('select * from db_schema.order', con=engine)

    # Chỉ lấy thông tin giao dịch từ n_days_back trở lại
    valid_order_df['created_at'] = pd.to_datetime(valid_order_df['created_at'], errors='coerce')
    valid_order_df = valid_order_df.loc[
        valid_order_df['created_at'] >=
        (run_date - timedelta(days=n_days_back))
        ]
    print(len(valid_order_df))

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

    valid_order_df = create_type_of_delivery(valid_order_df)
    valid_order_df['order_type'] = valid_order_df['order_type_id'].map(MAPPING_ID_ORDER_TYPE)

    # valid_order_df['created_at'] = pd.to_datetime(valid_order_df['created_at'], errors='coerce')
    valid_order_df['sent_at'] = pd.to_datetime(valid_order_df['sent_at'], errors='coerce')
    valid_order_df['picked_at'] = pd.to_datetime(valid_order_df['picked_at'], errors='coerce')
    valid_order_df['carrier_updated_at'] = pd.to_datetime(valid_order_df['carrier_updated_at'], errors='coerce')
    valid_order_df['last_delivering_at'] = pd.to_datetime(valid_order_df['last_delivering_at'], errors='coerce')
    valid_order_df['carrier_delivered_at'] = pd.to_datetime(valid_order_df['carrier_delivered_at'], errors='coerce')
    valid_order_df['date'] = pd.to_datetime(valid_order_df['date'], errors='coerce')

    valid_order_df = valid_order_df[[
        'created_at', 'order_code', 'carrier', 'weight',
        'sender_province', 'sender_district', 'sender_province_code', 'sender_district_code',
        'receiver_province', 'receiver_district', 'receiver_province_code', 'receiver_district_code',
        'sent_at', 'order_status', 'carrier_status',
        'order_type', 'order_type_id', 'sys_order_type_id',
        'delivery_count', 'delivery_type', 'is_returned',
        'picked_at', 'carrier_updated_at', 'last_delivering_at', 'carrier_delivered_at', 'date',
    ]]

    print('Min (created_at): ', valid_order_df['created_at'].min())
    print('Max (created_at): ', valid_order_df['created_at'].max())
    print('Shape: ', len(valid_order_df))

    # 4. Lưu thông tin
    valid_order_df.to_parquet(ROOT_PATH + '/processed_data/order_full.parquet', index=False)


if __name__ == '__main__':
    parser = optparse.OptionParser(description="Running mode")
    parser.add_option(
        '-r', '--run_date',
        action="store", dest="run_date",
        help="run_date string", default=f"{datetime.now().strftime('%Y-%m-%d')}"
    )
    options, args = parser.parse_args()

    tong_hop_thong_tin_giao_dich_full(run_date_str=options.run_date)
