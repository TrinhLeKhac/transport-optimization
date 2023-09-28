
import sys
from pathlib import Path
sys.path.append(Path(__file__).parent)

from config import *
from helper import *

def xu_ly_bang_gia_cuoc():
    
    # Đọc file bảng giá cước chung
    bang_gia_cuoc_df = pd.read_excel(ROOT_PATH + '/raw_data/Bảng Cước Phí.xlsx', sheet_name='Bảng Giá Khối Lượng')
    
    # Tách lấy thông tin bảng giá cước ninja van và xử lý
    ninja_van_df = pd.concat([bang_gia_cuoc_df.iloc[1:21, :2], bang_gia_cuoc_df.iloc[1:21, 2:9]], axis=1).reset_index(drop=True)
    ninja_van_df.columns = ['gt', 'lt_or_eq', 'noi_thanh_tinh', 'ngoai_thanh_tinh', 'noi_thanh_tphcm_hn', 'ngoai_thanh_tphcm_hn', 'noi_mien', 'can_mien', 'cach_mien']
    for i in range(80):
        ninja_van_df.loc[20+i, :] = [10000 + 500*i, 10500 + 500*i, 70 + 9*int(i/2), 70 + 9*int(i/2), 70 + 9*int(i/2), 70 + 9*int(i/2), 82 + 11*int(i/2), 124 + 16*int(i/2), 124 + 16*int(i/2)]
    # ninja_van_df.iloc[:, 2:] = ninja_van_df.iloc[:, 2:] + 1.5 # Phi lấy hàng, chỉ khi lấy tận nơi mới thêm vào
    ninja_van_df['nha_van_chuyen'] = 'ninja_van'

    # Tách lấy thông tin bảng giá cước best và xử lý
    best_df = pd.concat([bang_gia_cuoc_df.iloc[1:21, :2], bang_gia_cuoc_df.iloc[1:21, 9:16]], axis=1).reset_index(drop=True)
    best_df.columns = ['gt', 'lt_or_eq', 'noi_thanh_tinh', 'ngoai_thanh_tinh', 'noi_thanh_tphcm_hn', 'ngoai_thanh_tphcm_hn', 'noi_mien', 'can_mien', 'cach_mien']
    for i in range(180):
        best_df.loc[20+i, :] = [10000 + 500*i, 10500 + 500*i, 39 + 2*i, 39 + 2*i, 39 + 2*i, 39 + 2*i, 39 + 2*i, 39 + 2*i, 39 + 2*i]
    best_df['nha_van_chuyen'] = 'best'

    # Tách lấy thông tin bảng giá cước shopee express và xử lý
    shopee_express_df = pd.concat([bang_gia_cuoc_df.iloc[1:21, :2], bang_gia_cuoc_df.iloc[1:21, 16:23]], axis=1).reset_index(drop=True)
    shopee_express_df.columns = ['gt', 'lt_or_eq', 'noi_thanh_tinh', 'ngoai_thanh_tinh', 'noi_thanh_tphcm_hn', 'ngoai_thanh_tphcm_hn', 'noi_mien', 'can_mien', 'cach_mien']
    for i in range(80):
        shopee_express_df.loc[20+i, :] = [10000 + 500*i, 10500 + 500*i, 58 + 2*i, 58 + 2*i, 58 + 2*i, 58 + 2*i, 108 + 3*i, 112 + 7*i, 112 + 7*i]
    shopee_express_df['nha_van_chuyen'] = 'shopee_express'

    # Tách lấy thông tin bảng giá cước ghn và xử lý
    ghn_df = pd.concat([bang_gia_cuoc_df.iloc[1:21, :2], bang_gia_cuoc_df.iloc[1:21, 23:30]], axis=1).reset_index(drop=True)
    ghn_df.columns = ['gt', 'lt_or_eq', 'noi_thanh_tinh', 'ngoai_thanh_tinh', 'noi_thanh_tphcm_hn', 'ngoai_thanh_tphcm_hn', 'noi_mien', 'can_mien', 'cach_mien']
    for i in range(80):
        ghn_df.loc[20+i, :] = [10000 + 500*i, 10500 + 500*i, 54 + 5*int(i/2), 54 + 5*int(i/2), 54 + 5*int(i/2), 54 + 5*int(i/2), 54 + 5*int(i/2), 54 + 5*int(i/2), 54 + 5*int(i/2)]
    # ghn_df.iloc[:, 2:] = ghn_df.iloc[:, 2:] + 1 # Phí lấy hàng, chỉ khi lấy tận nơi mới thêm vào
    ghn_df['nha_van_chuyen'] = 'ghn'

    # Tách lấy thông tin bảng giá cước viettel post và xử lý
    viettel_post_df = pd.concat([bang_gia_cuoc_df.iloc[1:21, :2], bang_gia_cuoc_df.iloc[1:21, 30:37]], axis=1).reset_index(drop=True)
    viettel_post_df.columns = ['gt', 'lt_or_eq', 'noi_thanh_tinh', 'ngoai_thanh_tinh', 'noi_thanh_tphcm_hn', 'ngoai_thanh_tphcm_hn', 'noi_mien', 'can_mien', 'cach_mien']
    for i in range(80):
        viettel_post_df.loc[20+i, :] = [10000 + 500*i, 10500 + 500*i, 47.5 + 2.5*i, 47.5 + 2.5*i, 47.5 + 2.5*i, 47.5 + 2.5*i, 54.5 + 2.5*i, 64 + 3*i, 64 + 3*i]
    viettel_post_df['nha_van_chuyen'] = 'viettel_post'

    # Tách lấy thông tin bảng giá cước ghtk và xử lý
    ghtk_df = pd.concat([bang_gia_cuoc_df.iloc[1:21, :2], bang_gia_cuoc_df.iloc[1:21, 37:44]], axis=1).reset_index(drop=True)
    ghtk_df.columns = ['gt', 'lt_or_eq', 'noi_thanh_tinh', 'ngoai_thanh_tinh', 'noi_thanh_tphcm_hn', 'ngoai_thanh_tphcm_hn', 'noi_mien', 'can_mien', 'cach_mien']
    for i in range(80):
        ghtk_df.loc[20+i, :] = [10000 + 500*i, 10500 + 500*i, 85 + 2.5*i, 85 + 2.5*i, 59.5 + 2.5*i, 67.5 + 2.5*i, 85 + 2.5*i, 127.5 + 2.5*i, 127.5 + 2.5*i]
    ghtk_df['nha_van_chuyen'] = 'ghtk'

    # Tách lấy thông tin bảng giá cước tikinow và xử lý
    tikinow_df = pd.concat([bang_gia_cuoc_df.iloc[1:21, :2], bang_gia_cuoc_df.iloc[1:21, 44:51]], axis=1).reset_index(drop=True)
    tikinow_df.columns = ['gt', 'lt_or_eq', 'noi_thanh_tinh', 'ngoai_thanh_tinh', 'noi_thanh_tphcm_hn', 'ngoai_thanh_tphcm_hn', 'noi_mien', 'can_mien', 'cach_mien']
    for i in range(80):
        tikinow_df.loc[20+i, :] = [10000 + 500*i, 10500 + 500*i, 55.5 + 2.5*i, 59.5 + 2.5*i, 55.5 + 2.5*i, 59.5 + 2.5*i, 105.5 + 5.5*i, 116.5 + 5.5*i, 126.5 + 5.5*i]
    tikinow_df['nha_van_chuyen'] = 'tikinow'

    # Tổng hợp thông tin
    cuoc_phi_df = pd.concat([ninja_van_df, best_df, shopee_express_df, ghn_df, viettel_post_df, ghtk_df, tikinow_df], ignore_index=True)
    cuoc_phi_df = cuoc_phi_df[[
        'nha_van_chuyen', 'gt', 'lt_or_eq', 
        'noi_thanh_tinh', 'ngoai_thanh_tinh', 
        'noi_thanh_tphcm_hn', 'ngoai_thanh_tphcm_hn', 
        'noi_mien', 'can_mien', 'cach_mien'
    ]]
    cuoc_phi_df = cuoc_phi_df.set_index(['nha_van_chuyen', 'gt', 'lt_or_eq'])
    cuoc_phi_df = (cuoc_phi_df*1000).astype(int).reset_index() # đưa giá tiền từ 1.5 -> 1,500 (giá chuẩn)

    # Lưu thông tin đã xử lý
    cuoc_phi_df.to_parquet(ROOT_PATH + '/processed_data/cuoc_phi_nvc.parquet', index=False)