import numpy as np
import pandas as pd
import requests
import json
from unidecode import unidecode
from scripts.utilities.config import *
import streamlit as st
from functools import reduce
from datetime import datetime, timedelta
from time import time
import re
import os
import warnings
warnings.filterwarnings("ignore")
import requests
from config import Settings


def telegram_bot_send_message(
        bot_message,
        bot_token=Settings.TELEGRAM_BOT_TOKEN,
        bot_chat_id=Settings.TELEGRAM_CHAT_ID,
):
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chat_id + '&parse_mode=Markdown&text=' + bot_message
    res = requests.get(send_text)
    return res.json()


def telegram_bot_send_error_message(message):
    telegram_bot_send_message(f"""
        ❌❌❌ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Task run daily *FAILED*!!!  
    """)
    telegram_bot_send_message(f"""
        Details of error:  
        {message}
    """)


def telegram_bot_send_success_message():
    telegram_bot_send_message(f"""
        ✅✅✅ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Task run daily *SUCCESSED*!!!
    """)


def convert_time_m_s(stop, start):
    minute = int((stop - start) / 60)
    second = int(stop - start) - int((stop - start) / 60) * 60
    return '{}m{}s'.format(minute, second)


def merge_left_only(df1, df2, keys=list()):
    result = pd.merge(
        df1, df2,
        how='outer',
        on=keys,
        indicator=True,
        suffixes=('', '_foo')
    ).query('_merge == "left_only"')[df1.columns.tolist()]
    return result


def get_data_province_mapping_district():
    response = requests.get('https://api.mysupership.vn/v1/partner/areas/province', verify=False).json()

    province_df = pd.DataFrame(data={
        'province_code': [c['code'] for c in response['results']],
        'province': [c['name'] for c in response['results']]
    })

    list_df = []
    for province_code in province_df['province_code'].tolist():
        result = requests.get('https://api.mysupership.vn/v1/partner/areas/district?province={}'.format(province_code),
                              verify=False).json()['results']
        for c in result:
            tmp_df = pd.DataFrame(data={
                'district_code': [c['code']],
                'district': [c['name']],
                'province_code': [province_code]
            })
            list_df.append(tmp_df)
    district_df = pd.concat(list_df, ignore_index=True)

    province_district_df = (
        province_df.merge(
            district_df, on='province_code', how='inner')
            .sort_values(['province_code', 'district_code'])
            .reset_index(drop=True)
    )
    province_district_df.to_parquet(ROOT_PATH + '/input/province_mapping_district.parquet', index=False)


PROVINCE_MAPPING_DISTRICT_DF = pd.read_parquet(ROOT_PATH + '/input/province_mapping_district.parquet')

active_carrier_df = pd.DataFrame(data={'carrier': ACTIVE_CARRIER})
PROVINCE_MAPPING_DISTRICT_CROSS_CARRIER_DF = (
    PROVINCE_MAPPING_DISTRICT_DF[['province', 'district']].rename(columns={
        'province': 'receiver_province',
        'district': 'receiver_district'
    }).merge(active_carrier_df, how='cross')
)

with open(ROOT_PATH + '/input/province_mapping_district_from_api.json') as file:
    PROVINCE_MAPPING_DISTRICT = json.load(file)


# để norm được case dấu đặt khác vị trí => dùng unidecode
# unidecode dùng sau cùng (case tỉnh hà tĩnh)

def preprocess_str(target_str):
    tmp_str = target_str.replace('-', ' ')  # case tỉnh Bà Rịa - Vũng Tàu, Thành phố Phan Rang-Tháp Chàm
    tmp_str = ' '.join(tmp_str.split())  # remove khoảng trống dư giữa các từ
    tmp_str = tmp_str.strip()
    tmp_str = tmp_str.lower()
    # tmp_str = unidecode(tmp_str) # chú ý case tỉnh hà tĩnh, không bỏ dấu được
    return tmp_str


def get_norm_province(province):
    if province is not None:
        short_province = unidecode(
            preprocess_str(province).replace('tỉnh ', '').replace('thành phố ', '').replace('tp ', '').replace('.',
                                                                                                               '').replace(
                ',', ''))
        if short_province == 'ba ria vung tau':
            return 'Tỉnh Bà Rịa - Vũng Tàu'
        for n_province in PROVINCE_MAPPING_DISTRICT.keys():
            if unidecode(n_province.lower()).endswith(unidecode(preprocess_str(province))):
                return n_province
        for n_province in PROVINCE_MAPPING_DISTRICT.keys():
            if unidecode(n_province.lower()).endswith(short_province):
                return n_province
    else:
        return None


def get_norm_district(province, district):
    if district is not None:
        # province đưa vào hàm phải ở dạng chuẩn
        # 1. sử dụng get_norm_province => 2. sử dụng hàm get_norm_district
        short_district = unidecode(
            preprocess_str(district).replace('quận ', '').replace('huyện ', '').replace('thị xã ', '').replace(
                'thành phố ', '').replace('.', '').replace(',', ''))
        if short_district == 'phan rang thap cham':
            return 'Thành phố Phan Rang-Tháp Chàm'
        if province == 'Tỉnh Bình Định' and short_district == 'qui nhon':
            return 'Thành phố Quy Nhơn'
        if province == 'Tỉnh Bình Thuận' and short_district == 'phu quy':
            return 'Huyện Phú Quí'
        if province == 'Tỉnh Kon Tum' and short_district == "ia h'drai":
            return "Huyện Ia H' Drai"
        for n_district in PROVINCE_MAPPING_DISTRICT[province]:
            if unidecode(n_district.lower()).endswith(unidecode(preprocess_str(district))):
                return n_district
        for n_district in PROVINCE_MAPPING_DISTRICT[province]:
            if unidecode(n_district.lower()).endswith(short_district):
                return n_district
    else:
        return None


def normalize_province_district(target_df, tinh_thanh='tinh_thanh', quan_huyen='quan_huyen'):
    # 1. province
    print('Normalizing province...')
    print('Before: ', target_df.shape[0])
    target_df[tinh_thanh] = target_df[tinh_thanh].apply(get_norm_province)
    target_df = target_df[target_df[tinh_thanh].notna()]
    print('After: ', target_df.shape[0])

    # 2. district
    print('Normalizing district...')
    print('Before: ', target_df[target_df[quan_huyen].notna()].shape[0])
    target_df[quan_huyen] = \
        target_df[[tinh_thanh, quan_huyen]] \
            .apply(lambda x: get_norm_district(x[tinh_thanh], x[quan_huyen]), axis=1)
    print('After: ', target_df[target_df[quan_huyen].notna()].shape[0])

    return target_df


def generate_sample_input(n_rows=1000):
    result_df = pd.DataFrame()
    result_df['order_code'] = [
        ''.join(np.random.choice(list('ABCDEFGHIJKLMNOPQRSTUVWXYZ'), 12)) \
        + ''.join(np.random.choice(list('123456789'), 9))
        for i in range(n_rows)
    ]
    result_df['sender_district_code'] = np.random.choice(PROVINCE_MAPPING_DISTRICT_DF['district_code'].tolist(), n_rows)
    result_df['receiver_district_code'] = np.random.choice(PROVINCE_MAPPING_DISTRICT_DF['district_code'].tolist(),
                                                           n_rows)
    result_df = (
        result_df.merge(
            PROVINCE_MAPPING_DISTRICT_DF[['province_code', 'district_code']].rename(columns={
                'province_code': 'sender_province_code',
                'district_code': 'sender_district_code'
            }), on='sender_district_code', how='left')
            .merge(
            PROVINCE_MAPPING_DISTRICT_DF[['province_code', 'district_code']].rename(columns={
                'province_code': 'receiver_province_code',
                'district_code': 'receiver_district_code'
            }), on='receiver_district_code', how='left')
    )
    result_df['weight'] = [
        np.random.choice(list(range(100, 50000, 100)))
        for i in range(n_rows)
    ]

    result_df['delivery_type'] = [
        np.random.choice(['Lấy Tận Nơi', 'Gửi Bưu Cục'])
        for i in range(n_rows)
    ]

    return result_df[[
        'order_code', 'weight', 'delivery_type',
        'sender_province_code', 'sender_district_code', 'receiver_province_code', 'receiver_district_code',
    ]]


def create_type_of_delivery(input_df):

    target_df = input_df.copy()

    phan_vung_nvc = pd.read_parquet(ROOT_PATH + '/processed_data/phan_vung_nvc.parquet')
    phan_vung_nvc = phan_vung_nvc[[
        'carrier_id', 'receiver_province_code', 'receiver_district_code',
        'outer_region_id', 'inner_region_id'
    ]]
    target_df = (
        target_df.merge(
            phan_vung_nvc.rename(columns={
                'receiver_province_code': 'sender_province_code',
                'receiver_district_code': 'sender_district_code',
                'outer_region_id': 'sender_outer_region_id',
                'inner_region_id': 'sender_inner_region_id',
            }), on=['carrier_id', 'sender_province_code', 'sender_district_code'], how='left')
            .merge(
            phan_vung_nvc.rename(columns={
                'outer_region_id': 'receiver_outer_region_id',
                'inner_region_id': 'receiver_inner_region_id',
            }), on=['carrier_id', 'receiver_province_code', 'receiver_district_code'], how='left')
    )

    target_df['order_type_id'] = -1
    target_df.loc[
        (((target_df['sender_province_code'] == '79') & (
            target_df['receiver_province_code'].isin(['01', '48']))) | ((target_df['sender_province_code'] == '01') & (
            target_df['receiver_province_code'].isin(['79', '48']))) | ((target_df['receiver_province_code'] == '79') & (
            target_df['sender_province_code'].isin(['01', '48']))) | ((target_df['receiver_province_code'] == '01') & (
            target_df['sender_province_code'].isin(['79', '48']))))
        & (target_df['order_type_id'] == -1),
        'order_type_id'
    ] = 10

    target_df.loc[
        (((target_df['sender_province_code'] == '79') & (
            target_df['receiver_outer_region_id'].isin([0, 1])))
         | (
                 (target_df['sender_province_code'] == '01') & (target_df['receiver_outer_region_id'].isin([1, 2]))))
        & (target_df['order_type_id'] == -1),
        'order_type_id'
    ] = 9

    target_df.loc[
        (((target_df['sender_outer_region_id'] == 0) & (target_df['receiver_outer_region_id'] == 2))
         | ((target_df['sender_outer_region_id'] == 2) & (target_df['receiver_outer_region_id'] == 0)))
        & (target_df['order_type_id'] == -1),
        'order_type_id'
    ] = 7

    target_df.loc[
        (((target_df['sender_outer_region_id'] == 0) & (target_df['receiver_outer_region_id'] == 1))
         | ((target_df['sender_outer_region_id'] == 1) & (target_df['receiver_outer_region_id'] == 2))
         | ((target_df['sender_outer_region_id'] == 1) & (target_df['receiver_outer_region_id'] == 0))
         | ((target_df['sender_outer_region_id'] == 2) & (target_df['receiver_outer_region_id'] == 1)))
        & (target_df['order_type_id'] == -1),
        'order_type_id'
    ] = 6

    target_df.loc[
        (target_df['sender_province_code'] != target_df['receiver_province_code'])
        & target_df['sender_province_code'].isin(['01', '79'])
        & (target_df['order_type_id'] == -1),
        'order_type_id'
    ] = 8

    target_df.loc[
        (target_df['sender_province_code'] != target_df['receiver_province_code'])
        & (target_df['order_type_id'] == -1),
        'order_type_id'
    ] = 5

    target_df.loc[
        (target_df['receiver_inner_region_id'] == 0)
        & (target_df['receiver_province_code'].isin(['79', '01']))
        & (target_df['order_type_id'] == -1),
        'order_type_id'
    ] = 3

    target_df.loc[
        (target_df['receiver_inner_region_id'] == 0)
        & (~target_df['receiver_province_code'].isin(['79', '01']))
        & (target_df['order_type_id'] == -1),
        'order_type_id'
    ] = 1

    target_df.loc[
        (target_df['receiver_inner_region_id'] == 1)
        & (target_df['receiver_province_code'].isin(['79', '01']))
        & (target_df['order_type_id'] == -1),
        'order_type_id'
    ] = 4

    target_df.loc[
        (target_df['receiver_inner_region_id'] == 1)
        & (~target_df['receiver_province_code'].isin(['79', '01']))
        & (target_df['order_type_id'] == -1),
        'order_type_id'
    ] = 2

    # target_df['sys_order_type_id'] = -1
    # target_df.loc[
    #     (target_df['sender_province_code'].isin(['79', '01'])) \
    #     & (target_df['sender_province_code'] == target_df['receiver_province_code'])
    #     & (target_df['sys_order_type_id'] == -1),
    #     'sys_order_type_id'
    # ] = 1
    # target_df.loc[
    #     (((target_df['sender_province_code'] == '79') & (
    #         target_df['receiver_province_code'].isin(['01', '48'])))
    #      | ((target_df['sender_province_code'] == '01') & (
    #                 target_df['receiver_province_code'].isin(['79', '48'])))
    #      | ((target_df['receiver_province_code'] == '79') & (
    #                 target_df['sender_province_code'].isin(['01', '48'])))
    #      | ((target_df['receiver_province_code'] == '01') & (
    #                 target_df['sender_province_code'].isin(['79', '48']))))
    #     & (target_df['sys_order_type_id'] == -1),
    #     'sys_order_type_id'
    # ] = 2
    # target_df.loc[
    #     (((target_df['sender_province_code'] == '79') & (target_df['receiver_outer_region_id'] == 2)) | ((target_df['sender_province_code'] == '01') & (input_df['receiver_outer_region_id'] == 0)) | ((input_df['receiver_province_code'] == '79') & (input_df['sender_outer_region_id'] == 2)) | ((input_df['receiver_province_code'] == '01') & (input_df['sender_outer_region_id'] == 0)))
    #     & (target_df['sys_order_type_id'] == -1),
    #     'sys_order_type_id'
    # ] = 3
    # target_df.loc[
    #     (((target_df['sender_province_code'] == '79') & (
    #         target_df['receiver_outer_region_id'].isin([0, 1])))
    #      | (
    #              (target_df['sender_province_code'] == '01') & (target_df['receiver_outer_region_id'].isin([1, 2])))
    #      | ((target_df['receiver_province_code'] == '79') & (
    #                 target_df['sender_outer_region_id'].isin([0, 1])))
    #      | (
    #              (target_df['receiver_province_code'] == '01') & (target_df['sender_outer_region_id'].isin([1, 2]))))
    #     & (target_df['sys_order_type_id'] == -1),
    #     'sys_order_type_id'
    # ] = 4
    # target_df.loc[
    #     (target_df['sender_province_code'] == target_df['receiver_province_code'])
    #     & (target_df['sys_order_type_id'] == -1),
    #     'sys_order_type_id'
    # ] = 5
    # target_df.loc[
    #     (target_df['sender_outer_region_id'] == target_df['receiver_outer_region_id'])
    #     & (target_df['sys_order_type_id'] == -1),
    #     'sys_order_type_id'
    # ] = 6
    # target_df.loc[
    #     (((target_df['sender_outer_region_id'] == 0) & (target_df['receiver_outer_region_id'].isin([1, 2])))
    #      | ((target_df['sender_outer_region_id'] == 1) & (target_df['receiver_outer_region_id'].isin([0, 2])))
    #      | ((target_df['sender_outer_region_id'] == 2) & (target_df['receiver_outer_region_id'].isin([0, 1])))
    #      | ((target_df['receiver_outer_region_id'] == 0) & (target_df['sender_outer_region_id'].isin([1, 2])))
    #      | ((target_df['receiver_outer_region_id'] == 1) & (target_df['sender_outer_region_id'].isin([0, 2])))
    #      | ((target_df['receiver_outer_region_id'] == 2) & (target_df['sender_outer_region_id'].isin([0, 1]))))
    #     & (target_df['sys_order_type_id'] == -1),
    #     'sys_order_type_id'
    # ] = 7
    target_df['sys_order_type_id'] = target_df['order_type_id'].map(MAPPING_ORDER_TYPE_ID_ROUTE_TYPE)

    return target_df


def transform_dict(g):
    return pd.Series({
        'ninja_van_stt': dict(zip(g['loai'], g['ninja_van_score'])),
        'ghn_stt': dict(zip(g['loai'], g['ghn_score'])),
        'best_stt': dict(zip(g['loai'], g['best_score'])),
        'shopee_express_stt': dict(zip(g['loai'], g['shopee_express_score'])),
        'ghtk_stt': dict(zip(g['loai'], g['ghtk_score'])),
        'viettel_post_stt': dict(zip(g['loai'], g['viettel_post_score'])),
        'tikinow_stt': dict(zip(g['loai'], g['tikinow_score'])),
    })


QUERY_SQL_COMMAND = """
    -- Create carrier_information CTE
    -- by JOIN tbl_order_type, tbl_data_api, tbl_service_fee, tbl_optimal_score

    WITH carrier_information AS (
        SELECT 
        tbl_ord.carrier_id, tbl_ord.route_type, 
        tbl_fee.price, 
        tbl_api.status::varchar(1) AS status, tbl_api.description, tbl_api.time_data,
        tbl_api.time_display, tbl_api.rate, tbl_api.score, tbl_api.star, 
        tbl_api.for_shop, tbl_api.speed_ranking, tbl_api.score_ranking, tbl_api.rate_ranking, 
        tbl_optimal_score.optimal_score, 
        CAST (DENSE_RANK() OVER (
            ORDER BY tbl_fee.price ASC
        ) AS smallint) AS price_ranking
        FROM db_schema.tbl_order_type tbl_ord
        INNER JOIN (SELECT * FROM db_schema.tbl_data_api WHERE import_date = (SELECT MAX(import_date) FROM db_schema.tbl_data_api)) AS tbl_api
        ON tbl_ord.carrier_id = tbl_api.carrier_id --6
        AND tbl_ord.receiver_province_code = tbl_api.receiver_province_code
        AND tbl_ord.receiver_district_code = tbl_api.receiver_district_code --713
        AND tbl_ord.new_type = tbl_api.new_type --7
        INNER JOIN db_schema.tbl_service_fee tbl_fee
        ON tbl_ord.carrier_id = tbl_fee.carrier_id --6
        AND tbl_ord.new_type = tbl_fee.new_type  --7
        CROSS JOIN (SELECT score AS optimal_score FROM db_schema.tbl_optimal_score WHERE date = (SELECT MAX(date) FROM db_schema.tbl_optimal_score)) AS tbl_optimal_score
        WHERE tbl_ord.sender_province_code = '{}' 
        AND tbl_ord.sender_district_code = '{}'
        AND tbl_ord.receiver_province_code = '{}' 
        AND tbl_ord.receiver_district_code = '{}' 
        AND tbl_fee.weight = CEIL({}/500.0)*500 
        AND tbl_fee.pickup = '{}'
    ),

    -- Create carrier_information_above CTE by 
    -- FILTER carrier_information WHERE score >= optimal_score and
    -- RANKING for_partner by price ASC

    carrier_information_above AS (
        SELECT carrier_id, route_type, price, status, description, time_data, 
        time_display, rate, score, optimal_score, star, for_shop, 
        CAST (DENSE_RANK() OVER (
            ORDER BY price ASC
        ) AS smallint) AS for_partner,
        price_ranking, speed_ranking, score_ranking
        FROM carrier_information
        WHERE score >= optimal_score
    ), 

    -- Create carrier_information_below_tmp CTE by 
    -- FILTER carrier_information WHERE score < optimal_score and
    -- RANKING for_partner by score DESC

    carrier_information_below_tmp1 AS (
        SELECT carrier_id, route_type, price, status, description, time_data, 
        time_display, rate, score, optimal_score, star, for_shop, 
        CAST (DENSE_RANK() OVER (
            ORDER BY score DESC
        ) AS smallint) AS for_partner,
        price_ranking, speed_ranking, score_ranking
        FROM carrier_information
        WHERE score < optimal_score
    ),

    -- Create carrier_information_below CTE by 
    -- ADD for_partner with max_idx_partner in carrier_information_above CTE

    carrier_information_below_tmp2 AS (
        SELECT * FROM carrier_information_below_tmp1
        CROSS JOIN
        -- using COALESCE in case 
        -- n_rows of carrier_information_above == 0 => max_idx_partner is Null
        (SELECT COALESCE(MAX(for_partner), 0) AS max_idx_partner FROM carrier_information_above) AS tbl_max_idx_partner
    ),

    carrier_information_below AS (
        SELECT carrier_id, route_type, price, status, description, time_data, 
        time_display, rate, score, optimal_score, star, for_shop, 
        for_partner + max_idx_partner as for_partner, --ADD for_partner with max_idx_partner
        price_ranking, speed_ranking, score_ranking
        FROM carrier_information_below_tmp2
    ),

    -- Create carrier_information_final CTE by 
    -- UNION carrier_information_above and carrier_information_below

    carrier_information_union AS (
        SELECT * FROM carrier_information_above
        UNION ALL
        SELECT * FROM carrier_information_below
    ),

    -- UPDATE for_fshop EQUAL for_partner
    carrier_information_final AS (
        SELECT carrier_id, route_type, price, status, description, time_data, 
        time_display, rate, score, optimal_score, star, 
        for_partner AS for_shop, -- UPDATE for_fshop = for_partner
        for_partner,
        price_ranking, speed_ranking, score_ranking FROM carrier_information_union
    )

    SELECT * FROM carrier_information_final ORDER BY carrier_id;
"""

QUERY_SQL_COMMAND_OLD = """
    WITH carrier_information AS (
        SELECT 
        tbl_ord.carrier_id, tbl_ord.route_type, 
        tbl_fee.price, 
        tbl_api.status, tbl_api.description, tbl_api.time_data,
        tbl_api.time_display, tbl_api.rate, tbl_api.score, tbl_api.star, 
        tbl_api.for_shop, tbl_api.speed_ranking, tbl_api.score_ranking, tbl_api.rate_ranking, 
        CAST (DENSE_RANK() OVER (
            ORDER BY tbl_fee.price ASC
        ) AS smallint) AS price_ranking
        FROM db_schema.tbl_order_type tbl_ord
        INNER JOIN (SELECT * FROM db_schema.tbl_data_api WHERE import_date = (SELECT MAX(import_date) FROM db_schema.tbl_data_api)) AS tbl_api
        ON tbl_ord.carrier_id = tbl_api.carrier_id --6
        AND tbl_ord.receiver_province_code = tbl_api.receiver_province_code
        AND tbl_ord.receiver_district_code = tbl_api.receiver_district_code --713
        AND tbl_ord.new_type = tbl_api.new_type --7
        INNER JOIN db_schema.tbl_service_fee tbl_fee
        ON tbl_ord.carrier_id = tbl_fee.carrier_id --6
        AND tbl_ord.new_type = tbl_fee.new_type  --7
        WHERE tbl_ord.sender_province_code = '{}' 
        AND tbl_ord.sender_district_code = '{}'
        AND tbl_ord.receiver_province_code = '{}' 
        AND tbl_ord.receiver_district_code = '{}' 
        AND tbl_fee.weight = CEIL({}/500.0)*500 
        AND tbl_fee.pickup = '{}'
    )
    select carrier_id, route_type, price, status::varchar(1) AS status, description, time_data, time_display,
    rate, score, star, for_shop, 
    CAST (DENSE_RANK() OVER (
        ORDER BY
            (1.4 * price_ranking + 1.2 * rate_ranking + score_ranking)
        ASC
    ) AS smallint) AS for_partner,
    price_ranking, speed_ranking, score_ranking
    FROM carrier_information
    ORDER BY carrier_id;
"""