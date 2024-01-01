from scripts.utilities.helper import *
from scripts.utilities.config import *


def get_don_ton_dong():
    ndate = datetime.strptime(datetime.now().strftime('%F'), '%Y-%m-%d')

    loai_van_chuyen_df = pd.DataFrame(THOI_GIAN_GIAO_HANG_DEFAULT.items(),
                                      columns=['order_type', 'default_delivery_time'])
    loai_van_chuyen_df['default_delivery_time_details'] = [48, 48, 48, 48, 24, 48, 72, 72, 72, 108]

    df_order = pd.read_parquet(ROOT_PATH + '/processed_data/order.parquet')
    df_order = df_order.sort_values('date', ascending=False).drop_duplicates('order_code', keep='first')
    df_order = df_order.loc[df_order['created_at'] >= (ndate - timedelta(days=30))]
    df_order = df_order[[
        'order_code', 'carrier', 'receiver_province', 'receiver_district',
        'order_type', 'picked_at', 'last_delivering_at'
    ]]

    max_delivering_time = df_order['last_delivering_at'].max()
    df_order['last_delivering_at'] = df_order['last_delivering_at'].fillna(max_delivering_time)
    df_order['delta_time_h'] = (df_order['last_delivering_at'] - df_order[
        'picked_at']).dt.total_seconds() / 60 / 60

    df_order = df_order.merge(loai_van_chuyen_df[['order_type', 'default_delivery_time_details']],
                              on='order_type', how='inner')
    df_order['is_late'] = df_order['delta_time_h'] > df_order['default_delivery_time_details']

    return df_order


def get_khu_vuc_ton_dong(threshold=10):
    df_order = get_don_ton_dong()

    df_order_analytic = df_order.groupby(['receiver_province', 'receiver_district', 'carrier', 'order_type']).agg(
        n_order_late=('is_late', 'sum')).reset_index()
    don_ton_dong = df_order_analytic.loc[df_order_analytic['n_order_late'] >= threshold]

    return don_ton_dong[['receiver_province', 'receiver_district', 'carrier', 'order_type']]
