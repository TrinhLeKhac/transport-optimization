
import sys
from pathlib import Path
sys.path.append(Path(__file__).parent)

from config import *
from helper import *

def transform_data_tien_giao_dich():

    # Thông tin giao dịch valid
    giao_dich_valid = pd.read_parquet(ROOT_PATH + '/processed_data/giao_dich_combine_valid.parquet')
    giao_dich_valid = giao_dich_valid[giao_dich_valid['trang_thai_van_don'].isin([
        'Giao hàng thành công',
        'Đã hoàn thành',
        'Delivered | Giao hàng thành công',
        'Đã giao hàng/Chưa đối soát'
    ])]
    
    giao_dich_valid['nha_van_chuyen'] = giao_dich_valid['nha_van_chuyen'].map({
        'BEST Express': 'best',
        'Ninja Van': 'ninja_van',
        'GHN': 'ghn',
        'Shopee Express': 'shopee_express',
        'Viettel Post': 'viettel_post',
        'GHTK': 'ghtk',
        'TikiNow':'tikinow', 
    })
    cuoc_phi_giao_dich = giao_dich_valid[[
        'ma_don_hang', 'nha_van_chuyen', 
        'tinh_thanh_giao_hang', 'quan_huyen_giao_hang',
        'khoi_luong', 'co_hang_doi_tra', 'hinh_thuc_gui_hang', 'loai'
    ]].rename(columns={'tinh_thanh_giao_hang': 'tinh_thanh', 'quan_huyen_giao_hang': 'quan_huyen'})
    
    cuoc_phi_giao_dich['loai'] = cuoc_phi_giao_dich['loai'].map({
        'Nội Miền': 'noi_mien',
        'Nội Miền Đặc Biệt': 'noi_mien',
        'Nội Thành': 'noi_thanh_tinh',
        'Nội Tỉnh': 'ngoai_thanh_tinh',
        'Liên Miền Đặc Biệt': 'can_mien',
        'Liên Miền': 'can_mien',
        'Liên Vùng': 'can_mien',
    })
    cuoc_phi_giao_dich.loc[
        (cuoc_phi_giao_dich['loai'] == 'noi_thanh_tinh') & 
        (cuoc_phi_giao_dich['tinh_thanh'].isin(['Thành phố Hà Nội', 'Thành phố Hồ Chí Minh'])),
        'loai'
    ] = 'noi_thanh_tphcm_hn'
    cuoc_phi_giao_dich.loc[
        (cuoc_phi_giao_dich['loai'] == 'ngoai_thanh_tinh') & 
        (cuoc_phi_giao_dich['tinh_thanh'].isin(['Thành phố Hà Nội', 'Thành phố Hồ Chí Minh'])),
        'loai'
    ] = 'ngoai_thanh_tphcm_hn'
    cuoc_phi_giao_dich = cuoc_phi_giao_dich[[
        'tinh_thanh', 'quan_huyen', 'ma_don_hang', 
        'khoi_luong', 'hinh_thuc_gui_hang', 'loai'
    ]]

    #############################################################################################
    # Thông tin cước phí nhà vận chuyển
    cuoc_phi_nvc = pd.read_parquet(ROOT_PATH + '/processed_data/cuoc_phi_nvc.parquet')
    cuoc_phi_nvc = (
        pd.melt(
            cuoc_phi_nvc, 
            id_vars =['nha_van_chuyen', 'gt', 'lt_or_eq'], 
            value_vars =[
                'noi_thanh_tinh', 'ngoai_thanh_tinh', 
                'noi_thanh_tphcm_hn', 'ngoai_thanh_tphcm_hn', 
                'noi_mien', 'can_mien', 'cach_mien'
            ],
            var_name ='loai', value_name ='cuoc_phi'
        )
    )

    # Tổng hợp cước phí full
    cuoc_phi_giao_dich_full = cuoc_phi_giao_dich.merge(cuoc_phi_nvc, on=['loai'], how='inner')
    cuoc_phi_giao_dich_full = cuoc_phi_giao_dich_full.loc[
        (cuoc_phi_giao_dich_full['khoi_luong'] > cuoc_phi_giao_dich_full['gt']) & 
        (cuoc_phi_giao_dich_full['khoi_luong'] <= cuoc_phi_giao_dich_full['lt_or_eq'])
    ]
    cuoc_phi_giao_dich_full.loc[
        cuoc_phi_giao_dich_full['nha_van_chuyen'].isin(['ninja_van']) & 
        cuoc_phi_giao_dich_full['hinh_thuc_gui_hang'].isin(['Lấy Tận Nơi']),
        'cuoc_phi'
    ] = cuoc_phi_giao_dich_full['cuoc_phi'] + 1500 # Lấy tận nơi cộng phí 1,500
    cuoc_phi_giao_dich_full.loc[
        cuoc_phi_giao_dich_full['nha_van_chuyen'].isin(['ghn']) & 
        cuoc_phi_giao_dich_full['hinh_thuc_gui_hang'].isin(['Lấy Tận Nơi']),
        'cuoc_phi'
    ] = cuoc_phi_giao_dich_full['cuoc_phi'] + 1000 # Lấy tận nơi cộng phí 1,000

    # Transform bảng
    cuoc_phi_giao_dich_all_nvc = pd.pivot_table(
        data=cuoc_phi_giao_dich_full, 
        index=['tinh_thanh', 'quan_huyen', 'ma_don_hang', 'loai', 'khoi_luong'], 
        columns=['nha_van_chuyen'], 
        values='cuoc_phi',
        aggfunc=np.sum,
        fill_value=0
    ).rename_axis(None, axis=1).reset_index()

    return cuoc_phi_giao_dich_all_nvc
    # Lưu output
    # cuoc_phi_giao_dich_all_nvc.to_parquet('../../output/cuoc_phi_giao_dich.parquet', index=False)