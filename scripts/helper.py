import numpy as np
import pandas as pd
from datetime import datetime
import requests
import json
from unidecode import unidecode
from functools import reduce

from config import ROOT_PATH

# để norm được case dấu đặt khác vị trí => dùng unidecode
# unidecode dùng sau cùng (case tỉnh hà tĩnh)

def merge_left_only(df1, df2, keys=list()):
    result = pd.merge(
        df1, df2,
        how='outer', 
        on=keys, 
        indicator=True, 
        suffixes=('','_foo')
    ).query('_merge == "left_only"')[df1.columns.tolist()]
    return result
    
with open(ROOT_PATH + '/processed_data/province_mapping_district_from_api.json') as file:
    PROVINCE_MAPPING_DISTRICT = json.load(file)
    
def preprocess_str(target_str):
    tmp_str = target_str.replace('-', ' ') # case tỉnh Bà Rịa - Vũng Tàu, Thành phố Phan Rang-Tháp Chàm
    tmp_str = ' '.join(tmp_str.split()) # remove khoảng trống dư giữa các từ
    tmp_str = tmp_str.strip()
    tmp_str = tmp_str.lower()
    # tmp_str = unidecode(tmp_str) # chú ý case tỉnh hà tĩnh, không bỏ dấu được
    return tmp_str

def get_norm_province(province):
    if province is not None:
        short_province = unidecode(preprocess_str(province).replace('tỉnh ', '').replace('thành phố ', '').replace('tp ', '').replace('.', '').replace(',', ''))
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
        short_district = unidecode(preprocess_str(district).replace('quận ', '').replace('huyện ', '').replace('thị xã ', '').replace('thành phố ', '').replace('.', '').replace(',', ''))
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
    target_df[[tinh_thanh, quan_huyen]]\
    .apply(lambda x: get_norm_district(x[tinh_thanh], x[quan_huyen]), axis=1)
    print('After: ', target_df[target_df[quan_huyen].notna()].shape[0])
    
    return target_df

def get_latest_province_district():
    response = requests.get('https://api.mysupership.vn/v1/partner/areas/province', verify=False).json()
    api_response = [(c['code'], c['name']) for c in response['results']]
    list_province = []
    list_district = []
    for province_code, province in api_response:
        result = requests.get('https://api.mysupership.vn/v1/partner/areas/district?province={}'.format(province_code), verify=False).json()['results']
        for row in result:
            list_province.append(province)
            list_district.append(row['name'])
    province_district_norm_df = pd.DataFrame(data={
        'tinh_thanh': list_province,
        'quan_huyen': list_district
    })

    return province_district_norm_df
    
def status_chat_luong_noi_bo_ninja_van(series):
    if series['pct'] == 0:
        return 'Không có thông tin'
    elif (series['pct'] >= 0.95) & series['more_than_100']:
        return 'Ti lệ trên 95% và tổng số đơn giao hàng trên 100 đơn'
    elif (series['pct'] >= 0.9) & (series['pct'] < 0.95) & series['more_than_100']:
        return 'Ti lệ trên 90% và tổng số đơn giao hàng trên 100 đơn'
    elif (series['pct'] < 0.9) & series['more_than_100']:
        return 'Ti lệ dưới 90% và tổng số đơn giao hàng trên 100 đơn'
    elif (series['pct'] >= 0.95) & (~series['more_than_100']):
        return 'Ti lệ trên 95% và tổng số đơn giao hàng dưới 100 đơn'
    elif (series['pct'] >= 0.9) & (series['pct'] < 0.95) & (~series['more_than_100']):
        return 'Ti lệ trên 90% và tổng số đơn giao hàng dưới 100 đơn'
    elif (series['pct'] < 0.9) & (~series['more_than_100']):
        return 'Ti lệ dưới 90% và tổng số đơn giao hàng dưới 100 đơn'

def status_kho_giao_nhan(so_buu_cuc, so_buu_cuc_trong_tinh, so_quan_huyen):
    if so_buu_cuc == 0:
        if so_buu_cuc_trong_tinh == 0:
            return 'Không có bưu cục trong tỉnh'
        elif so_buu_cuc_trong_tinh/so_quan_huyen > 0.8:
            return 'Trong tỉnh có trên 80% bưu cục/tổng quận huyện của tỉnh'
        elif so_buu_cuc_trong_tinh/so_quan_huyen > 0.5:
            return 'Trong tỉnh có trên 50% bưu cục/tổng quận huyện của tỉnh'
        elif so_buu_cuc_trong_tinh/so_quan_huyen > 0.3:
            return 'Trong tỉnh có trên 30% bưu cục/tổng quận huyện của tỉnh'
        elif so_buu_cuc_trong_tinh/so_quan_huyen <= 0.3:
            return 'Trong tỉnh có bé hơn hoặc bằng 30% bưu cục/tổng quận huyện của tỉnh'
            
    if so_buu_cuc >= 3:
        return 'Có từ 3 bưu cục cùng cấp quận/huyện trở lên'
    elif so_buu_cuc == 2:
        return 'Có 2 bưu cục cùng cấp quận/huyện trở lên'
    elif so_buu_cuc == 1:
        return 'Có bưu cục cùng cấp quận/huyện'

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
    
def score_thoi_gian_giao_hang(tong_don, thoi_gian_giao_tb, loai_van_chuyen):
    if tong_don == -1:
        return 'Không có thông tin'
    # group 1 (cận miền)
    if loai_van_chuyen == 'Cận Miền':
        # thời gian giao trung bình < 72h
        if (tong_don > 20) and (thoi_gian_giao_tb < 72):
            return 'Trung bình dưới 72h và tổng số đơn giao hàng lớn hơn 20 đơn'
        elif (tong_don > 10) and (thoi_gian_giao_tb < 72):
            return 'Trung bình dưới 72h và tổng số đơn giao hàng lớn hơn 10 đơn'
        elif (tong_don > 5) and (thoi_gian_giao_tb < 72):
            return 'Trung bình dưới 72h và tổng số đơn giao hàng lớn hơn 5 đơn'
        elif (tong_don <= 5) and (thoi_gian_giao_tb < 72):
            return 'Trung bình dưới 72h và tổng số đơn giao hàng bé hơn hoặc bằng 5 đơn'
        # thời gian giao trung bình < 96h
        elif (tong_don > 30) and (thoi_gian_giao_tb < 96):
            return 'Trung bình dưới 96h và tổng số đơn giao hàng lớn hơn 30 đơn'
        elif (tong_don > 20) and (thoi_gian_giao_tb < 96):
            return 'Trung bình dưới 96h và tổng số đơn giao hàng lớn hơn 20 đơn'
        elif (tong_don > 10) and (thoi_gian_giao_tb < 96):
            return 'Trung bình dưới 96h và tổng số đơn giao hàng lớn hơn 10 đơn'
        elif (tong_don > 5) and (thoi_gian_giao_tb < 96):
            return 'Trung bình dưới 96h và tổng số đơn giao hàng lớn hơn 5 đơn'
        elif (tong_don <= 5) and (thoi_gian_giao_tb < 96):
            return 'Trung bình dưới 96h và tổng số đơn giao hàng bé hơn hoặc bằng 5 đơn'
        # trễ
        elif (tong_don > 3) and (thoi_gian_giao_tb < 120):
            return 'Trung bình dưới 120h và tổng số đơn giao hàng lớn hơn 3 đơn'
        elif (tong_don <= 3) and (thoi_gian_giao_tb < 120):
            return 'Trung bình dưới 120h và tổng số đơn giao hàng bé hơn hoặc bằng 3 đơn'
        elif (tong_don > 3) and (thoi_gian_giao_tb < 144):
            return 'Trung bình dưới 144h và tổng số đơn giao hàng lớn hơn 3 đơn'
        elif (tong_don <= 3) and (thoi_gian_giao_tb < 144):
            return 'Trung bình dưới 144h và tổng số đơn giao hàng bé hơn hoặc bằng 3 đơn'
        elif thoi_gian_giao_tb >= 144:
            return 'Trung bình thời gian giao hàng lớn hơn hoặc bằng 144h'
            
    # group 2 (nội miền)
    if loai_van_chuyen == 'Nội Miền':
        # thời gian giao trung bình < 48h
        if (tong_don > 20) and (thoi_gian_giao_tb < 48):
            return 'Trung bình dưới 48h và tổng số đơn giao hàng lớn hơn 20 đơn'
        elif (tong_don > 10) and (thoi_gian_giao_tb < 48):
            return 'Trung bình dưới 48h và tổng số đơn giao hàng lớn hơn 10 đơn'
        elif (tong_don > 5) and (thoi_gian_giao_tb < 48):
            return 'Trung bình dưới 48h và tổng số đơn giao hàng lớn hơn 5 đơn'
        elif (tong_don <= 5) and (thoi_gian_giao_tb < 48):
            return 'Trung bình dưới 48h và tổng số đơn giao hàng bé hơn hoặc bằng 5 đơn'
        # thời gian giao trung bình < 72h
        elif (tong_don > 30) and (thoi_gian_giao_tb < 72):
            return 'Trung bình dưới 72h và tổng số đơn giao hàng lớn hơn 30 đơn'
        elif (tong_don > 20) and (thoi_gian_giao_tb < 72):
            return 'Trung bình dưới 72h và tổng số đơn giao hàng lớn hơn 20 đơn'
        elif (tong_don > 10) and (thoi_gian_giao_tb < 72):
            return 'Trung bình dưới 72h và tổng số đơn giao hàng lớn hơn 10 đơn'
        elif (tong_don > 5) and (thoi_gian_giao_tb < 72):
            return 'Trung bình dưới 72h và tổng số đơn giao hàng lớn hơn 5 đơn'
        elif (tong_don <= 5) and (thoi_gian_giao_tb < 72):
            return 'Trung bình dưới 72h và tổng số đơn giao hàng bé hơn hoặc bằng 5 đơn'
        # trễ
        elif (tong_don > 3) and (thoi_gian_giao_tb < 96):
            return 'Trung bình dưới 96h và tổng số đơn giao hàng lớn hơn 3 đơn'
        elif (tong_don <= 3) and (thoi_gian_giao_tb < 96):
            return 'Trung bình dưới 96h và tổng số đơn giao hàng bé hơn hoặc bằng 3 đơn'
        elif (tong_don > 3) and (thoi_gian_giao_tb < 120):
            return 'Trung bình dưới 120h và tổng số đơn giao hàng lớn hơn 3 đơn'
        elif (tong_don <= 3) and (thoi_gian_giao_tb < 120):
            return 'Trung bình dưới 120h và tổng số đơn giao hàng bé hơn hoặc bằng 3 đơn'
        elif thoi_gian_giao_tb >= 120:
            return 'Trung bình thời gian giao hàng lớn hơn hoặc bằng 120h'
            
    # group 3 (nội tỉnh)
    if loai_van_chuyen in ['Nội Thành Tỉnh', 'Ngoại Thành Tỉnh']:
        # thời gian giao trung bình < 48h
        if (tong_don > 30) and (thoi_gian_giao_tb < 48):
            return 'Trung bình dưới 48h và tổng số đơn giao hàng lớn hơn 30 đơn'
        elif (tong_don > 20) and (thoi_gian_giao_tb < 48):
            return 'Trung bình dưới 48h và tổng số đơn giao hàng lớn hơn 20 đơn'
        elif (tong_don > 10) and (thoi_gian_giao_tb < 48):
            return 'Trung bình dưới 48h và tổng số đơn giao hàng lớn hơn 10 đơn'
        elif (tong_don > 5) and (thoi_gian_giao_tb < 48):
            return 'Trung bình dưới 48h và tổng số đơn giao hàng lớn hơn 5 đơn'
        elif (tong_don <= 5) and (thoi_gian_giao_tb < 48):
            return 'Trung bình dưới 48h và tổng số đơn giao hàng bé hơn hoặc bằng 5 đơn'
        # thời gian giao trung bình < 72h
        elif (tong_don > 30) and (thoi_gian_giao_tb < 72):
            return 'Trung bình dưới 72h và tổng số đơn giao hàng lớn hơn 30 đơn'
        elif (tong_don > 20) and (thoi_gian_giao_tb < 72):
            return 'Trung bình dưới 72h và tổng số đơn giao hàng lớn hơn 20 đơn'
        elif (tong_don > 10) and (thoi_gian_giao_tb < 72):
            return 'Trung bình dưới 72h và tổng số đơn giao hàng lớn hơn 10 đơn'
        elif (tong_don > 5) and (thoi_gian_giao_tb < 72):
            return 'Trung bình dưới 72h và tổng số đơn giao hàng lớn hơn 5 đơn'
        elif (tong_don <= 5) and (thoi_gian_giao_tb < 72):
            return 'Trung bình dưới 72h và tổng số đơn giao hàng bé hơn hoặc bằng 5 đơn'
        # trễ
        elif (tong_don > 3) and (thoi_gian_giao_tb < 96):
            return 'Trung bình dưới 96h và tổng số đơn giao hàng lớn hơn 3 đơn'
        elif (tong_don <= 3) and (thoi_gian_giao_tb < 96):
            return 'Trung bình dưới 96h và tổng số đơn giao hàng bé hơn hoặc bằng 3 đơn'
        elif thoi_gian_giao_tb >= 96:
            return 'Trung bình thời gian giao hàng lớn hơn hoặc bằng 96h'

def score_ti_le_giao_hang(tong_don, ti_le_thanh_cong):
    # group 1
    if (tong_don >= 30) and (ti_le_thanh_cong >0.95):
        return 'Tổng đơn hàng từ 30 đơn trở lên và có tỷ lệ giao hàng thành công trên 95%'
    elif (tong_don >= 20) and (ti_le_thanh_cong >0.95):
        return 'Tổng đơn hàng từ 20 đơn trở lên và có tỷ lệ giao hàng thành công trên 95%'
    elif (tong_don >= 10) and (ti_le_thanh_cong >0.95):
        return 'Tổng đơn hàng từ 10 đơn trở lên và có tỷ lệ giao hàng thành công trên 95%'
    # group 2
    elif (tong_don >= 30) and (ti_le_thanh_cong >0.9):
        return 'Tổng đơn hàng từ 30 đơn trở lên và có tỷ lệ giao hàng thành công trên 90%'
    elif (tong_don >= 20) and (ti_le_thanh_cong >0.9):
        return 'Tổng đơn hàng từ 20 đơn trở lên và có tỷ lệ giao hàng thành công trên 90%'
    elif (tong_don >= 10) and (ti_le_thanh_cong >0.9):
        return 'Tổng đơn hàng từ 10 đơn trở lên và có tỷ lệ giao hàng thành công trên 90%'
    # group 3
    elif (tong_don >= 5) and (ti_le_thanh_cong >0.95):
        return 'Tổng đơn hàng từ 5 đơn trở lên và có tỷ lệ giao hàng thành công trên 95%'
    elif (tong_don >= 5) and (ti_le_thanh_cong >0.9):
        return 'Tổng đơn hàng từ 5 đơn trở lên và có tỷ lệ giao hàng thành công trên 90%'
    elif (tong_don >= 5) and (ti_le_thanh_cong >0.85):
        return 'Tổng đơn hàng từ 5 đơn trở lên và có tỷ lệ giao hàng thành công trên 85%'
    elif (tong_don >= 5) and (ti_le_thanh_cong >0.75):
        return 'Tổng đơn hàng từ 5 đơn trở lên và có tỷ lệ giao hàng thành công trên 75%'
    elif (tong_don >= 5) and (ti_le_thanh_cong >0.5):
        return 'Tổng đơn hàng từ 5 đơn trở lên và có tỷ lệ giao hàng thành công trên 50%'
    elif ti_le_thanh_cong == -1:
        return 'Tổng đơn hàng từ 10 đơn trở lên và có tỷ lệ hoàn từ 25% trở lên'
    elif ti_le_thanh_cong == -2:
        return 'Tổng đơn hàng từ 4 đơn trở lên và có tỷ lệ hoàn từ 50% trở lên'
    elif ti_le_thanh_cong == -3:
        return 'TOP 10 KHU VỰC có số lượng đơn hàng từ 3 đơn trở lên và có tỷ lệ hoàn hơn 20%'
    elif ti_le_thanh_cong == -4:
        return 'Không có thông tin'
    else:
        return 'Trường hợp khác'

