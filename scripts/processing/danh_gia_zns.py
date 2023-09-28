
import sys
from pathlib import Path
sys.path.append(Path(__file__).parent)

from config import *
from helper import *

def xu_ly_danh_gia_zns():
    
    # Đọc thông tin raw
    danh_gia_zns = pd.read_excel(ROOT_PATH + '/raw_data/DANH SÁCH ZNS 1-14.07.2023.xlsx', sheet_name='THÔNG TIN')
    
    # Thay đổi icon ở file excel
    danh_gia_zns.loc[danh_gia_zns['Chuyển Ngoài'] == '✅', 'Chuyển Ngoài'] = True
    danh_gia_zns['Chuyển Ngoài'] = danh_gia_zns['Chuyển Ngoài'].fillna(False)
    danh_gia_zns.drop(['TT', 'Thông Tin Lỗi'], axis=1, inplace=True)

    # Đổi tên cột
    danh_gia_zns.columns=[
        'kho_lay_hang', 'tinh_thanh_lay_hang', 'thoi_gian_lay_hang', 'ma_don_hang', 'nha_van_chuyen', 'trang_thai',
        'kho_giao_hang', 'tinh_thanh_giao_hang', 'quan_huyen_giao_hang', 'chuyen_ngoai', 'so_tin_gui', 
        'danh_gia', 'so_sao', 'nhan_xet', 'danh_gia_luc'
    ]

    # Chuẩn hóa tên quận/huyện, tỉnh/thành
    danh_gia_zns = normalize_province_district(danh_gia_zns, tinh_thanh='tinh_thanh_giao_hang', quan_huyen='quan_huyen_giao_hang')

    # Lưu thông tin
    danh_gia_zns.to_parquet(ROOT_PATH + '/processed_data/danh_gia_zns.parquet', index=False)
    