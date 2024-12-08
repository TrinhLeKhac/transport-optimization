import optparse
import sys
from pathlib import Path

ROOT_PATH = str(Path(__file__).parent.parent.parent)
sys.path.append(ROOT_PATH)

from scripts.utilities.helper import *
from scripts.utilities.config import *
from dateutil.relativedelta import relativedelta
import gc

FINAL_FULL_COLS = [
    'carrier', 'carrier_id',
    'preferred_carrier', 'preferred_carrier_id',
    'sender_province_code', 'sender_district_code',
    'receiver_province_code', 'receiver_district_code',
    'sender_province', 'sender_district',
    'receiver_province', 'receiver_district',
    'order_type', 'order_type_id', 'sys_order_type_id',
    'orders_in_1_month', 'ndays_in_1_month',
    'orders_in_2_month', 'ndays_in_2_month',
]

API_COLS = [
    'carrier_id',
    'sender_province_code', 'sender_district_code',
    'receiver_province_code', 'receiver_district_code',
    'order_type_id', 'sys_order_type_id',
]


def get_top_percent(group, sort_col, ascending=True, pct=0.25):
    sorted_group = group.sort_values(by=sort_col, ascending=ascending)
    top_n = max(1, int(len(sorted_group) * pct))
    return sorted_group.head(top_n)


def get_metadata_tuyen_uu_tien(run_date_str, n_months_back=2):
    run_date = datetime.strptime(run_date_str, '%Y-%m-%d')

    df_target = pd.read_parquet(ROOT_PATH + '/processed_data/total_order.parquet')
    df_target = df_target.loc[
        df_target['picked_at'].notna()
        & df_target['last_delivering_at'].notna()
        & (df_target['last_delivering_at'] >= (run_date - relativedelta(months=n_months_back)))
        & (df_target['last_delivering_at'] < run_date)
        ]
    df_target['delta_hour'] = (df_target['last_delivering_at'] - df_target['picked_at']).dt.total_seconds() / 60 / 60

    get_top_by_15_pct_df = df_target.groupby("order_type_id", group_keys=False).apply(get_top_percent,
                                                                                      sort_col='delta_hour',
                                                                                      ascending=True, pct=0.15)
    get_top_by_15_pct_df['type'] = 'top 15%'

    get_top_by_20_pct_df = df_target.groupby("order_type_id", group_keys=False).apply(get_top_percent,
                                                                                      sort_col='delta_hour',
                                                                                      ascending=True, pct=0.2)
    get_top_by_20_pct_df['type'] = 'top 20%'

    get_top_by_25_pct_df = df_target.groupby("order_type_id", group_keys=False).apply(get_top_percent,
                                                                                      sort_col='delta_hour',
                                                                                      ascending=True, pct=0.25)
    get_top_by_25_pct_df['type'] = 'top 25%'

    get_top_by_pct_df = pd.concat([get_top_by_15_pct_df, get_top_by_20_pct_df, get_top_by_25_pct_df])
    meta_priority_route_df = get_top_by_pct_df.groupby(['order_type_id', 'type'])['delta_hour'].mean().reset_index()
    meta_priority_route_df['rounded_delta_hour'] = np.round(meta_priority_route_df['delta_hour'], 2)
    meta_priority_route_df = meta_priority_route_df.sort_values(['type', 'delta_hour']).reset_index(drop=True)

    meta_priority_route_df['idea_delta_hour'] = meta_priority_route_df['rounded_delta_hour']
    meta_priority_route_df.loc[meta_priority_route_df['rounded_delta_hour'] < 24, 'idea_delta_hour'] = 24
    meta_priority_route_df['order_type'] = meta_priority_route_df['order_type_id'].map(MAPPING_ID_ORDER_TYPE)
    meta_priority_route_df = meta_priority_route_df[
        ['order_type', 'order_type_id', 'type', 'delta_hour', 'rounded_delta_hour', 'idea_delta_hour']]

    meta_priority_route_df.to_parquet(ROOT_PATH + '/processed_data/meta_priority_route.parquet', index=False)


def get_data_tuyen_uu_tien(run_date_str, n_months_back=2, priority_type='top 25%'):
    run_date = datetime.strptime(run_date_str, '%Y-%m-%d')

    print('1. Xử lý data giao dịch...')
    df_target = pd.read_parquet(ROOT_PATH + '/processed_data/total_order.parquet')
    df_target = df_target.loc[
        df_target['picked_at'].notna()
        & df_target['last_delivering_at'].notna()
        & (df_target['last_delivering_at'] >= (run_date - relativedelta(months=n_months_back)))
        & (df_target['last_delivering_at'] < run_date)
        ]
    df_target['delta_hour'] = (df_target['last_delivering_at'] - df_target['picked_at']).dt.total_seconds() / 60 / 60

    df_target['is_1_month'] = False
    df_target['is_2_month'] = False

    df_target['day_last_delivering_at'] = df_target['last_delivering_at'].dt.date

    df_target.loc[(df_target['last_delivering_at'] < run_date) & (
            df_target['last_delivering_at'] >= (run_date - relativedelta(months=1))), 'is_1_month'] = True
    df_target.loc[(df_target['last_delivering_at'] < run_date) & (
            df_target['last_delivering_at'] >= (run_date - relativedelta(months=1))), 'day_last_delivering_at_1m'] = \
        df_target['day_last_delivering_at']

    df_target.loc[(df_target['last_delivering_at'] < run_date) & (
            df_target['last_delivering_at'] >= (run_date - relativedelta(months=2))), 'is_2_month'] = True
    df_target.loc[(df_target['last_delivering_at'] < run_date) & (
            df_target['last_delivering_at'] >= (run_date - relativedelta(months=2))), 'day_last_delivering_at_2m'] = \
        df_target['day_last_delivering_at']

    print('Done\n')

    print('2. Lấy metadata tuyến ưu tiên...')
    meta_priority_route_df = pd.read_parquet(ROOT_PATH + '/processed_data/meta_priority_route.parquet')
    meta_priority_route_df = meta_priority_route_df.loc[meta_priority_route_df['type'] == priority_type][
        ['order_type_id', 'idea_delta_hour']]
    print('Done\n')

    print('3. Transform data tuyến ưu tiên...')
    df_target_modified = df_target.merge(meta_priority_route_df, on='order_type_id', how='inner')
    priority_df = df_target_modified.loc[
        (df_target_modified['delta_hour'] <= df_target_modified['idea_delta_hour'])
        & (df_target_modified['picked_at'].dt.hour < 18)
        & (df_target_modified['last_delivering_at'].dt.hour < 10)
        ]

    priority_df.to_parquet(ROOT_PATH + '/processed_data/order_with_priority_route_streamlit.parquet', index=False)

    grouped_priority_df = (
        priority_df
        .groupby(['carrier', 'sender_province_code', 'sender_district_code', 'receiver_province_code',
                  'receiver_district_code', 'order_type_id', 'sys_order_type_id'])
        .agg(
            orders_in_1_month=('is_1_month', 'sum'),
            ndays_in_1_month=('day_last_delivering_at_1m', 'nunique'),
            orders_in_2_month=('is_2_month', 'sum'),
            ndays_in_2_month=('day_last_delivering_at_2m', 'nunique'),
        ).reset_index()
    )
    print('Done\n')

    # Logic ưu tiên
    priority_columns = [
        "ndays_in_1_month", "orders_in_1_month",
        "ndays_in_2_month", "orders_in_2_month",
    ]

    print('4. Chọn nhà vận chuyển ưu tiên hơn trong cùng tuyến...')

    def get_preferred_carrier(group):
        return group.sort_values(by=priority_columns, ascending=False).iloc[0]

    preferred_carrier_df = grouped_priority_df.groupby(
        ['sender_province_code', 'sender_district_code', 'receiver_province_code', 'receiver_district_code',
         'order_type_id', 'sys_order_type_id']
    ).apply(get_preferred_carrier).reset_index(drop=True)
    preferred_carrier_df = preferred_carrier_df.rename(columns={'carrier': 'preferred_carrier'})

    final_priority_df = (
        grouped_priority_df.merge(
            preferred_carrier_df[
                ["preferred_carrier", 'sender_province_code', 'sender_district_code', 'receiver_province_code',
                 'receiver_district_code', 'order_type_id']],
            on=['sender_province_code', 'sender_district_code', 'receiver_province_code', 'receiver_district_code',
                'order_type_id'],
            how='left'
        )
    )
    final_priority_df['order_type'] = final_priority_df['order_type_id'].map(MAPPING_ID_ORDER_TYPE)
    final_priority_df['carrier_id'] = final_priority_df['carrier'].map(MAPPING_CARRIER_ID)
    final_priority_df['preferred_carrier_id'] = final_priority_df['preferred_carrier'].map(MAPPING_CARRIER_ID)
    final_priority_df['sys_order_type_id'] = final_priority_df['sys_order_type_id'].astype('int')

    final_priority_df = (
        final_priority_df.merge(
            PROVINCE_MAPPING_DISTRICT_DF.rename(columns={
                'province_code': 'sender_province_code',
                'district_code': 'sender_district_code',
                'province': 'sender_province',
                'district': 'sender_district'
            }), on=['sender_province_code', 'sender_district_code'], how='left')
        .merge(
            PROVINCE_MAPPING_DISTRICT_DF.rename(columns={
                'province_code': 'receiver_province_code',
                'district_code': 'receiver_district_code',
                'province': 'receiver_province',
                'district': 'receiver_district',
            }), on=['receiver_province_code', 'receiver_district_code'], how='left')
        [FINAL_FULL_COLS]
        .sort_values(
            ['sender_province_code', 'sender_district_code', 'receiver_province_code', 'receiver_district_code',
             'order_type', 'carrier'])
    )
    api_priority_df = (
        final_priority_df.loc[final_priority_df[
            ['sender_province_code', 'sender_district_code', 'receiver_province_code',
             'receiver_district_code']].duplicated(keep=False)]
        [API_COLS].rename(columns={
            'order_type_id': 'new_type',
            'sys_order_type_id': 'route_type'
        })
    )

    final_priority_df.to_parquet(ROOT_PATH + '/output/priority_route_full.parquet', index=False)
    api_priority_df.to_parquet(ROOT_PATH + '/output/priority_route_api.parquet', index=False)


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

    n_months_back = 2
    priority_type = 'top 25%'

    get_metadata_tuyen_uu_tien(options.run_date, n_months_back=n_months_back)
    get_data_tuyen_uu_tien(
        run_date_str=options.run_date,
        n_months_back=n_months_back,
        priority_type=priority_type
    )