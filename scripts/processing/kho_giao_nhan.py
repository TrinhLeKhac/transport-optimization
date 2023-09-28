
import sys
from pathlib import Path
sys.path.append(Path(__file__).parent)

from config import *
from helper import *

def xu_ly_kho_giao_nhan():

    # Đọc thông tin bưu cục best
    print('NINJA VAN...')
    buu_cuc_njv_df = pd.read_excel(ROOT_PATH + '/raw_data/Cap nhat Nin 15.07.xlsx', sheet_name='QUẬN HUYỆN (SPS only)')
    
    # Chọn cột và đổi tên
    buu_cuc_njv_df = buu_cuc_njv_df[1:]
    buu_cuc_njv_df.columns = [
        'mien', 'tinh_thanh', 'ma_quan_huyen', 'quan_huyen', 
        'ten_ngan', 'buu_cuc', 'ty_le_thanh_cong', 'don_den_tram'
    ]
    buu_cuc_njv_df = buu_cuc_njv_df[['mien', 'tinh_thanh', 'quan_huyen', 'buu_cuc']]
    buu_cuc_njv_df['tinh_thanh'] = buu_cuc_njv_df['tinh_thanh'].astype(str)
    buu_cuc_njv_df['quan_huyen'] = buu_cuc_njv_df['quan_huyen'].astype(str)
    
    # Chuẩn hóa quận/huyện, tỉnh/thành
    buu_cuc_njv_df = normalize_province_district(buu_cuc_njv_df, tinh_thanh='tinh_thanh', quan_huyen='quan_huyen')

    # Loại bỏ thông tin rỗng
    buu_cuc_njv_df = buu_cuc_njv_df.loc[
        buu_cuc_njv_df['tinh_thanh'].notna() & 
        buu_cuc_njv_df['quan_huyen'].notna()
    ].reset_index(drop=True)

    # Lưu thông tin
    buu_cuc_njv_df.to_parquet(ROOT_PATH + '/processed_data/buu_cuc_ninja_van.parquet', index=False)
    
    #############################################################################################
    # Đọc thông tin bưu cục ghn
    print('GHN...')
    buu_cuc_ghn_df = pd.read_excel(ROOT_PATH + '/raw_data/Bưu cục GHN.xlsx')

    # Chọn cột và đổi tên
    buu_cuc_ghn_df.columns=['dia_chi', 'tinh_thanh', 'quan_huyen']
    buu_cuc_ghn_df['tinh_thanh'] = buu_cuc_ghn_df['tinh_thanh'].astype(str)
    buu_cuc_ghn_df['quan_huyen'] = buu_cuc_ghn_df['quan_huyen'].astype(str)
    
    # Chuẩn hóa quận/huyện, tỉnh/thành
    buu_cuc_ghn_df = normalize_province_district(buu_cuc_ghn_df, tinh_thanh='tinh_thanh', quan_huyen='quan_huyen')

    # Loại bỏ thông tin rỗng
    buu_cuc_ghn_df = buu_cuc_ghn_df.loc[
        buu_cuc_ghn_df['tinh_thanh'].notna() & 
        buu_cuc_ghn_df['quan_huyen'].notna()
    ].reset_index(drop=True)

    # Lưu thông tin
    buu_cuc_ghn_df.to_parquet(ROOT_PATH + '/processed_data/buu_cuc_ghn.parquet', index=False)

    #############################################################################################
    # Đọc thông tin bưu cục best
    print('BEST...')
    buu_cuc_best_df = pd.read_excel(ROOT_PATH + '/raw_data/Bưu cục Best.xlsx')

    # Chọn cột và đổi tên
    buu_cuc_best_df.columns=['stt', 'are', 'tinh_thanh', 'quan_huyen', 'phuong_xa', 'buu_cuc']
    buu_cuc_best_df = buu_cuc_best_df[['tinh_thanh', 'quan_huyen', 'phuong_xa', 'buu_cuc']]
    buu_cuc_best_df['tinh_thanh'] = buu_cuc_best_df['tinh_thanh'].astype(str)
    buu_cuc_best_df['quan_huyen'] = buu_cuc_best_df['quan_huyen'].astype(str)
    
    # Chuẩn hóa quận/huyện, tỉnh/thành
    buu_cuc_best_df = normalize_province_district(buu_cuc_best_df, tinh_thanh='tinh_thanh', quan_huyen='quan_huyen')

    # Loại bỏ thông tin rỗng
    buu_cuc_best_df = buu_cuc_best_df.loc[
        buu_cuc_best_df['tinh_thanh'].notna() & 
        buu_cuc_best_df['quan_huyen'].notna()
    ].reset_index(drop=True)

    # Lưu thông tin
    buu_cuc_best_df.to_parquet(ROOT_PATH + '/processed_data/buu_cuc_best.parquet', index=False)

    #############################################################################################
    # Đọc thông tin bưu cục ghtk
    print('GHTK...')
    buu_cuc_ghtk_df = pd.read_excel(ROOT_PATH + '/raw_data/Bưu cục giao hàng tiết kiệm toàn quôc.xlsx')

    # Chọn cột và đổi tên
    buu_cuc_ghtk_df = buu_cuc_ghtk_df[['Tên bưu cục', 'Địa chỉ']]
    buu_cuc_ghtk_df.columns = ['buu_cuc', 'dia_chi']

    # Tách quận/huyện, tinh/thành
    buu_cuc_ghtk_df['tinh_thanh'] = buu_cuc_ghtk_df['dia_chi'].str.split(', ').str[-1].astype(str)
    buu_cuc_ghtk_df['quan_huyen'] = buu_cuc_ghtk_df['dia_chi'].str.split(', ').str[-2].astype(str)
    
    # Chuẩn hóa quận/huyện, tỉnh/thành
    buu_cuc_ghtk_df = normalize_province_district(buu_cuc_ghtk_df, tinh_thanh='tinh_thanh', quan_huyen='quan_huyen')
    
    # Loại bỏ thông tin rỗng
    buu_cuc_ghtk_df = buu_cuc_ghtk_df.loc[
        buu_cuc_ghtk_df['tinh_thanh'].notna() & 
        buu_cuc_ghtk_df['quan_huyen'].notna()
    ].reset_index(drop=True)

    # Lưu thông tin
    buu_cuc_ghtk_df.to_parquet(ROOT_PATH + '/processed_data/buu_cuc_ghtk.parquet', index=False)
