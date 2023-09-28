
import sys
from pathlib import Path
sys.path.append(Path(__file__).parent)

from config import *
from helper import *

def xu_ly_phan_vung_nha_van_chuyen():
    
    # Đọc thông tin raw
    phan_vung_nvc = pd.read_excel(ROOT_PATH + '/raw_data/Bảng Cước Phí - cập nhật 25.07.xlsx', sheet_name='Phân Vùng Ghép SuperShip')
    
    # Tách thông tin các nhà vận chuyển
    phan_vung_nvc = pd.concat([
        phan_vung_nvc.iloc[:, 2:4], 
        phan_vung_nvc.iloc[:, 6], 
        phan_vung_nvc.iloc[:, 7],
        phan_vung_nvc.iloc[:, 9],
        phan_vung_nvc.iloc[:, 11],
        phan_vung_nvc.iloc[:, 13],
    ], axis=1, ignore_index=True)
    
    # Đổi tên cột
    phan_vung_nvc.columns = [
        'tinh_thanh', 'quan_huyen', 'ghn', 'ninja_van', 
        'viettel_post', 'shopee_express', 'tikinow'
    ]
    
    # Transform bảng
    phan_vung_nvc = (
        pd.melt(
            phan_vung_nvc, 
            id_vars =['tinh_thanh', 'quan_huyen'], 
            value_vars =['ghn', 'ninja_van', 'viettel_post', 'shopee_express', 'tikinow'],
            var_name ='nha_van_chuyen', value_name ='loai'
        )
    )
    # Đưa thông tin quận/huyện, tỉnh/thành về dạng chuẩn
    phan_vung_nvc = normalize_province_district(phan_vung_nvc, tinh_thanh='tinh_thanh', quan_huyen='quan_huyen')
    
    # Lưu thông tin
    phan_vung_nvc.to_parquet(ROOT_PATH + '/processed_data/phan_vung_nvc.parquet', index=False)