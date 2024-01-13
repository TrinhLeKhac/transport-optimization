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


def type_of_delivery(s):

    if ((s['sender_province'] == 'Thành phố Hồ Chí Minh') & (
            s['receiver_province'] in ['Thành phố Hà Nội', 'Thành phố Đà Nẵng'])) \
            | ((s['sender_province'] == 'Thành phố Hà Nội') & (
            s['receiver_province'] in ['Thành phố Hồ Chí Minh', 'Thành phố Đà Nẵng'])) \
            | ((s['receiver_province'] == 'Thành phố Hồ Chí Minh') & (
            s['sender_province'] in ['Thành phố Hà Nội', 'Thành phố Đà Nẵng'])) \
            | ((s['receiver_province'] == 'Thành phố Hà Nội') & (
            s['sender_province'] in ['Thành phố Hồ Chí Minh', 'Thành phố Đà Nẵng'])):
        return 'Liên Miền Đặc Biệt'

    elif ((s['sender_province'] == 'Thành phố Hồ Chí Minh') & (
            s['receiver_outer_region'] in ['Miền Bắc', 'Miền Trung'])) \
            | (
            (s['sender_province'] == 'Thành phố Hà Nội') & (s['receiver_outer_region'] in ['Miền Trung', 'Miền Nam'])):
        return 'Liên Miền Tp.HCM - HN'

    elif ((s['sender_outer_region'] == 'Miền Bắc') & (s['receiver_outer_region'] == 'Miền Nam')) \
            | ((s['sender_outer_region'] == 'Miền Nam') & (s['receiver_outer_region'] == 'Miền Bắc')):
        return 'Cách Miền'

    elif ((s['sender_outer_region'] == 'Miền Bắc') & (s['receiver_outer_region'] == 'Miền Trung')) \
            | ((s['sender_outer_region'] == 'Miền Trung') & (s['receiver_outer_region'] == 'Miền Nam')) \
            | ((s['sender_outer_region'] == 'Miền Trung') & (s['receiver_outer_region'] == 'Miền Bắc')) \
            | ((s['sender_outer_region'] == 'Miền Nam') & (s['receiver_outer_region'] == 'Miền Trung')):
        return 'Cận Miền'

    elif ((s['sender_province'] != s['receiver_province'])
          & (s['sender_province'] in ['Thành phố Hồ Chí Minh', 'Thành phố Hà Nội'])):
        return 'Nội Miền Tp.HCM - HN'

    elif s['sender_province'] != s['receiver_province']:
        return 'Nội Miền'

    elif (s['receiver_inner_region'] == 'Nội Thành') \
            & (s['receiver_province'] in ['Thành phố Hồ Chí Minh', 'Thành phố Hà Nội']):
        return 'Nội Thành Tp.HCM - HN'

    elif (s['receiver_inner_region'] == 'Nội Thành') \
            & (s['receiver_province'] not in ['Thành phố Hồ Chí Minh', 'Thành phố Hà Nội']):
        return 'Nội Thành Tỉnh'

    elif (s['receiver_inner_region'] == 'Ngoại Thành') \
            & (s['receiver_province'] in ['Thành phố Hồ Chí Minh', 'Thành phố Hà Nội']):
        return 'Ngoại Thành Tp.HCM - HN'

    elif (s['receiver_inner_region'] == 'Ngoại Thành') \
            & (s['receiver_province'] not in ['Thành phố Hồ Chí Minh', 'Thành phố Hà Nội']):
        return 'Ngoại Thành Tỉnh'


def type_of_system_delivery(s):

    if (s['sender_province'] in ['Thành phố Hồ Chí Minh', 'Thành phố Hà Nội']) \
            & (s['sender_province'] == s['receiver_province']):
        return 1

    elif ((s['sender_province'] == 'Thành phố Hồ Chí Minh') & (
            s['receiver_province'] in ['Thành phố Hà Nội', 'Thành phố Đà Nẵng'])) \
            | ((s['sender_province'] == 'Thành phố Hà Nội') & (
            s['receiver_province'] in ['Thành phố Hồ Chí Minh', 'Thành phố Đà Nẵng'])) \
            | ((s['receiver_province'] == 'Thành phố Hồ Chí Minh') & (
            s['sender_province'] in ['Thành phố Hà Nội', 'Thành phố Đà Nẵng'])) \
            | ((s['receiver_province'] == 'Thành phố Hà Nội') & (
            s['sender_province'] in ['Thành phố Hồ Chí Minh', 'Thành phố Đà Nẵng'])):
        return 2

    elif ((s['sender_province'] == 'Thành phố Hồ Chí Minh') & (s['receiver_outer_region'] == 'Miền Nam')) \
            | ((s['sender_province'] == 'Thành phố Hà Nội') & (s['receiver_outer_region'] == 'Miền Bắc')) \
            | ((s['receiver_province'] == 'Thành phố Hồ Chí Minh') & (s['sender_outer_region'] == 'Miền Nam')) \
            | ((s['receiver_province'] == 'Thành phố Hà Nội') & (s['sender_outer_region'] == 'Miền Bắc')):
        return 3

    elif ((s['sender_province'] == 'Thành phố Hồ Chí Minh') & (
            s['receiver_outer_region'] in ['Miền Bắc', 'Miền Trung'])) \
            | (
            (s['sender_province'] == 'Thành phố Hà Nội') & (s['receiver_outer_region'] in ['Miền Trung', 'Miền Nam'])) \
            | ((s['receiver_province'] == 'Thành phố Hồ Chí Minh') & (
            s['sender_outer_region'] in ['Miền Bắc', 'Miền Trung'])) \
            | (
            (s['receiver_province'] == 'Thành phố Hà Nội') & (s['sender_outer_region'] in ['Miền Trung', 'Miền Nam'])):
        return 4

    elif s['sender_province'] == s['receiver_province']:
        return 5

    elif s['sender_outer_region'] == s['receiver_outer_region']:
        return 6

    elif ((s['sender_outer_region'] == 'Miền Bắc') & (s['receiver_outer_region'] in ['Miền Trung', 'Miền Nam'])) \
            | ((s['sender_outer_region'] == 'Miền Trung') & (s['receiver_outer_region'] in ['Miền Bắc', 'Miền Nam'])) \
            | ((s['sender_outer_region'] == 'Miền Nam') & (s['receiver_outer_region'] in ['Miền Bắc', 'Miền Trung'])) \
            | ((s['receiver_outer_region'] == 'Miền Bắc') & (s['sender_outer_region'] in ['Miền Trung', 'Miền Nam'])) \
            | ((s['receiver_outer_region'] == 'Miền Trung') & (s['sender_outer_region'] in ['Miền Bắc', 'Miền Nam'])) \
            | ((s['receiver_outer_region'] == 'Miền Nam') & (s['sender_outer_region'] in ['Miền Bắc', 'Miền Trung'])):
        return 7


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


def calculate_monetary(id_nvc, khoi_luong, loai_van_chuyen):
    cuoc_phi_nvc = pd.read_parquet(ROOT_PATH + '/processed_data/cuoc_phi_nvc.parquet')
    cuoc_phi_nvc = (
        pd.melt(
            cuoc_phi_nvc,
            id_vars=['nha_van_chuyen', 'gt', 'lt_or_eq'],
            value_vars=[
                'noi_thanh_tinh', 'ngoai_thanh_tinh',
                'noi_thanh_tphcm_hn', 'ngoai_thanh_tphcm_hn',
                'noi_mien', 'can_mien', 'cach_mien'
            ],
            var_name='loai', value_name='cuoc_phi'
        )
    )
    cuoc_phi_nvc['id_nvc'] = cuoc_phi_nvc['nha_van_chuyen'].map(MAPPING_ID_NVC)
    cuoc_phi_nvc = cuoc_phi_nvc.loc[
        cuoc_phi_nvc['loai'].isin(['noi_thanh_tinh', 'ngoai_thanh_tinh', 'noi_mien', 'can_mien'])]
    cuoc_phi_nvc['loai'] = cuoc_phi_nvc['loai'].map({
        'noi_thanh_tinh': 'Nội Thành Tỉnh',
        'ngoai_thanh_tinh': 'Ngoại Thành Tỉnh',
        'noi_mien': 'Nội Miền',
        'can_mien': 'Cận Miền',
    })
    cuoc_phi = cuoc_phi_nvc.loc[
        (cuoc_phi_nvc['id_nvc'] == id_nvc) &
        (cuoc_phi_nvc['loai'] == loai_van_chuyen) &
        (cuoc_phi_nvc['lt_or_eq'] >= khoi_luong) &
        (cuoc_phi_nvc['gt'] < khoi_luong)
        ]['cuoc_phi'].values[0]
    return cuoc_phi


def _calculate_output_api(df_api, ma_don_hang, tinh_thanh, quan_huyen, id_nvc, loai_van_chuyen, khoi_luong):
    result = df_api.loc[
        (df_api['tinh_thanh'] == tinh_thanh)
        & (df_api['quan_huyen'] == quan_huyen)
        & (df_api['id_nvc'] == id_nvc)
        & (df_api['loai'] == loai_van_chuyen)
        ]
    if len(result) > 0:
        status = result['status'].values[0]  # lấy từ quá khứ
        estimate_delivery_time = result['estimate_delivery_time'].values[0]  # lấy từ quá khứ
        score = result['score'].values[0]  # lấy từ quá khứ
        stars = result['stars'].values[0]  # lấy từ quá khứ
        monetary = calculate_monetary(id_nvc, khoi_luong, loai_van_chuyen)  # tính tiền từ khối lượng đơn hiện tại
        # notification = result['notification'].values[0] # tính lại ở khâu sau

        return_df = pd.DataFrame(data={
            'ma_don_hang': [ma_don_hang],
            'id_nvc': [id_nvc],
            'status': [status],
            'monetary': [monetary],
            'estimate_delivery_time': [estimate_delivery_time],
            'score': [score],
            'stars': [stars],
            # 'notification': [notification],
        })
        return_df['nvc'] = return_df['id_nvc'].map({
            7: 'Ninja Van',
            2: 'Giao Hàng Nhanh',
            6: 'Best',
            10: 'Shopee Express',
            1: 'Giao Hàng Tiết Kiệm',
            4: 'Viettel Post',
            12: 'Tiki Now',
        })
        return_df = return_df[['ma_don_hang', 'id_nvc', 'nvc', 'status', 'monetary',
                               'estimate_delivery_time', 'score', 'stars']]
    else:
        return_df = pd.DataFrame(columns=['ma_don_hang', 'id_nvc', 'nvc', 'status', 'monetary',
                                          'estimate_delivery_time', 'score', 'stars'])
    return return_df


def calculate_output_api(df_api, ma_don_hang, tinh_thanh, quan_huyen, ids_nvc, loai_van_chuyen, khoi_luong):
    all_res = []
    for id_nvc in ids_nvc:
        tmp_df = _calculate_output_api(df_api, ma_don_hang, tinh_thanh, quan_huyen, id_nvc, loai_van_chuyen, khoi_luong)
        all_res.append(tmp_df)
    total_df = pd.concat(all_res, ignore_index=True)

    return total_df


def calculate_notification(data_df):
    data_df['notification'] = ''

    re_nhat_df = data_df.loc[data_df['monetary'] == data_df['monetary'].min()]
    re_nhat_df['notification'] = 'Rẻ nhất'

    remain_df1 = merge_left_only(data_df, re_nhat_df, keys=['monetary'])
    if len(remain_df1) == 0:
        return re_nhat_df
    else:
        nhanh_nhat_df = remain_df1.loc[
            remain_df1['estimate_delivery_time'].str[0].astype(int) ==
            remain_df1['estimate_delivery_time'].str[0].astype(int).min()
            ]
        nhanh_nhat_df['notification'] = 'Nhanh nhất'
        remain_df2 = merge_left_only(remain_df1, nhanh_nhat_df, keys=['estimate_delivery_time'])
        if len(remain_df2) == 0:
            return pd.concat([re_nhat_df, nhanh_nhat_df])
        else:
            hieu_qua_nhat_df = remain_df2.loc[
                remain_df2['score'] == remain_df2['score'].max()]
            hieu_qua_nhat_df['notification'] = 'Hiệu quả nhất'
            remain_df3 = merge_left_only(remain_df2, hieu_qua_nhat_df, keys=['score'])
            if len(remain_df3) == 0:
                return pd.concat([re_nhat_df, nhanh_nhat_df, hieu_qua_nhat_df])
            else:
                remain_df3['notification'] = 'Bình thường'
                return pd.concat([re_nhat_df, nhanh_nhat_df, hieu_qua_nhat_df, remain_df3])
