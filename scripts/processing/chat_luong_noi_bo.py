
import sys
from pathlib import Path
sys.path.append(Path(__file__).parent)

from config import *
from helper import *

MAPPING_PROVINCE_BEST = {
    'Bình Dương': ['Bình Dương-North', 'Bình Dương-South'],
    'Bình Phước': ['Bình Phước-East', 'Bình Phước-West'],
    'Quảng Ninh': ['Quảng Ninh-East', 'Quảng Ninh-West'],
    'Đắk Lắk': ['Đắk Lắk-North', 'Đắk Lắk-South'],
    'Đồng Nai': ['Đồng Nai-North', 'Đồng Nai-South'],
    'Bà Rịa - Vũng Tàu': ['Bà Rịa Vũng Tàu'],
}
MAPPING_PROVINCE_DISTRICT_BEST = {
    'Hà Nội': [
        'Ba Vì', 'Hoài Đức', 'Đông Anh', 'Thường Tín', 
        'Thanh Oai', 'Bắc Từ Liêm', 'Thanh Xuân', 
        'Hà Đông', 'Hoàng Mai',
    ],
    'Hồ Chí Minh': [
        'Bình Thạnh', 'Quận 7', 'Quận 8', 'Củ Chi', 
        'Phú Nhuận', 'Thủ Đức', 'Bình Tân',
    ],
    'Thanh Hóa': ['Lam Sơn'],
    'Nghệ An': ['Thành Phố Vinh', 'Thái Hòa'],
}

def mapping_province_best(s):
    for province in MAPPING_PROVINCE_BEST.keys():
        if s in MAPPING_PROVINCE_BEST[province]:
            return province
        
def mapping_province_district_best(s):
    for province in MAPPING_PROVINCE_DISTRICT_BEST.keys():
        if s in MAPPING_PROVINCE_DISTRICT_BEST[province]:
            return province, s
    else:
        return None, None

def get_pct_ninja_van(s):
    if '<=' in s:
        return int(s.split('<=')[1].split('%')[0])/100
    elif '-' in s:
        first =  int(s.split('-')[0].strip().split('%')[0])
        second = int(s.split('-')[1].strip().split('%')[0])
        return (first + second)/2.0/100
    else:
        return 0 # không có thông tin return 0
        
def xu_ly_chat_luong_noi_bo_ninja_van():

    # Đọc data raw
    clnb_njv_df = pd.read_excel(ROOT_PATH + '/raw_data/Cap nhat Nin 15.07.xlsx', sheet_name='QUẬN HUYỆN (all Retail)')

    # Chọn cột phù hợp và đổi tên
    clnb_njv_df = clnb_njv_df[1:]
    clnb_njv_df.columns = [
        'mien', 'tinh_thanh', 'ma_quan_huyen', 'quan_huyen',
        'ten_ngan', 'buu_cục', 'pct', 'more_than_100'
    ]
    
    # Xử lý data
    clnb_njv_df.loc[clnb_njv_df['more_than_100'].isna(), 'more_than_100'] = False
    clnb_njv_df['more_than_100'] = clnb_njv_df['more_than_100'].astype(bool)
    clnb_njv_df = clnb_njv_df.drop(['ma_quan_huyen', 'ten_ngan'], axis=1)

    # Tách percentage
    clnb_njv_df['pct'] = clnb_njv_df['pct'].astype(str).apply(get_pct_ninja_van)

    # Chuẩn hóa tên quận/huyện, tỉnh/thành
    clnb_njv_df = normalize_province_district(clnb_njv_df, tinh_thanh='tinh_thanh', quan_huyen='quan_huyen')
    clnb_njv_df = clnb_njv_df.loc[clnb_njv_df['tinh_thanh'].notna() & clnb_njv_df['quan_huyen'].notna()]
    
    # Lưu thông tin
    clnb_njv_df.to_parquet(ROOT_PATH + '/processed_data/chat_luong_noi_bo_njv_all.parquet', index=False)

def xu_ly_chat_luong_noi_bo_best():

    # Đọc thông tin raw
    clnb_best_df = pd.read_excel(ROOT_PATH + '/raw_data/CHẤT LƯỢNG KHÂU CUỐI THÁNG 07.xlsx')

    # Chọn thông tin và đổi tên cột
    clnb_best_df = clnb_best_df[3:]
    clnb_best_df.columns = [
        'khu_vuc_lon', 'khu_vuc_nho', 'tong_don_giao', 'ty_le_nhap_kho_dung_han', 
        'ty_le_trien_khai_giao_hang', 'ty_le_kien_co_van_de', 'ty_le_ky_nhan_ca_dau',
        'ty_le_ky_nhan', 'backlog_cuoi_ngay'
    ]

    # Xử lý data
    clnb_best_df['khu_vuc_nho'] = clnb_best_df['khu_vuc_nho'].str.title()
    clnb_best_df['tinh_thanh'] = clnb_best_df['khu_vuc_nho'].map(mapping_province_best).fillna(clnb_best_df['khu_vuc_nho'])
    clnb_best_df['tinh_thanh'] = clnb_best_df['tinh_thanh'].apply(get_norm_province).fillna(clnb_best_df['tinh_thanh'])
    clnb_best_df[['tinh_thanh_noi_suy', 'quan_huyen']] = (
        clnb_best_df.apply(lambda s: mapping_province_district_best(s['tinh_thanh']), axis=1, result_type="expand")
    )
    clnb_best_df.loc[clnb_best_df['quan_huyen'].notna(), 'tinh_thanh'] = clnb_best_df['tinh_thanh_noi_suy']
    clnb_best_df.drop('tinh_thanh_noi_suy', axis=1, inplace=True)

    # Chuẩn hóa tên quận/huyện, tỉnh/thành
    clnb_best_df = normalize_province_district(clnb_best_df, tinh_thanh='tinh_thanh', quan_huyen='quan_huyen')

    # Lưu thông tin
    clnb_best_df.to_parquet(ROOT_PATH + '/processed_data/chat_luong_noi_bo_best_all.parquet', index=False)
    