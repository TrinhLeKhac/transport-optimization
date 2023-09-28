
import sys
from pathlib import Path
sys.path.append(Path(__file__).parent)

from config import *
from helper import *    
    
def transform_data_kho_giao_nhan():

    # Đọc thông tin bưu cục
    buu_cuc_njv = pd.read_parquet(ROOT_PATH + '/processed_data/buu_cuc_ninja_van.parquet')
    buu_cuc_ghn = pd.read_parquet(ROOT_PATH + '/processed_data/buu_cuc_ghn.parquet')
    buu_cuc_best = pd.read_parquet(ROOT_PATH + '/processed_data/buu_cuc_best.parquet')
    buu_cuc_ghtk = pd.read_parquet(ROOT_PATH + '/processed_data/buu_cuc_ghtk.parquet')
    
    # Transform bảng
    ninja_van_df = (
        buu_cuc_njv
        .groupby(['tinh_thanh', 'quan_huyen'])
        .agg(ninja_van_so_buu_cuc=('buu_cuc', 'size'))
        .reset_index()
    )
    ghn_df = (
        buu_cuc_ghn
        .groupby(['tinh_thanh', 'quan_huyen'])
        .agg(ghn_so_buu_cuc=('dia_chi', 'size'))
        .reset_index()
    )
    best_df = (
        buu_cuc_best
        .groupby(['tinh_thanh', 'quan_huyen'])
        .agg(best_so_buu_cuc=('buu_cuc', 'size'))
        .reset_index()
    )
    ghtk_df = (
        buu_cuc_ghtk
        .groupby(['tinh_thanh', 'quan_huyen'])
        .agg(ghtk_so_buu_cuc=('buu_cuc', 'size'))
        .reset_index()
    )

    # Lấy thông tin quận/huyện, tỉnh/thành mới nhất
    province_district_norm_df = pd.read_parquet(ROOT_PATH + '/processed_data/province_mapping_district.parquet')

    # Transform thông tin kho giao nhận
    kho_giao_nhan = (
        province_district_norm_df
        .merge(ninja_van_df, on=['tinh_thanh', 'quan_huyen'], how='left')
        .merge(ghn_df, on=['tinh_thanh', 'quan_huyen'], how='left')
        .merge(best_df, on=['tinh_thanh', 'quan_huyen'], how='left')
        .merge(ghtk_df, on=['tinh_thanh', 'quan_huyen'], how='left')
        .fillna(0)
    )
    for c in ['ninja_van_so_buu_cuc', 'ghn_so_buu_cuc', 'best_so_buu_cuc', 'ghtk_so_buu_cuc']:
        kho_giao_nhan[c] = kho_giao_nhan[c].astype(int)
        
    kho_giao_nhan['ninja_van_so_buu_cuc_trong_tinh'] = (
        kho_giao_nhan.groupby('tinh_thanh')['ninja_van_so_buu_cuc'].transform(np.sum)
    )
    kho_giao_nhan['ghn_so_buu_cuc_trong_tinh'] = kho_giao_nhan.groupby('tinh_thanh')['ghn_so_buu_cuc'].transform(np.sum)
    kho_giao_nhan['best_so_buu_cuc_trong_tinh'] = kho_giao_nhan.groupby('tinh_thanh')['best_so_buu_cuc'].transform(np.sum)
    kho_giao_nhan['ghtk_so_buu_cuc_trong_tinh'] = kho_giao_nhan.groupby('tinh_thanh')['ghtk_so_buu_cuc'].transform(np.sum)
    kho_giao_nhan['so_quan_huyen'] = kho_giao_nhan.groupby('tinh_thanh')['quan_huyen'].transform(np.size)  
          
    for col in ['shopee_express', 'viettel_post', 'tikinow']:
        kho_giao_nhan[col + '_so_buu_cuc'] = 0
        kho_giao_nhan[col + '_so_buu_cuc_trong_tinh'] = 0
        kho_giao_nhan[col + '_stt'] = 'Không có bưu cục trong tỉnh'
        kho_giao_nhan[col + '_score'] = -10
    
    for col in ['ninja_van', 'ghn', 'best', 'ghtk']:
        kho_giao_nhan[col + '_stt'] = (
            kho_giao_nhan[[col + '_so_buu_cuc', col + '_so_buu_cuc_trong_tinh', 'so_quan_huyen']]
            .apply(
                lambda x: 
                status_kho_giao_nhan(x[col + '_so_buu_cuc'], x[col + '_so_buu_cuc_trong_tinh'], x['so_quan_huyen']), axis=1
            )
        )
        kho_giao_nhan[col + '_score'] = kho_giao_nhan[col + '_stt'].map(TRONG_SO['Có kho giao nhận']['Phân loại'])
    kho_giao_nhan['tieu_chi'] = 'Có kho giao nhận'
    kho_giao_nhan['trong_so'] = TRONG_SO['Có kho giao nhận']['Tiêu chí']
    kho_giao_nhan = kho_giao_nhan[SELECTED_COLS]

    # Kiểm tra data kho giao nhan
    assert kho_giao_nhan.isna().sum().all() == 0, 'Transform data có vấn đề'

    return kho_giao_nhan
    # Lưu thông tin
    # kho_giao_nhan.to_parquet('../../output/kho_giao_nhan.parquet', index=False)