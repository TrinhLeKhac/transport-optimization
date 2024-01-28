from scripts.utilities.helper import *
from scripts.utilities.config import *


def score_ton_dong(n_order_type, threshold=10):
    if n_order_type in [1, 2, 3, 4]:
        return f'Tồn đọng trên {threshold} đơn đối với {n_order_type} loại hình vận chuyển'
    elif n_order_type >= 5:
        return f'Tồn đọng trên {threshold} đơn đối với 4++ loại hình vận chuyển'
    else:
        return 'Không có thông tin'


def get_don_ton_dong(run_date_str, n_days_back=30):
    run_date = datetime.strptime(run_date_str, '%Y-%m-%d')
    loai_van_chuyen_df = pd.DataFrame(THOI_GIAN_GIAO_HANG_DEFAULT.items(),
                                      columns=['order_type', 'default_delivery_time'])
    loai_van_chuyen_df['default_delivery_time_details'] = [48 + 12, 48 + 12, 48 + 12, 48 + 12, 24 + 12, 48 + 12, 72 + 12, 72 + 12, 72 + 12, 108 + 12]

    df_order = pd.read_parquet(ROOT_PATH + '/processed_data/order.parquet')
    df_order = df_order.sort_values('date', ascending=False).drop_duplicates('order_code', keep='first')
    df_order = df_order.loc[df_order['created_at'] >= (run_date - timedelta(days=n_days_back))]
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


def get_khu_vuc_ton_dong(run_date_str, threshold=10):
    df_order = get_don_ton_dong(run_date_str)

    df_order_analytic = df_order.groupby(['receiver_province', 'receiver_district', 'carrier', 'order_type']).agg(
        n_order_late=('is_late', 'sum')).reset_index()
    don_ton_dong = df_order_analytic.loc[df_order_analytic['n_order_late'] > threshold]

    nghen_don = don_ton_dong.groupby([
        'receiver_province', 'receiver_district', 'carrier'
    ])['order_type'].apply(lambda x: ', '.join(x)).reset_index()
    nghen_don['carrier_status_comment'] = 'Nghẽn đơn (' + nghen_don['order_type'] + ')'

    don_ton_dong_final = don_ton_dong.groupby(['receiver_province', 'receiver_district', 'carrier']).agg(
        n_order_type=('order_type', 'nunique')).reset_index()
    don_ton_dong_final = don_ton_dong_final.merge(nghen_don, on=['receiver_province', 'receiver_district', 'carrier'],
                                                  how='inner')
    don_ton_dong_final['status'] = don_ton_dong_final['n_order_type'].map(
        lambda s: score_ton_dong(s, threshold=threshold))

    don_ton_dong_final = (
        PROVINCE_MAPPING_DISTRICT_CROSS_CARRIER_DF.merge(
            don_ton_dong_final, on=['receiver_province', 'receiver_district', 'carrier'], how='left'
        )
    )
    don_ton_dong_final['status'] = don_ton_dong_final['status'].fillna('Không có thông tin')
    don_ton_dong_final['carrier_status_comment'] = don_ton_dong_final['carrier_status_comment'].fillna('Bình thường')
    don_ton_dong_final['score'] = don_ton_dong_final['status'].map(TRONG_SO['Đơn tồn đọng']['Phân loại'])
    don_ton_dong_final['criteria'] = 'Đơn tồn đọng'
    don_ton_dong_final['criteria_weight'] = TRONG_SO['Đơn tồn đọng']['Tiêu chí']

    don_ton_dong_final = don_ton_dong_final[['receiver_province', 'receiver_district', 'carrier', 'carrier_status_comment', 'status', 'score', 'criteria', 'criteria_weight']]

    return don_ton_dong_final
