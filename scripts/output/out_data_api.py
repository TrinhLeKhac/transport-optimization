import optparse
import sys
from pathlib import Path

ROOT_PATH = str(Path(__file__).parent.parent.parent)
sys.path.append(ROOT_PATH)

from scripts.utilities.helper import *
from scripts.utilities.config import *
from scripts.transform.total_transform import total_transform

API_FULL_COLS = [
    'receiver_province_code', 'receiver_province',
    'receiver_district_code', 'receiver_district',
    'carrier_id', 'carrier', 'order_type',
    'order_type_id', 'sys_order_type_id', 'carrier_status', 'carrier_status_comment',
    'estimate_delivery_time_details', 'estimate_delivery_time',
    'customer_best_carrier_id',
    'fastest_carrier_id', 'highest_score_carrier_id',
    'total_order', 'delivery_success_rate_id',
    'delivery_success_rate', 'score', 'star',
]
API_FULL_COLS_RENAMED = [
    'receiver_province_code', 'receiver_province',
    'receiver_district_code', 'receiver_district',
    'carrier_id', 'carrier', 'order_type',
    'new_type', 'route_type', 'status', 'description',
    'time_data', 'time_display',
    'for_shop',
    'speed_ranking', 'score_ranking',
    'total_order', 'rate_ranking',
    'rate', 'score', 'star',
]

API_COLS = [
    'receiver_province_code', 'receiver_district_code',
    'carrier_id', 'order_type_id', 'sys_order_type_id', 'carrier_status', 'carrier_status_comment',
    'estimate_delivery_time_details', 'estimate_delivery_time',
    'fastest_carrier_id', 'highest_score_carrier_id',
    'customer_best_carrier_id', 'total_order', 'delivery_success_rate_id',
    'delivery_success_rate', 'score', 'star',
]

API_COLS_RENAMED = [
    'receiver_province_code', 'receiver_district_code',
    'carrier_id', 'new_type', 'route_type', 'status', 'description',
    'time_data', 'time_display',
    'speed_ranking', 'score_ranking',
    'for_shop', 'total_order', 'rate_ranking',
    'rate', 'score', 'star',
]


def round_value(x):
    th1 = round(x - 0.25, 1)
    th2 = round(x + 0.25, 1)
    return '{} - {} ngày'.format(th1, th2)


def get_agg(
        target_df,
        partition_cols=['receiver_province_code', 'receiver_district_code', 'new_type'],
        target_col='time_data',
        n_top=3,
        asc=True
):
    result_df = (
        target_df[partition_cols + [target_col]]
            .sort_values(partition_cols + [target_col], ascending=[True, True, True, asc])
            .groupby(partition_cols)
            .head(n_top)
            .groupby(partition_cols)
            .mean()
            .reset_index()
    )
    return result_df


def customer_best_carrier(data_api_df):
    data_api_df['combine_col'] = data_api_df[["delivery_success_rate", "total_order"]].apply(tuple, axis=1)

    data_api_df["delivery_success_rate_id"] = \
        data_api_df.groupby(["receiver_province_code", "receiver_district_code", "order_type_id"])["combine_col"].rank(
            method="dense", ascending=False).astype(int)

    data_api_df['wscore'] = data_api_df['fastest_carrier_id'] * 1.4 + data_api_df['delivery_success_rate_id'] * 1.2 + \
                            data_api_df['highest_score_carrier_id']

    data_api_df["customer_best_carrier_id"] = \
        data_api_df.groupby(["receiver_province_code", "receiver_district_code", "order_type_id"])["wscore"].rank(
            method="dense", ascending=True).astype(int)

    return data_api_df.drop(['combine_col', 'wscore'], axis=1)


def calculate_vpn(group):
    # Kiểm tra xem group là Series hay DataFrame
    if isinstance(group, pd.Series):
        group = group.to_frame().T  # Chuyển Series thành DataFrame

    if 'carrier_id' not in group.columns:
        raise KeyError("The 'carrier_id' column is missing in the group DataFrame")

    # Thoi gian van chuyen trung binh (vtp + ghn + spx)
    time_data = group.loc[group['carrier_id'].isin([4, 2, 10])]['time_data'].mean()

    # Chat luong giao hang trung binh (spx + best + nin)
    score = group.loc[group['carrier_id'].isin([10, 6, 7])]['score'].mean()

    # ty le thanh cong trung binh (vtp + best + ghn)
    rate = group.loc[group['carrier_id'].isin([4, 6, 2])]['rate'].mean()

    # Trả về Series với tên các cột mong muốn
    return pd.Series({'time_data_modified': time_data, 'score_modified': score, 'rate_modified': rate})


def calculate_lex(group):
    # Kiểm tra xem group là Series hay DataFrame
    if isinstance(group, pd.Series):
        group = group.to_frame().T  # Chuyển Series thành DataFrame

    if 'carrier_id' not in group.columns:
        raise KeyError("The 'carrier_id' column is missing in the group DataFrame")

    # Thời gian vận chuyển trung bình (best + nin + spx)
    time_data = group.loc[group['carrier_id'].isin([6, 7, 10]), 'time_data'].mean()

    # Chất lượng giao hàng trung bình (vtp + best + nin)
    score = group.loc[group['carrier_id'].isin([4, 6, 7]), 'score'].mean()

    # Tỷ lệ thành công trung bình (spx + ghn)
    rate = group.loc[group['carrier_id'].isin([10, 2]), 'rate'].mean()

    # Trả về Series với tên các cột mong muốn
    return pd.Series({'time_data_modified': time_data, 'score_modified': score, 'rate_modified': rate})


def modified_output_api(df_api_full):
    main_data_api = df_api_full.loc[~df_api_full['carrier_id'].isin([13, 14])]

    # Calculate VNPost modified data api
    vnp_data_api = main_data_api.groupby(['receiver_province_code', 'receiver_district_code', 'new_type']).apply(
        calculate_vpn).reset_index()
    vnp_data_api['carrier_id'] = 13

    # Calculate Lazada Logistics modified data api
    lex_data_api = main_data_api.groupby(['receiver_province_code', 'receiver_district_code', 'new_type']).apply(
        calculate_lex).reset_index()
    lex_data_api['carrier_id'] = 14

    # Replace old value VNPost by new value
    df_api_full_final = df_api_full.merge(vnp_data_api,
                                          on=['carrier_id', 'receiver_province_code', 'receiver_district_code',
                                              'new_type'], how='left')
    df_api_full_final.loc[df_api_full_final['carrier_id'] == 13, 'time_data'] = df_api_full_final['time_data_modified']
    df_api_full_final.loc[df_api_full_final['carrier_id'] == 13, 'score'] = df_api_full_final['score_modified']
    df_api_full_final.loc[df_api_full_final['carrier_id'] == 13, 'rate'] = df_api_full_final['rate_modified']
    df_api_full_final = df_api_full_final.drop(['time_data_modified', 'score_modified', 'rate_modified'], axis=1)

    # Replace old value Lazada Logistics by new value
    df_api_full_final = df_api_full_final.merge(lex_data_api,
                                                on=['carrier_id', 'receiver_province_code', 'receiver_district_code',
                                                    'new_type'], how='left')
    df_api_full_final.loc[df_api_full_final['carrier_id'] == 14, 'time_data'] = df_api_full_final['time_data_modified']
    df_api_full_final.loc[df_api_full_final['carrier_id'] == 14, 'score'] = df_api_full_final['score_modified']
    df_api_full_final.loc[df_api_full_final['carrier_id'] == 14, 'rate'] = df_api_full_final['rate_modified']
    df_api_full_final = df_api_full_final.drop(['time_data_modified', 'score_modified', 'rate_modified'], axis=1)

    return df_api_full_final


def out_data_api(
    run_date_str,
    carriers=ACTIVE_CARRIER,
    full_cols=False,
    show_logs=True,
    save_output=True
):
    if show_logs:
        print('1. Transform dữ liệu...')
    (
        ngung_giao_nhan, danh_gia_zns,
        ti_le_giao_hang, chat_luong_noi_bo,
        thoi_gian_giao_hang, kho_giao_nhan, don_ton_dong
    ) = total_transform(run_date_str, show_logs=False)

    if show_logs:
        print('2. Tính toán quận huyện quá tải')
    qua_tai1 = ngung_giao_nhan.loc[ngung_giao_nhan['score'].isin(OVERLOADING_SCORE_DICT['Ngưng giao nhận'])]
    qua_tai1 = qua_tai1[['receiver_province', 'receiver_district', 'carrier', 'status']].rename(
        columns={'status': 'carrier_status_comment'})

    qua_tai2 = danh_gia_zns.loc[
        danh_gia_zns['score'].isin(OVERLOADING_SCORE_DICT['Đánh giá ZNS'])]
    qua_tai2 = qua_tai2[['receiver_province', 'receiver_district', 'carrier', 'status']].rename(
        columns={'status': 'carrier_status_comment'})
    qua_tai2.loc[
        qua_tai2[
            'carrier_status_comment'] == 'Loại', 'carrier_status_comment'] = 'Tổng số đánh giá ZNS 1, 2 sao >= 30% tổng đơn'

    qua_tai3 = ti_le_giao_hang.loc[
        ti_le_giao_hang['score'].isin(OVERLOADING_SCORE_DICT['Tỉ lệ giao hàng'])]
    qua_tai3 = qua_tai3[['receiver_province', 'receiver_district', 'carrier', 'status']].rename(
        columns={'status': 'carrier_status_comment'})

    qua_tai4 = chat_luong_noi_bo.loc[chat_luong_noi_bo['score'].isin(OVERLOADING_SCORE_DICT['Chất lượng nội bộ'])]
    qua_tai4['carrier_status_comment'] = qua_tai4['status'] + ' (clnb)'
    qua_tai4 = qua_tai4[['receiver_province', 'receiver_district', 'carrier', 'carrier_status_comment']]

    qua_tai5 = thoi_gian_giao_hang.loc[thoi_gian_giao_hang['score'].isin(OVERLOADING_SCORE_DICT['Thời gian giao hàng'])]
    qua_tai5['carrier_status_comment'] = qua_tai5['status'] + ' (' + qua_tai5['order_type'] + ')'
    qua_tai5 = qua_tai5[['receiver_province', 'receiver_district', 'carrier', 'carrier_status_comment']]

    qua_tai6 = kho_giao_nhan.loc[kho_giao_nhan['score'].isin(OVERLOADING_SCORE_DICT['Có kho giao nhận'])]
    qua_tai6 = qua_tai6[['receiver_province', 'receiver_district', 'carrier', 'status']].rename(
        columns={'status': 'carrier_status_comment'})

    qua_tai7 = don_ton_dong.loc[don_ton_dong['score'].isin(OVERLOADING_SCORE_DICT['Đơn tồn đọng'])]
    qua_tai7 = qua_tai7[['receiver_province', 'receiver_district', 'carrier', 'carrier_status_comment']]

    qua_tai = pd.concat([qua_tai1, qua_tai2, qua_tai3, qua_tai4, qua_tai5, qua_tai6, qua_tai7])

    qua_tai = (
        qua_tai.groupby([
            'receiver_province', 'receiver_district', 'carrier'
        ])['carrier_status_comment'].apply(lambda x: ' + '.join(x))
            .reset_index()
    )

    if show_logs:
        print('3. Xử lý data thời gian giao dịch')
    thoi_gian_giao_hang = thoi_gian_giao_hang.rename(columns={'delivery_time_mean_h': 'estimate_delivery_time_details'})
    thoi_gian_giao_hang['estimate_delivery_time_details'] = np.round(
        thoi_gian_giao_hang['estimate_delivery_time_details'] / 24, 2)
    thoi_gian_giao_hang['estimate_delivery_time'] = thoi_gian_giao_hang['estimate_delivery_time_details'].apply(
        round_value)

    # Thời gian giao hàng default
    active_carrier_df = pd.DataFrame(data={
        'carrier': carriers,
    })
    loai_van_chuyen_df = pd.DataFrame(THOI_GIAN_GIAO_HANG_DEFAULT.items(),
                                      columns=['order_type', 'default_delivery_time'])
    loai_van_chuyen_df['default_delivery_time_details'] = [2, 2, 2, 2, 1, 2, 3, 3, 3, 4]

    thoi_gian_giao_hang_default = (
        PROVINCE_MAPPING_DISTRICT_DF[['province', 'district']].rename(columns={
            'province': 'receiver_province',
            'district': 'receiver_district',
        })
        .merge(
            active_carrier_df.merge(loai_van_chuyen_df, how='cross'),
            how='cross'
        )
    )

    thoi_gian_giao_hang_final = (
        thoi_gian_giao_hang_default.merge(
            thoi_gian_giao_hang,
            on=['receiver_province', 'receiver_district', 'carrier', 'order_type'],
            how='left'
        )
    )

    thoi_gian_giao_hang_final.loc[
        thoi_gian_giao_hang_final['total_order'] == 0,
        'estimate_delivery_time'
    ] = thoi_gian_giao_hang_final['default_delivery_time']

    thoi_gian_giao_hang_final.loc[
        thoi_gian_giao_hang_final['total_order'] == 0,
        'estimate_delivery_time_details'
    ] = thoi_gian_giao_hang_final['default_delivery_time_details']

    if show_logs:
        print('4. Xủ lý score')
    score_df_list = []

    for focus_df in [ngung_giao_nhan, danh_gia_zns, ti_le_giao_hang, chat_luong_noi_bo, thoi_gian_giao_hang,
                     kho_giao_nhan, don_ton_dong]:
        target_df = focus_df.copy()
        target_df['weight_score'] = target_df['score'] * target_df['criteria_weight']
        score_df_list.append(target_df[['receiver_province', 'receiver_district', 'carrier', 'weight_score']])

    score_df = pd.concat(score_df_list, ignore_index=False)
    score_final = score_df.groupby(['receiver_province', 'receiver_district', 'carrier'])[
        'weight_score'].mean().reset_index()
    score_final = score_final.rename(columns={'weight_score': 'score'})

    q_lower = score_final['score'].quantile(0.002)
    q_upper = score_final['score'].quantile(0.998)

    score_final.loc[score_final['score'] < q_lower, 'score'] = q_lower
    score_final.loc[score_final['score'] > q_upper, 'score'] = q_upper
    score_final['score'] = (score_final['score'] - q_lower) / (q_upper - q_lower)
    score_final['score'] = score_final['score'] * 5  # Change score to range 0-5
    score_final['score'] = np.round(score_final['score'], 2)

    if show_logs:
        print('5. Combine api data')
    api_data_final = (
        thoi_gian_giao_hang_final[[
            'receiver_province', 'receiver_district', 'carrier', 'order_type',
            'estimate_delivery_time', 'estimate_delivery_time_details',
        ]].merge(score_final, on=['receiver_province', 'receiver_district', 'carrier'], how='inner')
            .merge(
            ti_le_giao_hang[[
                'receiver_province', 'receiver_district', 'carrier', 'total_order', 'delivery_success_rate'
            ]], on=['receiver_province', 'receiver_district', 'carrier'],
            how='inner'
        )
    )
    api_data_final['delivery_success_rate'] = np.round(api_data_final['delivery_success_rate'] * 100, 2)

    # Change delivery_success_rate random from 80% - 85% toward region have total_order = 0
    success_rate_modified_1 = api_data_final.loc[api_data_final['total_order'] == 0][
        ['receiver_province', 'receiver_district', 'carrier']].drop_duplicates()

    success_rate_modified_1['delivery_success_rate_modified'] = np.round(np.random.uniform(80, 85, len(success_rate_modified_1)), 2)
    api_data_final = api_data_final.merge(success_rate_modified_1, on=['receiver_province', 'receiver_district', 'carrier'], how='left')
    api_data_final.loc[api_data_final['total_order'] == 0, 'delivery_success_rate'] = api_data_final['delivery_success_rate_modified']
    api_data_final.drop('delivery_success_rate_modified', axis=1, inplace=True)

    # Change delivery_success_rate random from 96% - 98% toward region have delivery_success_rate = 100
    success_rate_modified_2 = api_data_final.loc[api_data_final['delivery_success_rate'] == 100][
        ['receiver_province', 'receiver_district', 'carrier']].drop_duplicates()

    success_rate_modified_2['delivery_success_rate_modified'] = np.round(
        np.random.uniform(96, 98, len(success_rate_modified_2)), 2)
    api_data_final = api_data_final.merge(success_rate_modified_2,
                                          on=['receiver_province', 'receiver_district', 'carrier'], how='left')
    api_data_final.loc[api_data_final['delivery_success_rate'] == 100, 'delivery_success_rate'] = api_data_final[
        'delivery_success_rate_modified']
    api_data_final.drop('delivery_success_rate_modified', axis=1, inplace=True)

    api_data_final['combine_col'] = api_data_final[["delivery_success_rate", "total_order"]].apply(tuple, axis=1)
    api_data_final["delivery_success_rate_id"] = \
        api_data_final.groupby(["receiver_province", "receiver_district", "order_type"])["combine_col"].rank(
            method="dense", ascending=False).astype(int)
    api_data_final.drop('combine_col', axis=1, inplace=True)

    if show_logs:
        print('6. Gắn thông tin quá tải')
    api_data_final = api_data_final.merge(qua_tai, on=['receiver_province', 'receiver_district', 'carrier'], how='left')
    api_data_final.loc[api_data_final['total_order'] == 0, 'carrier_status_comment'] = 'Không có đơn hàng'
    api_data_final['carrier_status_comment'] = api_data_final['carrier_status_comment'].fillna('Bình thường')

    api_data_final['carrier_status'] = 2
    api_data_final.loc[api_data_final['carrier_status_comment'].isin(['Bình thường', 'Không có đơn hàng']), 'carrier_status'] = 0
    api_data_final.loc[api_data_final['carrier_status_comment'].str.contains('Quá tải'), 'carrier_status'] = 1

    api_data_final['carrier_id'] = api_data_final['carrier'].map(MAPPING_CARRIER_ID)
    api_data_final = (
        api_data_final.merge(
            PROVINCE_MAPPING_DISTRICT_DF.rename(columns={
                'province': 'receiver_province',
                'district': 'receiver_district',
                'province_code': 'receiver_province_code',
                'district_code': 'receiver_district_code',
            }), on=['receiver_province', 'receiver_district'], how='left'
        )
    )
    api_data_final['order_type_id'] = api_data_final['order_type'].map(MAPPING_ORDER_TYPE_ID)

    if show_logs:
        print('7. Thông tin nhà vận chuyển nhanh nhất, hiệu quả nhất')
    api_data_final["fastest_carrier_id"] = \
        api_data_final.groupby(["receiver_province_code", "receiver_district_code", "order_type_id"])[
            "estimate_delivery_time_details"].rank(method="dense", ascending=True)
    api_data_final["fastest_carrier_id"] = api_data_final["fastest_carrier_id"].astype(int)

    api_data_final["highest_score_carrier_id"] = \
        api_data_final.groupby(["receiver_province_code", "receiver_district_code", "order_type_id"])["score"].rank(
            method="dense", ascending=False)
    api_data_final["highest_score_carrier_id"] = api_data_final["highest_score_carrier_id"].astype(int)

    if show_logs:
        print('8. Thông tin customer_best_carrier')
    # api_data_final = customer_best_carrier(api_data_final)

    # Force customer_best_carrier_id (for_shop) == -1
    # for_shop, for_partner will be calculated by different rule in SQL_QUERY_COMMAND
    api_data_final['customer_best_carrier_id'] = -1

    if show_logs:
        print('9. Thông tin số sao đánh giá của khách hàng')
    zns_df = pd.read_parquet(ROOT_PATH + '/processed_data/danh_gia_zns.parquet')
    zns_df = zns_df.groupby(['receiver_province', 'receiver_district', 'carrier']).agg(
        star=('n_stars', 'mean')).reset_index()
    zns_df['star'] = np.round(zns_df['star'], 1)

    api_data_final = api_data_final.merge(zns_df, on=['receiver_province', 'receiver_district', 'carrier'], how='left')
    api_data_final['star'] = api_data_final['star'].fillna(5.0)

    # # Nhu cầu business => lấy star bằng cột score
    # api_data_final['star'] = np.round(api_data_final['score'], 1)

    api_data_final['sys_order_type_id'] = api_data_final['order_type_id'].map(MAPPING_ORDER_TYPE_ID_ROUTE_TYPE)
    api_data_final['carrier_status'] = api_data_final['carrier_status'].astype(str)
    api_data_final['order_type_id'] = api_data_final['order_type_id'].astype(str)
    api_data_final['sys_order_type_id'] = api_data_final['sys_order_type_id'].astype(str)

    if full_cols:
        api_data_final = api_data_final[API_FULL_COLS]
        api_data_final.columns = API_FULL_COLS_RENAMED
    else:
        api_data_final = api_data_final[API_COLS]
        api_data_final.columns = API_COLS_RENAMED
    print('Shape: ', api_data_final.shape)
    print('Modifying 2 new carrier...')
    api_data_final = modified_output_api(api_data_final)
    if save_output:
        if show_logs:
            print('9. Lưu dữ liệu API')
        if not os.path.exists(ROOT_PATH + '/output'):
            os.makedirs(ROOT_PATH + '/output')
        api_data_final.to_parquet(ROOT_PATH + '/output/data_api.parquet', index=False)
    if show_logs:
        print('>>> Done\n')
    print('-' * 100)
    return api_data_final


def assign_supership_carrier(df_api, save_output=True):

    # 1. Get analytics of top 3 carrier
    time_data = get_agg(df_api, target_col='time_data', n_top=3, asc=True)
    rate = get_agg(df_api, target_col='rate', n_top=3, asc=False)
    score = get_agg(df_api, target_col='score', n_top=3, asc=False)
    star = get_agg(df_api, target_col='star', n_top=3, asc=False)

    total_order = get_agg(df_api, target_col='total_order', asc=False)
    total_order['total_order'] = total_order['total_order'].astype(int)

    # 2. Assign infor to SuperShip
    df_supership = (
        time_data.merge(rate, on=['receiver_province_code', 'receiver_district_code', 'new_type'], how='inner')
        .merge(score, on=['receiver_province_code', 'receiver_district_code', 'new_type'], how='inner')
        .merge(star, on=['receiver_province_code', 'receiver_district_code', 'new_type'], how='inner')
        .merge(total_order, on=['receiver_province_code', 'receiver_district_code', 'new_type'], how='inner')
    )

    df_supership['carrier_id'] = MAPPING_CARRIER_ID['SuperShip']
    df_supership['route_type'] = df_supership['new_type'].map(
        dict(zip(
            [str(i) for i in MAPPING_ORDER_TYPE_ID_ROUTE_TYPE.keys()],
            [str(i) for i in MAPPING_ORDER_TYPE_ID_ROUTE_TYPE.values()]
        ))
    )
    df_supership['status'] = '0'
    df_supership['description'] = 'Bình thường'
    df_supership['time_display'] = df_supership['time_data'].map(round_value)

    # 3. Recalculating metrics speed_ranking, score_ranking, rate_ranking, for_shop
    df_api_full = pd.concat([df_api, df_supership], ignore_index=True)
    df_api_full["speed_ranking"] = \
        df_api_full.groupby(["receiver_province_code", "receiver_district_code", "new_type"])[
            "time_data"].rank(method="dense", ascending=True)
    df_api_full["speed_ranking"] = df_api_full["speed_ranking"].astype(int)

    df_api_full["score_ranking"] = \
        df_api_full.groupby(["receiver_province_code", "receiver_district_code", "new_type"])["score"].rank(
            method="dense", ascending=False)
    df_api_full["score_ranking"] = df_api_full["score_ranking"].astype(int)

    df_api_full['combine_col'] = df_api_full[["rate", "total_order"]].apply(tuple, axis=1)

    df_api_full["rate_ranking"] = \
        df_api_full.groupby(["receiver_province_code", "receiver_district_code", "new_type"])["combine_col"].rank(
            method="dense", ascending=False).astype(int)

    df_api_full['wscore'] = df_api_full['speed_ranking'] * 1.4 + df_api_full['rate_ranking'] * 1.2 + df_api_full[
        'score_ranking']

    df_api_full["for_shop"] = \
        df_api_full.groupby(["receiver_province_code", "receiver_district_code", "new_type"])["wscore"].rank(
            method="dense", ascending=True).astype(int)
    df_api_full = df_api_full.drop(['combine_col', 'wscore'], axis=1)

    df_api_full['time_data'] = np.round(df_api_full['time_data'], 2)
    df_api_full['rate'] = np.round(df_api_full['rate'], 2)
    df_api_full['score'] = np.round(df_api_full['score'], 2)
    df_api_full['star'] = np.round(df_api_full['star'], 1)
    print('Shape after assigning: ', len(df_api_full))

    if save_output:
        df_api_full.to_parquet(ROOT_PATH + '/output/data_api.parquet', index=False)
    print('-' * 100)

    return df_api_full


if __name__ == '__main__':
    parser = optparse.OptionParser(description="Running mode")
    parser.add_option(
        '-r', '--run_date',
        type=str,
        # action="store", dest="run_date",
        # help="run_date string",
        default=f"{datetime.now().strftime('%Y-%m-%d')}"
    )
    options, args = parser.parse_args()
    # print(options.run_date)
    # print(type(options.run_date))

    try:
        print('Transforming output API from processed_data...')
        df_api = out_data_api(options.run_date)
    except Exception as e:
        error = type(e).__name__ + " – " + str(e)
        telegram_bot_send_error_message(error)

    include_supership = False
    if include_supership:
        try:
            print('Assigning SuperShip carrier...')
            _ = assign_supership_carrier(df_api)
        except Exception as e:
            error = type(e).__name__ + " – " + str(e)
            telegram_bot_send_error_message(error)
