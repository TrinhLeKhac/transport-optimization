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
import traceback
import warnings

warnings.filterwarnings("ignore")
from config import Settings


def exception_wrapper(func):
    def wrapper(*args, **kwargs):
        result = None  # Initialize result
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            # Extract the line number where the exception occurred
            error_line = traceback.extract_tb(e.__traceback__)[-1].lineno
            error = f"Error in function '{func.__name__}' at line {error_line}: {type(e).__name__} – {str(e)}"
            print(error)
            telegram_bot_send_error_message(error)
        return result

    return wrapper


def telegram_bot_send_success_message():
    telegram_bot_send_message(f"""
        ✅✅✅ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Task run daily *SUCCESSED*!!!
    """)


def telegram_bot_send_error_message(message):
    telegram_bot_send_message(f"""
        ❌❌❌ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Task run daily *FAILED*!!!  
    """)
    telegram_bot_send_message(f"""
        Details of error:  
        {message}
    """)


def telegram_bot_send_message(
        bot_message,
        bot_token=Settings.TELEGRAM_BOT_TOKEN,
        bot_chat_id=Settings.TELEGRAM_CHAT_ID,
):
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chat_id + '&parse_mode=Markdown&text=' + bot_message
    res = requests.get(send_text)
    return res.json()


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


def vietnamese_sort_key(s):
    # Define the Vietnamese alphabet order
    vietnamese_order = 'aăâbcdđeêghiklmnoôơpqrstuưvxyáàảãạắằẳẵặấầẩẫậéèẻẽẹếềểễệíìỉĩịóòỏõọốồổỗộớờởỡợúùủũụứừửữựýỳỷỹỵ'

    # Create a mapping of each character to its order index
    char_order = {char: idx for idx, char in enumerate(vietnamese_order)}

    # Convert the string to lower case and replace characters with their order index
    return [char_order.get(char, len(vietnamese_order)) for char in s.lower()]


try:
    PROVINCE_MAPPING_DISTRICT_DF = pd.read_parquet(ROOT_PATH + '/user_input/province_mapping_district.parquet')
except FileNotFoundError:
    print(
        f"Error: The file {ROOT_PATH}/user_input/province_mapping_district.parquet was not found. Use file {ROOT_PATH}/input/province_mapping_district.parquet instead.")
    PROVINCE_MAPPING_DISTRICT_DF = pd.read_parquet(ROOT_PATH + '/input/province_mapping_district.parquet')

try:
    PROVINCE_MAPPING_DISTRICT_MAPPING_WARD_DF = pd.read_parquet(
        ROOT_PATH + '/user_input/province_mapping_district_mapping_ward.parquet')
except FileNotFoundError:
    print(
        f"Error: The file {ROOT_PATH}/user_input/province_mapping_district_mapping_ward.parquet was not found. Use file {ROOT_PATH}/input/province_mapping_district_mapping_ward.parquet instead.")
    PROVINCE_MAPPING_DISTRICT_MAPPING_WARD_DF = pd.read_parquet(
        ROOT_PATH + '/input/province_mapping_district_mapping_ward.parquet')

active_carrier_df = pd.DataFrame(data={'carrier': ACTIVE_CARRIER})
PROVINCE_MAPPING_DISTRICT_CROSS_CARRIER_DF = (
    PROVINCE_MAPPING_DISTRICT_DF[['province', 'district']].rename(columns={
        'province': 'receiver_province',
        'district': 'receiver_district'
    }).merge(active_carrier_df, how='cross')
)
PROVINCE_MAPPING_DISTRICT_MAPPING_WARD_CROSS_CARRIER_DF = (
    PROVINCE_MAPPING_DISTRICT_MAPPING_WARD_DF[['province', 'district', 'commune']].rename(columns={
        'province': 'receiver_province',
        'district': 'receiver_district',
        'commune': 'receiver_commune',
    }).merge(active_carrier_df, how='cross')
)

try:
    with open(ROOT_PATH + '/user_input/province_mapping_district_from_api.json') as file:
        PROVINCE_MAPPING_DISTRICT = json.load(file)
except FileNotFoundError:
    with open(ROOT_PATH + '/input/province_mapping_district_from_api.json') as file:
        PROVINCE_MAPPING_DISTRICT = json.load(file)

try:
    with open(ROOT_PATH + '/user_input/province_mapping_district_mapping_ward_from_api.json') as file:
        PROVINCE_MAPPING_DISTRICT_MAPPING_WARD = json.load(file)
except FileNotFoundError:
    with open(ROOT_PATH + '/input/province_mapping_district_mapping_ward_from_api.json') as file:
        PROVINCE_MAPPING_DISTRICT_MAPPING_WARD = json.load(file)


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
            preprocess_str(district).replace('quận ', '').replace('huyện ', '').replace('thị xã ', '')
            .replace('thành phố ', '').replace('.', '').replace(',', '')
        )
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


def get_norm_commune(province, district, commune):
    if commune is not None:
        # province, district đưa vào hàm phải ở dạng chuẩn
        # 1. sử dụng get_norm_province => 2. sử dụng hàm get_norm_district => 3. sử dụng hàm get_norm_commune
        short_commune = unidecode(
            preprocess_str(commune).replace('xã ', '').replace('phường ', '').replace('thị trấn ', '').replace('.',
                                                                                                               '').replace(
                ',', '')
        )
        # if short_commune == 'phan rang thap cham':
        #     return 'Thành phố Phan Rang-Tháp Chàm'
        # if province == 'Tỉnh Bình Định' and district == 'Thành phố Quy Nhơn' and short_commune == 'abc':
        #     return 'abc'
        try:
            for n_commune in PROVINCE_MAPPING_DISTRICT_MAPPING_WARD[province][district]:
                if unidecode(n_commune.lower()).endswith(unidecode(preprocess_str(commune))):
                    return n_commune
            for n_commune in PROVINCE_MAPPING_DISTRICT_MAPPING_WARD[province][district]:
                if unidecode(n_commune.lower()).endswith(short_commune):
                    return n_commune
        except:
            return None
    else:
        return None


def normalize_province_district(target_df, tinh_thanh='tinh_thanh', quan_huyen='quan_huyen'):
    # 1. province
    print('Normalizing province...')
    target_df = target_df[target_df[tinh_thanh].notna()]
    print('Before: ', len(target_df))

    target_df[tinh_thanh] = target_df[tinh_thanh].apply(get_norm_province)

    target_df = target_df[target_df[tinh_thanh].notna()]
    print('After: ', len(target_df))

    # 2. district
    print('Normalizing district...')
    print('Before: ', target_df[target_df[quan_huyen].notna()].shape[0])
    target_df[quan_huyen] = \
        target_df[[tinh_thanh, quan_huyen]] \
            .apply(lambda x: get_norm_district(x[tinh_thanh], x[quan_huyen]), axis=1)
    print('After: ', target_df[target_df[quan_huyen].notna()].shape[0])

    return target_df


def normalize_province_district_ward(focus_df, tinh_thanh='tinh_thanh', quan_huyen='quan_huyen', phuong_xa='phuong_xa'):
    target_df = focus_df.copy()
    # Có thể comment toàn bộ dòng filter notna()
    # # để tìm ra tên tỉnh/thành, quận/huyện, phường/xã bị sai

    # 1. province
    print('Normalizing province...')
    target_df = target_df[target_df[tinh_thanh].notna()]
    print('Before: ', len(target_df))

    target_df[tinh_thanh] = target_df[tinh_thanh].apply(get_norm_province)

    target_df = target_df[target_df[tinh_thanh].notna()]
    print('After: ', len(target_df))

    # 2. district
    print('Normalizing district...')
    target_df = target_df[target_df[quan_huyen].notna()]
    print('Before: ', len(target_df))

    target_df[quan_huyen] = \
        target_df[[tinh_thanh, quan_huyen]] \
            .apply(lambda x: get_norm_district(x[tinh_thanh], x[quan_huyen]), axis=1)
    target_df = target_df[target_df[quan_huyen].notna()]
    print('After: ', len(target_df))

    # 3. commune
    print('Normalizing commune...')
    target_df = target_df[target_df[phuong_xa].notna()]
    print('Before: ', len(target_df))

    target_df[phuong_xa] = \
        target_df[[tinh_thanh, quan_huyen, phuong_xa]] \
            .apply(lambda x: get_norm_commune(x[tinh_thanh], x[quan_huyen], x[phuong_xa]), axis=1)

    target_df = target_df[target_df[phuong_xa].notna()]
    print('After: ', len(target_df))

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
            target_df['receiver_province_code'].isin(['79', '48']))) | (
                 (target_df['receiver_province_code'] == '79') & (
             target_df['sender_province_code'].isin(['01', '48']))) | (
                 (target_df['receiver_province_code'] == '01') & (
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

    target_df['order_type'] = target_df['order_type_id'].map(MAPPING_ID_ORDER_TYPE)

    # ------------------------------------- Adhoc order_type ---------------------------------------------------------
    # Khong dung adhoc nay => data giao_dich khong co 'Lien Thanh' => out_data_api giu nguyen shape (713*6*10)
    # target_df.loc[
    #     (target_df['carrier_id'] == 7) &
    #     (
    #             ((target_df['sender_province_code'] == '01') & (
    #                         target_df['receiver_province_code'] == '79')) |
    #             ((target_df['sender_province_code'] == '79') & (
    #                         target_df['receiver_province_code'] == '01'))
    #     ),
    #     'order_type'
    # ] = 'Liên Thành'

    # -------------------------------------- Mapping sys_order_type_id ------------------------------------------------
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


QUERY_SQL_API_BY_DISTRICT = """
    -- Select properties from API data
    
    SELECT receiver_province_code as province_code, receiver_district_code as district_code, 
    carrier_id, route_type, new_type, status, description, time_data, time_display, rate, score,
    star, for_shop, for_shop as for_partner, speed_ranking, score_ranking
    FROM db_schema.tbl_data_api
    WHERE tbl_data_api.receiver_district_code = '{}';
"""

QUERY_SQL_COMMAND_API = """
    -- Create carrier_information CTE
    -- by JOIN tbl_order_type, tbl_data_api, tbl_service_fee, tbl_optimal_score
    
    -- CREATE UNIQUE INDEX tbl_order_type_idx 
    -- ON db_schema.tbl_order_type(carrier_id, sender_province_code, sender_district_code, receiver_province_code, receiver_district_code);
    
    -- CREATE UNIQUE INDEX tbl_data_api_idx 
    -- ON db_schema.tbl_data_api(carrier_id, receiver_province_code, receiver_district_code, new_type);

    -- CREATE UNIQUE INDEX tbl_service_fee_idx 
    -- ON db_schema.tbl_service_fee(carrier_id, order_type, weight, pickup);
    
    -- CREATE UNIQUE INDEX tbl_ngung_giao_nhan_idx 
    -- ON db_schema.tbl_ngung_giao_nhan(carrier_id, sender_province_code, sender_district_code);

    WITH carrier_information_tmp AS ( 
        SELECT 
        tbl_ord.carrier_id, tbl_ord.route_type, 
        tbl_fee.price, 
        -- tbl_ngn.status AS ngn_status, 
        CASE 
            WHEN tbl_ngn.status = 'Quá tải' AND tbl_fee.pickup = '0' 
                THEN 'Bình thường' 
            ELSE tbl_ngn.status
        END AS ngn_status,
        tbl_api.status::varchar(1) AS status, tbl_api.description, tbl_api.time_data, 
        tbl_api.time_display, tbl_api.rate, tbl_api.score, 
        ROUND(tbl_api.score, 1) AS star, -- Nhu cầu business => lấy star bằng cột score
        tbl_api.for_shop, tbl_api.speed_ranking, tbl_api.score_ranking, tbl_api.rate_ranking, 
        tbl_optimal_score.optimal_score 
        FROM db_schema.tbl_order_type tbl_ord 
        INNER JOIN db_schema.tbl_data_api AS tbl_api 
        ON tbl_ord.carrier_id = tbl_api.carrier_id 
        AND tbl_ord.receiver_province_code = tbl_api.receiver_province_code 
        AND tbl_ord.receiver_district_code = tbl_api.receiver_district_code 
        AND tbl_ord.new_type = tbl_api.new_type 
        INNER JOIN db_schema.tbl_service_fee tbl_fee 
        ON tbl_ord.carrier_id = tbl_fee.carrier_id 
        AND tbl_ord.order_type = tbl_fee.order_type 
        INNER JOIN db_schema.tbl_ngung_giao_nhan AS tbl_ngn 
        ON tbl_ord.carrier_id = tbl_ngn.carrier_id 
        AND tbl_ord.sender_province_code = tbl_ngn.sender_province_code 
        AND tbl_ord.sender_district_code = tbl_ngn.sender_district_code 
        CROSS JOIN (
        SELECT score AS optimal_score FROM db_schema.tbl_optimal_score 
        WHERE date = (SELECT MAX(date) FROM db_schema.tbl_optimal_score)
        ) AS tbl_optimal_score 
        WHERE tbl_ord.sender_province_code = '{}' 
        AND tbl_ord.sender_district_code = '{}' 
        AND tbl_ord.receiver_province_code = '{}' 
        AND tbl_ord.receiver_district_code = '{}' 
        AND tbl_fee.weight = CEIL({}/500.0)*500 
        AND tbl_fee.pickup = '{}' 
    ),
    
    carrier_information AS ( 
        SELECT carrier_id, route_type, price, ngn_status, status, 
        CASE
            WHEN ngn_status = 'Quá tải'
                THEN 
                    CASE 
                        WHEN status = '0' THEN 'Quá tải (quận/huyện gửi)'
                        WHEN status = '1' THEN description
                        ELSE 'Quá tải (quận/huyện gửi) + ' || description
                    END
            ELSE description
        END AS description, 
        time_data, 
        time_display, rate, score, star, for_shop, 
        speed_ranking, score_ranking, rate_ranking, optimal_score
        FROM carrier_information_tmp 
    ),
    
    -- Create carrier_information_above CTE by 
    -- FILTER carrier_information WHERE score >= optimal_score and
    -- RANKING for_partner by price ASC
    
    carrier_information_above AS ( 
        SELECT carrier_id, route_type, price, 
        status, description, time_data, 
        time_display, rate, score, star, for_shop, 
        CAST (DENSE_RANK() OVER ( 
            ORDER BY price ASC, score DESC, time_data ASC 
        ) AS smallint) AS for_partner, 
        speed_ranking, score_ranking 
        FROM carrier_information 
        WHERE (score >= optimal_score) AND (status != '1') AND (ngn_status != 'Quá tải') 
    ), 
    
    -- Create carrier_information_below_tmp CTE by 
    -- FILTER carrier_information WHERE score < optimal_score and
    -- RANKING for_partner by score DESC
    
    carrier_information_below_tmp1 AS ( 
        SELECT carrier_id, route_type, price, 
        status, description, time_data, 
        time_display, rate, score, star, for_shop, 
        CAST (DENSE_RANK() OVER ( 
            ORDER BY score DESC, price ASC, time_data ASC 
        ) AS smallint) AS for_partner, 
        speed_ranking, score_ranking 
        FROM carrier_information 
        WHERE (score < optimal_score) AND (status != '1') AND (ngn_status != 'Quá tải') 
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
        SELECT carrier_id, route_type, price, 
        status, description, time_data, 
        time_display, rate, score, star, for_shop, 
        for_partner + max_idx_partner as for_partner, --ADD for_partner with max_idx_partner 
        speed_ranking, score_ranking 
        FROM carrier_information_below_tmp2 
    ),
    
    -- Create carrier_information_final CTE by 
    -- UNION carrier_information_above and carrier_information_below 
    
    carrier_information_union_tmp1 AS ( 
        SELECT * FROM carrier_information_above 
        UNION ALL 
        SELECT * FROM carrier_information_below 
    ),
    
    carrier_information_overload_tmp1 AS ( 
        SELECT carrier_id, route_type, price, 
        status, description, time_data, 
        time_display, rate, score, star, for_shop, 
        CAST (DENSE_RANK() OVER ( 
            ORDER BY score DESC, price ASC, time_data ASC 
        ) AS smallint) AS for_partner, 
        speed_ranking, score_ranking 
        FROM carrier_information 
        WHERE (status = '1') OR (ngn_status = 'Quá tải') 
    ),
    
    carrier_information_overload_tmp2 AS (
        SELECT * FROM carrier_information_overload_tmp1 
        CROSS JOIN 
        (SELECT COALESCE(MAX(for_partner), 0) AS max_idx_partner FROM carrier_information_union_tmp1) AS tbl_max_idx_partner 
    ),
    
    carrier_information_overload AS ( 
        SELECT carrier_id, route_type, price, 
        status, description, time_data, 
        time_display, rate, score, star, for_shop, 
        for_partner + max_idx_partner AS for_partner, --ADD for_partner with max_idx_partner 
        speed_ranking, score_ranking 
        FROM carrier_information_overload_tmp2 
    ),
    
    carrier_information_union AS ( 
        SELECT * FROM carrier_information_union_tmp1 
        UNION ALL 
        SELECT * FROM carrier_information_overload 
    ),
    
    -- UPDATE for_fshop EQUAL for_partner
    carrier_information_final AS ( 
        SELECT carrier_id, route_type, price, 
        status, description, time_data, 
        time_display, rate, score, star, 
        for_partner AS for_shop, -- UPDATE for_shop = for_partner 
        for_partner, 
        CAST (DENSE_RANK() OVER ( 
            ORDER BY price ASC 
        ) AS smallint) AS price_ranking, 
        speed_ranking, score_ranking FROM carrier_information_union 
    )
    
    SELECT * FROM carrier_information_final ORDER BY carrier_id; 
"""

QUERY_SQL_COMMAND_API_SUPER = """
    -- Create carrier_information CTE
    -- by JOIN tbl_order_type, tbl_data_api, tbl_service_fee, tbl_optimal_score

    WITH carrier_information_tmp AS ( 
        SELECT 
        tbl_ord.carrier_id, tbl_ord.route_type, 
        tbl_price.price, 
        -- tbl_ngn.status AS ngn_status, 
        CASE 
            WHEN tbl_ngn.status = 'Quá tải' AND tbl_fee.pickup = '0' 
                THEN 'Bình thường' 
            ELSE tbl_ngn.status
        END AS ngn_status,
        tbl_api.status::varchar(1) AS status, tbl_api.description, tbl_api.time_data, 
        tbl_api.time_display, tbl_api.rate, tbl_api.score, 
        ROUND(tbl_api.score, 1) AS star, -- Nhu cầu business => lấy star bằng cột score
        tbl_api.for_shop, tbl_api.speed_ranking, tbl_api.score_ranking, tbl_api.rate_ranking, 
        tbl_optimal_score.optimal_score 
        FROM db_schema.tbl_order_type tbl_ord 
        INNER JOIN db_schema.tbl_data_api AS tbl_api 
        ON tbl_ord.carrier_id = tbl_api.carrier_id 
        AND tbl_ord.receiver_province_code = tbl_api.receiver_province_code 
        AND tbl_ord.receiver_district_code = tbl_api.receiver_district_code 
        AND tbl_ord.new_type = tbl_api.new_type 
        INNER JOIN db_schema.tbl_service_fee tbl_fee 
        ON tbl_ord.carrier_id = tbl_fee.carrier_id 
        AND tbl_ord.order_type = tbl_fee.order_type
        INNER JOIN db_schema.tbl_ngung_giao_nhan AS tbl_ngn 
        ON tbl_ord.carrier_id = tbl_ngn.carrier_id 
        AND tbl_ord.sender_province_code = tbl_ngn.sender_province_code 
        AND tbl_ord.sender_district_code = tbl_ngn.sender_district_code 
        -- (6, 18000), (7, 17000), (2, 19000), (4, 20000), (10, 15000), (13, 15000), (14, 15000) 
        INNER JOIN (VALUES {}) AS tbl_price(carrier_id, price) 
        ON tbl_ord.carrier_id = tbl_price.carrier_id 
        CROSS JOIN ( 
            SELECT score AS optimal_score FROM db_schema.tbl_optimal_score 
            WHERE date = (SELECT MAX(date) FROM db_schema.tbl_optimal_score) 
        ) AS tbl_optimal_score 
        WHERE tbl_ord.sender_province_code = '{}' 
        AND tbl_ord.sender_district_code = '{}' 
        AND tbl_ord.receiver_province_code = '{}' 
        AND tbl_ord.receiver_district_code = '{}' 
        AND tbl_fee.weight = CEIL({}/500.0)*500 
        AND tbl_fee.pickup = '{}' 
    ),
    
    carrier_information AS ( 
        SELECT carrier_id, route_type, price, ngn_status, status, 
        CASE
            WHEN ngn_status = 'Quá tải'
                THEN 
                    CASE 
                        WHEN status = '0' THEN 'Quá tải (quận/huyện gửi)'
                        WHEN status = '1' THEN description
                        ELSE 'Quá tải (quận/huyện gửi) + ' || description
                    END
            ELSE description
        END AS description, 
        time_data, 
        time_display, rate, score, star, for_shop, 
        speed_ranking, score_ranking, rate_ranking, optimal_score
        FROM carrier_information_tmp 
    ),

    -- Create carrier_information_above CTE by 
    -- FILTER carrier_information WHERE score >= optimal_score and
    -- RANKING for_partner by price ASC

    carrier_information_above AS ( 
        SELECT carrier_id, route_type, price, 
        status, description, time_data, 
        time_display, rate, score, star, for_shop, 
        CAST (DENSE_RANK() OVER ( 
            ORDER BY price ASC, score DESC, time_data ASC 
        ) AS smallint) AS for_partner, 
        speed_ranking, score_ranking 
        FROM carrier_information 
        WHERE (score >= optimal_score) AND (status != '1') AND (ngn_status != 'Quá tải') 
    ), 

    -- Create carrier_information_below_tmp CTE by 
    -- FILTER carrier_information WHERE score < optimal_score and
    -- RANKING for_partner by score DESC

    carrier_information_below_tmp1 AS ( 
        SELECT carrier_id, route_type, price, 
        status, description, time_data, 
        time_display, rate, score, star, for_shop, 
        CAST (DENSE_RANK() OVER ( 
            ORDER BY score DESC, price ASC, time_data ASC 
        ) AS smallint) AS for_partner, 
        speed_ranking, score_ranking 
        FROM carrier_information 
        WHERE (score < optimal_score) AND (status != '1') AND (ngn_status != 'Quá tải') 
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
        SELECT carrier_id, route_type, price, 
        status, description, time_data, 
        time_display, rate, score, star, for_shop, 
        for_partner + max_idx_partner as for_partner, --ADD for_partner with max_idx_partner 
        speed_ranking, score_ranking 
        FROM carrier_information_below_tmp2 
    ),

    -- Create carrier_information_final CTE by 
    -- UNION carrier_information_above and carrier_information_below

    carrier_information_union_tmp1 AS ( 
        SELECT * FROM carrier_information_above 
        UNION ALL 
        SELECT * FROM carrier_information_below 
    ),

    carrier_information_overload_tmp1 AS ( 
        SELECT carrier_id, route_type, price, 
        status, description, time_data, 
        time_display, rate, score, star, for_shop, 
        CAST (DENSE_RANK() OVER ( 
            ORDER BY score DESC, price ASC, time_data ASC 
        ) AS smallint) AS for_partner, 
        speed_ranking, score_ranking 
        FROM carrier_information 
        WHERE (status = '1') OR (ngn_status = 'Quá tải') 
    ),

    carrier_information_overload_tmp2 AS ( 
        SELECT * FROM carrier_information_overload_tmp1 
        CROSS JOIN 
        (SELECT COALESCE(MAX(for_partner), 0) AS max_idx_partner FROM carrier_information_union_tmp1) AS tbl_max_idx_partner 
    ),

    carrier_information_overload AS ( 
        SELECT carrier_id, route_type, price, 
        status, description, time_data, 
        time_display, rate, score, star, for_shop, 
        for_partner + max_idx_partner AS for_partner, --ADD for_partner with max_idx_partner 
        speed_ranking, score_ranking 
        FROM carrier_information_overload_tmp2 
    ),

    carrier_information_union AS ( 
        SELECT * FROM carrier_information_union_tmp1 
        UNION ALL 
        SELECT * FROM carrier_information_overload 
    ),

    -- UPDATE for_fshop EQUAL for_partner 
    carrier_information_final AS ( 
        SELECT carrier_id, route_type, price, 
        status, description, time_data, 
        time_display, rate, score, star, 
        for_partner AS for_shop, -- UPDATE for_shop = for_partner 
        for_partner, 
        CAST (DENSE_RANK() OVER ( 
            ORDER BY price ASC 
        ) AS smallint) AS price_ranking, 
        speed_ranking, score_ranking FROM carrier_information_union 
    )

    SELECT * FROM carrier_information_final ORDER BY carrier_id; 
"""

QUERY_SQL_COMMAND_API_FINAL = """
    WITH carrier_information_tmp1 AS ( 
        SELECT 
        tbl_ord.carrier_id, tbl_ord.route_type, 
        tbl_fee.price, 
        -- tbl_ngn.status AS ngn_status, 
        CASE 
            WHEN tbl_ngn.status = 'Quá tải' AND tbl_fee.pickup = '0' 
                THEN 'Bình thường' 
            ELSE tbl_ngn.status
        END AS ngn_status,
        tbl_api.status::varchar(1) AS status, tbl_api.description, tbl_api.time_data, 
        tbl_api.time_display, tbl_api.rate, tbl_api.score, 
        ROUND(tbl_api.score, 1) AS star, -- Nhu cầu business => lấy star bằng cột score
        tbl_api.for_shop, tbl_api.speed_ranking, tbl_api.score_ranking, tbl_api.rate_ranking, 
        tbl_optimal_score.optimal_score, 
        CAST('{}' AS INTEGER) AS item_price, 
        CAST('{}' AS INTEGER) AS money_get_first, 
        '{}' AS is_returned 
        FROM db_schema.tbl_order_type tbl_ord 
        INNER JOIN db_schema.tbl_data_api AS tbl_api 
        ON tbl_ord.carrier_id = tbl_api.carrier_id 
        AND tbl_ord.receiver_province_code = tbl_api.receiver_province_code 
        AND tbl_ord.receiver_district_code = tbl_api.receiver_district_code 
        AND tbl_ord.new_type = tbl_api.new_type 
        INNER JOIN db_schema.tbl_service_fee tbl_fee 
        ON tbl_ord.carrier_id = tbl_fee.carrier_id 
        AND tbl_ord.order_type = tbl_fee.order_type 
        INNER JOIN db_schema.tbl_ngung_giao_nhan AS tbl_ngn 
        ON tbl_ord.carrier_id = tbl_ngn.carrier_id 
        AND tbl_ord.sender_province_code = tbl_ngn.sender_province_code 
        AND tbl_ord.sender_district_code = tbl_ngn.sender_district_code 
        CROSS JOIN (
        SELECT score AS optimal_score FROM db_schema.tbl_optimal_score 
        WHERE date = (SELECT MAX(date) FROM db_schema.tbl_optimal_score)
        ) AS tbl_optimal_score 
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
    
    carrier_information_tmp2 AS ( 
        SELECT carrier_id, route_type, price, 
        CASE
            WHEN carrier_id = 7 -- Ninja Van
                THEN
                    CASE 
                        WHEN item_price < 1000000 THEN 0
                        WHEN (item_price >= 1000000) AND (item_price < 3000000) THEN 0.005*item_price*(1+0.1)
                        WHEN (item_price >= 3000000) AND (item_price < 10000000) THEN 0.005*item_price*(1+0.1)
                        WHEN (item_price >= 10000000) AND (item_price <= 20000000) THEN 0.005*item_price*(1+0.1)
                        WHEN item_price > 20000000 THEN -1
                    END
            WHEN carrier_id = 6 -- BEST Express
                THEN
                    CASE
                        WHEN item_price <= 1000000 THEN 0
                        WHEN (item_price > 1000000) AND (item_price <= 10000000) THEN 0.005*item_price
                        WHEN item_price > 10000000 THEN 0.01*item_price
                    END
            WHEN carrier_id = 10 --- SPX Express
                THEN
                    CASE
                        WHEN item_price < 1000000 THEN 0
                        WHEN (item_price >= 1000000) AND (item_price < 3000000) THEN 0
                        WHEN (item_price >= 3000000) AND (item_price < 10000000) THEN 0.005*item_price
                        WHEN (item_price >= 10000000) AND (item_price <= 20000000) THEN 0.005*item_price
                        WHEN item_price > 20000000 THEN -1
                    END
            WHEN carrier_id = 2 -- GHN
                THEN
                    CASE
                        WHEN item_price < 1000000 THEN 0
                        WHEN (item_price >= 1000000) AND (item_price < 3000000) THEN 0.005*item_price
                        WHEN (item_price >= 3000000) AND (item_price <= 5000000) THEN 0.005*item_price
                        WHEN item_price > 5000000 THEN -1
                    END
            WHEN carrier_id = 4 -- Viettel Post
                THEN
                    CASE
                        WHEN item_price < 1000000 THEN 0
                        WHEN (item_price >= 1000000) AND (item_price < 3000000) THEN 0.005*item_price
                        WHEN (item_price >= 3000000) AND (item_price < 5000000) THEN 0.005*item_price
                        WHEN (item_price >= 5000000) AND (item_price <= 30000000) THEN 0.005*item_price
                        WHEN item_price > 30000000 THEN -1
                    END
            WHEN carrier_id = 13 -- VnPost
                THEN
                    CASE
                        WHEN item_price < 1000000 THEN 0
                        WHEN (item_price >= 1000000) AND (item_price < 3000000) THEN 0
                        WHEN (item_price >= 3000000) AND (item_price < 10000000) THEN 0.005*item_price
                        WHEN (item_price >= 10000000) AND (item_price <= 20000000) THEN 0.005*item_price
                        WHEN item_price > 20000000 THEN -1
                    END
            WHEN carrier_id = 14 -- Lazada Logistics
                THEN
                    CASE
                        WHEN item_price < 1000000 THEN 0
                        WHEN (item_price >= 1000000) AND (item_price < 3000000) THEN 0
                        WHEN (item_price >= 3000000) AND (item_price < 10000000) THEN 0.005*item_price
                        WHEN (item_price >= 10000000) AND (item_price <= 20000000) THEN 0.005*item_price
                        WHEN item_price > 5000000 THEN -1
                    END
        END AS insurance_fee,
        CASE
            WHEN carrier_id = 7 -- Ninja Van
                THEN
                    CASE 
                        WHEN money_get_first > 20000000 THEN -1
                        ELSE 0
                    END
            WHEN carrier_id = 6 -- BEST Express
                THEN
                    CASE
                        WHEN money_get_first > 5000000 THEN -1
                        ELSE 0
                    END
            WHEN carrier_id = 10 --- SPX Express
                THEN
                    CASE
                        WHEN money_get_first > 20000000 THEN -1
                        ELSE 0
                    END
            WHEN carrier_id = 2 -- GHN
                THEN
                    CASE
                        WHEN money_get_first > 5000000 THEN -1
                        ELSE 0
                    END
            WHEN carrier_id = 4 -- Viettel Post
                THEN
                    CASE
                        WHEN money_get_first < 1000000 THEN 0
                        WHEN (money_get_first >= 1000000) AND (money_get_first < 3000000) THEN 0
                        WHEN (money_get_first >= 3000000) AND (money_get_first < 10000000) THEN 0.005*(money_get_first - 3000000)
                        WHEN (money_get_first >= 10000000) AND (money_get_first <= 100000000) THEN 0.005*(money_get_first - 3000000)
                        WHEN money_get_first > 100000000 THEN -1
                    END
            WHEN carrier_id = 13 -- VNPost
                THEN
                    CASE
                        WHEN money_get_first > 20000000 THEN -1
                        ELSE 0
                    END
            WHEN carrier_id = 14 -- Lazada Logistics
                THEN
                    CASE
                        WHEN money_get_first > 20000000 THEN -1
                        ELSE 0
                    END
        END AS collection_fee,
        CASE
            WHEN carrier_id = 7 -- Ninja Van
                THEN
                    CASE 
                        WHEN is_returned = 'Có' THEN price
                        ELSE 0
                    END
            WHEN carrier_id = 6 -- BEST Express
                THEN
                    CASE
                        WHEN is_returned = 'Có' THEN price
                        ELSE 0
                    END
            WHEN carrier_id = 10 --- SPX Express
                THEN
                    CASE
                        WHEN is_returned = 'Có' THEN price
                        ELSE 0
                    END
            WHEN carrier_id = 2 THEN 0  -- GHN
            WHEN carrier_id = 4 -- Viettel Post
                THEN
                    CASE
                        WHEN is_returned = 'Có' THEN price
                        ELSE 0
                    END
            WHEN carrier_id = 13 -- VnPost
                THEN
                    CASE
                        WHEN is_returned = 'Có' THEN price
                        ELSE 0
                    END
            WHEN carrier_id = 14 -- Lazada Logistics
                THEN
                    CASE
                        WHEN is_returned = 'Có' THEN price
                        ELSE 0
                    END
        END AS redeem_fee, 
        status, ngn_status, 
        CASE
            WHEN ngn_status = 'Quá tải'
                THEN 
                    CASE 
                        WHEN status = '0' THEN 'Quá tải (quận/huyện gửi)'
                        WHEN status = '1' THEN description
                        ELSE 'Quá tải (quận/huyện gửi) + ' || description
                    END
            ELSE description
        END AS description,
        time_data, time_display, rate, score, optimal_score, star, for_shop, 
        speed_ranking, score_ranking 
        FROM carrier_information_tmp1 
    ), 
    
    carrier_information_tmp3 AS ( 
        SELECT carrier_id, route_type, price, insurance_fee, collection_fee, redeem_fee, 
        CASE WHEN insurance_fee != -1 THEN insurance_fee ELSE 0 END AS insurance_fee_modified, 
        CASE WHEN collection_fee != -1 THEN collection_fee ELSE 0 END AS collection_fee_modified, 
        status, ngn_status, description, time_data, 
        time_display, rate, score, optimal_score, star, for_shop, 
        speed_ranking, score_ranking 
        FROM carrier_information_tmp2 
    ), 
    
    carrier_information AS ( 
        SELECT carrier_id, route_type, insurance_fee, collection_fee, 
        price + insurance_fee_modified + collection_fee_modified + redeem_fee AS total_price, 
        status, ngn_status, description, time_data, 
        time_display, rate, score, optimal_score, star, for_shop, 
        speed_ranking, score_ranking 
        FROM carrier_information_tmp3 
    ), 
    
    carrier_information_above AS ( 
        SELECT carrier_id, route_type, total_price, 
        status, description, time_data, 
        time_display, rate, score, star, for_shop, 
        CAST (DENSE_RANK() OVER ( 
            ORDER BY total_price ASC, score DESC, time_data ASC 
        ) AS smallint) AS for_partner, 
        speed_ranking, score_ranking 
        FROM carrier_information 
        WHERE 
            (score >= optimal_score) 
            AND (insurance_fee != -1) 
            AND (collection_fee != -1) 
            AND (status != '1') 
            AND (ngn_status != 'Quá tải') 
    ), 
    
    -- Create carrier_information_below_tmp CTE by 
    -- FILTER carrier_information WHERE score < optimal_score and
    -- RANKING for_partner by score DESC
    
    carrier_information_below_tmp1 AS ( 
        SELECT carrier_id, route_type, total_price, 
        status, description, time_data, 
        time_display, rate, score, star, for_shop, 
        CAST (DENSE_RANK() OVER ( 
            ORDER BY score DESC, total_price ASC, time_data ASC 
        ) AS smallint) AS for_partner, 
        speed_ranking, score_ranking 
        FROM carrier_information 
        WHERE 
            (score < optimal_score) 
            AND (insurance_fee != -1) 
            AND (collection_fee != -1) 
            AND (status != '1')
            AND (ngn_status != 'Quá tải')
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
        SELECT carrier_id, route_type, total_price, 
        status, description, time_data, 
        time_display, rate, score, star, for_shop, 
        for_partner + max_idx_partner AS for_partner, --ADD for_partner with max_idx_partner 
        speed_ranking, score_ranking 
        FROM carrier_information_below_tmp2 
    ),
    
    -- Create carrier_information_final CTE by 
    -- UNION carrier_information_above and carrier_information_below
    
    carrier_information_union_tmp1 AS ( 
        SELECT * FROM carrier_information_above 
        UNION ALL 
        SELECT * FROM carrier_information_below 
    ),
    
    carrier_information_overload_tmp1 AS ( 
        SELECT carrier_id, route_type, total_price, 
        status, description, time_data, 
        time_display, rate, score, star, for_shop, 
        CAST (DENSE_RANK() OVER ( 
            ORDER BY score DESC, total_price ASC, time_data ASC 
        ) AS smallint) AS for_partner, 
        speed_ranking, score_ranking 
        FROM carrier_information 
        WHERE (status = '1') OR (ngn_status = 'Quá tải') 
    ),
    
    carrier_information_overload_tmp2 AS ( 
        SELECT * FROM carrier_information_overload_tmp1 
        CROSS JOIN 
        (SELECT COALESCE(MAX(for_partner), 0) AS max_idx_partner FROM carrier_information_union_tmp1) AS tbl_max_idx_partner 
    ),
    
    carrier_information_overload AS ( 
        SELECT carrier_id, route_type, total_price, 
        status, description, time_data, 
        time_display, rate, score, star, for_shop, 
        for_partner + max_idx_partner AS for_partner, --ADD for_partner with max_idx_partner 
        speed_ranking, score_ranking 
        FROM carrier_information_overload_tmp2 
    ),
    
    carrier_information_union_tmp2 AS ( 
        SELECT * FROM carrier_information_union_tmp1 
        UNION ALL 
        SELECT * FROM carrier_information_overload 
    ),
    
    carrier_information_refuse_tmp1 AS ( 
        SELECT carrier_id, route_type, total_price, 
        status, description, time_data, 
        time_display, rate, score, star, for_shop, 
        CAST (DENSE_RANK() OVER ( 
            ORDER BY score DESC, total_price ASC, time_data ASC 
        ) AS smallint) AS for_partner, 
        speed_ranking, score_ranking 
        FROM carrier_information 
        WHERE 
            ((insurance_fee = -1) OR (collection_fee = -1))
            AND (status != '1') 
            AND (ngn_status != 'Quá tải')
    ),
    
    carrier_information_refuse_tmp2 AS ( 
        SELECT * FROM carrier_information_refuse_tmp1 
        CROSS JOIN 
        (SELECT COALESCE(MAX(for_partner), 0) AS max_idx_partner FROM carrier_information_union_tmp2) AS tbl_max_idx_partner 
    ),
    
    carrier_information_refuse AS ( 
        SELECT carrier_id, route_type, total_price, 
        status, description, time_data, 
        time_display, rate, score, star, for_shop, 
        for_partner + max_idx_partner AS for_partner, --ADD for_partner with max_idx_partner 
        speed_ranking, score_ranking 
        FROM carrier_information_refuse_tmp2 
    ),
    
    carrier_information_union AS ( 
        SELECT * FROM carrier_information_union_tmp2 
        UNION ALL 
        SELECT * FROM carrier_information_refuse 
    ),
    
        -- UPDATE for_fshop EQUAL for_partner
    carrier_information_final AS ( 
        SELECT carrier_id, route_type, CAST (total_price AS int) AS price, 
        status, description, time_data, 
        time_display, rate, score, star, 
        for_partner AS for_shop, -- UPDATE for_shop = for_partner 
        for_partner, 
        CAST (DENSE_RANK() OVER ( 
            ORDER BY total_price ASC 
        ) AS smallint) AS price_ranking, 
        speed_ranking, score_ranking FROM carrier_information_union 
    )
    
    SELECT * FROM carrier_information_final ORDER BY carrier_id; 
"""

QUERY_SQL_COMMAND_STREAMLIT = """
    -- Create carrier_information CTE
    -- by JOIN tbl_order_type, tbl_data_api, tbl_service_fee, tbl_optimal_score
    
    WITH carrier_information_tmp1 AS ( 
        SELECT 
        tbl_ord.carrier_id, tbl_ord.new_type, 
        tbl_fee.price, 
        -- tbl_ngn.status AS ngn_status, 
        CASE 
            WHEN tbl_ngn.status = 'Quá tải' AND tbl_fee.pickup = '0' 
                THEN 'Bình thường' 
            ELSE tbl_ngn.status
        END AS ngn_status,
        tbl_api.status::varchar(1) AS status, tbl_api.description, tbl_api.time_data, 
        tbl_api.time_display, tbl_api.rate, tbl_api.score, 
        ROUND(tbl_api.star, 1) AS star,
        tbl_api.for_shop, tbl_api.speed_ranking, tbl_api.score_ranking, tbl_api.rate_ranking, 
        tbl_optimal_score.optimal_score, 
        CAST('{}' AS INTEGER) AS item_price, 
        CAST('{}' AS INTEGER) AS money_get_first, 
        '{}' AS is_returned 
        FROM db_schema.tbl_order_type tbl_ord 
        INNER JOIN db_schema.tbl_data_api AS tbl_api 
        ON tbl_ord.carrier_id = tbl_api.carrier_id 
        AND tbl_ord.receiver_province_code = tbl_api.receiver_province_code 
        AND tbl_ord.receiver_district_code = tbl_api.receiver_district_code 
        AND tbl_ord.new_type = tbl_api.new_type 
        INNER JOIN db_schema.tbl_service_fee tbl_fee 
        ON tbl_ord.carrier_id = tbl_fee.carrier_id 
        AND tbl_ord.order_type = tbl_fee.order_type 
        INNER JOIN db_schema.tbl_ngung_giao_nhan AS tbl_ngn 
        ON tbl_ord.carrier_id = tbl_ngn.carrier_id 
        AND tbl_ord.sender_province_code = tbl_ngn.sender_province_code 
        AND tbl_ord.sender_district_code = tbl_ngn.sender_district_code 
        CROSS JOIN (
        SELECT score AS optimal_score FROM db_schema.tbl_optimal_score 
        WHERE date = (SELECT MAX(date) FROM db_schema.tbl_optimal_score)
        ) AS tbl_optimal_score 
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
    
    carrier_information_tmp2 AS (
        SELECT carrier_id, new_type, price, 
        CASE
            WHEN carrier_id = 7 -- Ninja Van
                THEN
                    CASE 
                        WHEN item_price < 1000000 THEN 0
                        WHEN (item_price >= 1000000) AND (item_price < 3000000) THEN 0.005*item_price*(1+0.1)
                        WHEN (item_price >= 3000000) AND (item_price < 10000000) THEN 0.005*item_price*(1+0.1)
                        WHEN (item_price >= 10000000) AND (item_price <= 20000000) THEN 0.005*item_price*(1+0.1)
                        WHEN item_price > 20000000 THEN -1
                    END
            WHEN carrier_id = 6 -- BEST Express
                THEN
                    CASE
                        WHEN item_price <= 1000000 THEN 0
                        WHEN (item_price > 1000000) AND (item_price <= 10000000) THEN 0.005*item_price
                        WHEN item_price > 10000000 THEN 0.01*item_price
                    END
            WHEN carrier_id = 10 --- SPX Express
                THEN
                    CASE
                        WHEN item_price < 1000000 THEN 0
                        WHEN (item_price >= 1000000) AND (item_price < 3000000) THEN 0
                        WHEN (item_price >= 3000000) AND (item_price < 10000000) THEN 0.005*item_price
                        WHEN (item_price >= 10000000) AND (item_price <= 20000000) THEN 0.005*item_price
                        WHEN item_price > 20000000 THEN -1
                    END
            WHEN carrier_id = 2 -- GHN
                THEN
                    CASE
                        WHEN item_price < 1000000 THEN 0
                        WHEN (item_price >= 1000000) AND (item_price < 3000000) THEN 0.005*item_price
                        WHEN (item_price >= 3000000) AND (item_price <= 5000000) THEN 0.005*item_price
                        WHEN item_price > 5000000 THEN -1
                    END
            WHEN carrier_id = 4 -- Viettel Post
                THEN
                    CASE
                        WHEN item_price < 1000000 THEN 0
                        WHEN (item_price >= 1000000) AND (item_price < 3000000) THEN 0.005*item_price
                        WHEN (item_price >= 3000000) AND (item_price < 5000000) THEN 0.005*item_price
                        WHEN (item_price >= 5000000) AND (item_price <= 30000000) THEN 0.005*item_price
                        WHEN item_price > 30000000 THEN -1
                    END
            WHEN carrier_id = 13 -- VnPost
                THEN
                    CASE
                        WHEN item_price < 1000000 THEN 0
                        WHEN (item_price >= 1000000) AND (item_price < 3000000) THEN 0
                        WHEN (item_price >= 3000000) AND (item_price < 10000000) THEN 0.005*item_price
                        WHEN (item_price >= 10000000) AND (item_price <= 20000000) THEN 0.005*item_price
                        WHEN item_price > 20000000 THEN -1
                    END
            WHEN carrier_id = 14 -- Lazada Logistics
                THEN
                    CASE
                        WHEN item_price < 1000000 THEN 0
                        WHEN (item_price >= 1000000) AND (item_price < 3000000) THEN 0
                        WHEN (item_price >= 3000000) AND (item_price < 10000000) THEN 0.005*item_price
                        WHEN (item_price >= 10000000) AND (item_price <= 20000000) THEN 0.005*item_price
                        WHEN item_price > 5000000 THEN -1
                    END
        END AS insurance_fee,
        CASE
            WHEN carrier_id = 7 -- Ninja Van
                THEN
                    CASE 
                        WHEN money_get_first > 20000000 THEN -1
                        ELSE 0
                    END
            WHEN carrier_id = 6 -- BEST Express
                THEN
                    CASE
                        WHEN money_get_first > 5000000 THEN -1
                        ELSE 0
                    END
            WHEN carrier_id = 10 --- SPX Express
                THEN
                    CASE
                        WHEN money_get_first > 20000000 THEN -1
                        ELSE 0
                    END
            WHEN carrier_id = 2 -- GHN
                THEN
                    CASE
                        WHEN money_get_first > 5000000 THEN -1
                        ELSE 0
                    END
            WHEN carrier_id = 4 -- Viettel Post
                THEN
                    CASE
                        WHEN money_get_first < 1000000 THEN 0
                        WHEN (money_get_first >= 1000000) AND (money_get_first < 3000000) THEN 0
                        WHEN (money_get_first >= 3000000) AND (money_get_first < 10000000) THEN 0.005*(money_get_first - 3000000)
                        WHEN (money_get_first >= 10000000) AND (money_get_first <= 100000000) THEN 0.005*(money_get_first - 3000000)
                        WHEN money_get_first > 100000000 THEN -1
                    END
            WHEN carrier_id = 13 -- VNPost
                THEN
                    CASE
                        WHEN money_get_first > 20000000 THEN -1
                        ELSE 0
                    END
            WHEN carrier_id = 14 -- Lazada Logistics
                THEN
                    CASE
                        WHEN money_get_first > 20000000 THEN -1
                        ELSE 0
                    END
        END AS collection_fee,
        CASE
            WHEN carrier_id = 7 -- Ninja Van
                THEN
                    CASE 
                        WHEN is_returned = 'Có' THEN price
                        ELSE 0
                    END
            WHEN carrier_id = 6 -- BEST Express
                THEN
                    CASE
                        WHEN is_returned = 'Có' THEN price
                        ELSE 0
                    END
            WHEN carrier_id = 10 --- SPX Express
                THEN
                    CASE
                        WHEN is_returned = 'Có' THEN price
                        ELSE 0
                    END
            WHEN carrier_id = 2 THEN 0  -- GHN
            WHEN carrier_id = 4 -- Viettel Post
                THEN
                    CASE
                        WHEN is_returned = 'Có' THEN price
                        ELSE 0
                    END
            WHEN carrier_id = 13 -- VnPost
                THEN
                    CASE
                        WHEN is_returned = 'Có' THEN price
                        ELSE 0
                    END
            WHEN carrier_id = 14 -- Lazada Logistics
                THEN
                    CASE
                        WHEN is_returned = 'Có' THEN price
                        ELSE 0
                    END
        END AS redeem_fee, 
        status, ngn_status, 
        CASE
            WHEN ngn_status = 'Quá tải'
                THEN 
                    CASE 
                        WHEN status = '0' THEN 'Quá tải (quận/huyện gửi)'
                        WHEN status = '1' THEN description
                        ELSE 'Quá tải (quận/huyện gửi) + ' || description
                    END
            ELSE description
        END AS description, 
        time_data, time_display, rate, score, optimal_score, star, for_shop, 
        speed_ranking, score_ranking 
        FROM carrier_information_tmp1 
    ), 
    
    carrier_information_tmp3 AS ( 
        SELECT carrier_id, new_type, price, insurance_fee, collection_fee, redeem_fee, 
        CASE WHEN insurance_fee != -1 THEN insurance_fee ELSE 0 END AS insurance_fee_modified, 
        CASE WHEN collection_fee != -1 THEN collection_fee ELSE 0 END AS collection_fee_modified, 
        status, ngn_status, description, time_data, 
        time_display, rate, score, optimal_score, star, for_shop, 
        speed_ranking, score_ranking 
        FROM carrier_information_tmp2 
    ), 
    
    carrier_information AS ( 
        SELECT carrier_id, new_type, price, insurance_fee, collection_fee, redeem_fee, 
        price + insurance_fee_modified + collection_fee_modified + redeem_fee AS total_price, 
        status, ngn_status, description, time_data, 
        time_display, rate, score, optimal_score, star, for_shop, 
        speed_ranking, score_ranking 
        FROM carrier_information_tmp3 
    ), 

    carrier_information_above AS (
        SELECT carrier_id, new_type, price, insurance_fee, collection_fee, redeem_fee, total_price, 
        status, description, time_data, 
        time_display, rate, score, optimal_score, star, for_shop, 
        CAST (DENSE_RANK() OVER ( 
            ORDER BY total_price ASC, score DESC, time_data ASC 
        ) AS smallint) AS for_partner, 
        speed_ranking, score_ranking 
        FROM carrier_information 
        WHERE 
            (score >= optimal_score) 
            AND (insurance_fee != -1) 
            AND (collection_fee != -1) 
            AND (status != '1') 
            AND (ngn_status != 'Quá tải')
    ), 

    -- Create carrier_information_below_tmp CTE by 
    -- FILTER carrier_information WHERE score < optimal_score and
    -- RANKING for_partner by score DESC
    
    carrier_information_below_tmp1 AS ( 
        SELECT carrier_id, new_type, price, insurance_fee, collection_fee, redeem_fee, total_price, 
        status, description, time_data, 
        time_display, rate, score, optimal_score, star, for_shop, 
        CAST (DENSE_RANK() OVER ( 
            ORDER BY score DESC, total_price ASC, time_data ASC 
        ) AS smallint) AS for_partner, 
        speed_ranking, score_ranking 
        FROM carrier_information 
        WHERE 
            (score < optimal_score) 
            AND (insurance_fee != -1) 
            AND (collection_fee != -1) 
            AND (status != '1')
            AND (ngn_status != 'Quá tải')
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
        SELECT carrier_id, new_type, price, insurance_fee, collection_fee, redeem_fee, total_price, 
        status, description, time_data, 
        time_display, rate, score, optimal_score, star, for_shop, 
        for_partner + max_idx_partner AS for_partner, --ADD for_partner with max_idx_partner 
        speed_ranking, score_ranking 
        FROM carrier_information_below_tmp2 
    ),

    -- Create carrier_information_final CTE by 
    -- UNION carrier_information_above and carrier_information_below

    carrier_information_union_tmp1 AS ( 
        SELECT * FROM carrier_information_above 
        UNION ALL 
        SELECT * FROM carrier_information_below 
    ),
    
    carrier_information_overload_tmp1 AS ( 
        SELECT carrier_id, new_type, price, insurance_fee, collection_fee, redeem_fee, total_price, 
        status, description, time_data, 
        time_display, rate, score, optimal_score, star, for_shop, 
        CAST (DENSE_RANK() OVER ( 
            ORDER BY score DESC, total_price ASC, time_data ASC 
        ) AS smallint) AS for_partner, 
        speed_ranking, score_ranking 
        FROM carrier_information 
        WHERE (status = '1') OR (ngn_status = 'Quá tải') 
    ),
    
    carrier_information_overload_tmp2 AS ( 
        SELECT * FROM carrier_information_overload_tmp1 
        CROSS JOIN 
        (SELECT COALESCE(MAX(for_partner), 0) AS max_idx_partner FROM carrier_information_union_tmp1) AS tbl_max_idx_partner 
    ),

    carrier_information_overload AS ( 
        SELECT carrier_id, new_type, price, insurance_fee, collection_fee, redeem_fee, total_price, 
        status, description, time_data, 
        time_display, rate, score, optimal_score, star, for_shop, 
        for_partner + max_idx_partner AS for_partner, --ADD for_partner with max_idx_partner 
        speed_ranking, score_ranking 
        FROM carrier_information_overload_tmp2 
    ),
    
    carrier_information_union_tmp2 AS ( 
        SELECT * FROM carrier_information_union_tmp1 
        UNION ALL 
        SELECT * FROM carrier_information_overload 
    ),
    
    carrier_information_refuse_tmp1 AS ( 
        SELECT carrier_id, new_type, price, insurance_fee, collection_fee, redeem_fee, total_price, 
        status, description, time_data, 
        time_display, rate, score, optimal_score, star, for_shop, 
        CAST (DENSE_RANK() OVER ( 
            ORDER BY score DESC, total_price ASC, time_data ASC 
        ) AS smallint) AS for_partner, 
        speed_ranking, score_ranking 
        FROM carrier_information 
        WHERE 
            ((insurance_fee = -1) OR (collection_fee = -1)) 
            AND (status != '1') 
            AND (ngn_status != 'Quá tải')
    ),
    
    carrier_information_refuse_tmp2 AS ( 
        SELECT * FROM carrier_information_refuse_tmp1 
        CROSS JOIN 
        (SELECT COALESCE(MAX(for_partner), 0) AS max_idx_partner FROM carrier_information_union_tmp2) AS tbl_max_idx_partner 
    ),

    carrier_information_refuse AS ( 
        SELECT carrier_id, new_type, price, insurance_fee, collection_fee, redeem_fee, total_price, 
        status, description, time_data, 
        time_display, rate, score, optimal_score, star, for_shop, 
        for_partner + max_idx_partner AS for_partner, --ADD for_partner with max_idx_partner 
        speed_ranking, score_ranking 
        FROM carrier_information_refuse_tmp2 
    ),
    
    carrier_information_union AS ( 
        SELECT * FROM carrier_information_union_tmp2 
        UNION ALL 
        SELECT * FROM carrier_information_refuse 
    ),

    -- UPDATE for_fshop EQUAL for_partner
    carrier_information_final AS ( 
        SELECT carrier_id, new_type, price, insurance_fee, collection_fee, redeem_fee, total_price, 
        status, description, time_data, 
        time_display, rate, score, optimal_score, star, 
        for_partner AS for_shop, -- UPDATE for_shop = for_partner 
        for_partner, 
        CAST (DENSE_RANK() OVER ( 
            ORDER BY total_price ASC 
        ) AS smallint) AS price_ranking, 
        speed_ranking, score_ranking FROM carrier_information_union 
    )

    SELECT * FROM carrier_information_final ORDER BY carrier_id; 
"""
