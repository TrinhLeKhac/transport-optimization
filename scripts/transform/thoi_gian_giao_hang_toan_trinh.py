
import sys
from pathlib import Path
sys.path.append(Path(__file__).parent)

from config import *
from helper import *

LOAI_VAN_CHUYEN_DICT = {
    'Nội Miền': 'Nội Miền',
    'Nội Miền Đặc Biệt': 'Nội Miền',
    'Liên Miền': 'Cận Miền',
    'Liên Miền Đặc Biệt': 'Cận Miền',
    'Liên Vùng': 'Cận Miền',
    'Nội Tỉnh': 'Ngoại Thành Tỉnh',
    'Nội Thành': 'Nội Thành Tỉnh',
}

def transform_data_thoi_gian_giao_hang_toan_trinh():
    
    # Đọc thông tin giao dịch valid
    giao_dich_valid = pd.read_parquet(ROOT_PATH + '/processed_data/giao_dich_combine_valid.parquet')
    
    # Xử lý data
    giao_dich_valid = giao_dich_valid[giao_dich_valid['trang_thai_van_don'].isin([
        'Giao hàng thành công',
        'Đã hoàn thành',
        'Delivered | Giao hàng thành công',
        'Thành công - Phát thành công',
        'Đã giao hàng/Chưa đối soát',
        'Đã đối soát',
    ])]
    
    giao_dich_valid['nha_van_chuyen'] = giao_dich_valid['nha_van_chuyen'].map({
        'BEST Express': 'best',
        'Ninja Van': 'ninja_van',
        'GHN': 'ghn',
        'Shopee Express': 'shopee_express',
        'Viettel Post': 'viettel_post',
        'GHTK': 'ghtk',
        'TikiNow': 'tikinow',
    })
    thoi_gian_giao_hang = giao_dich_valid[[
        'tao_luc', 'ma_don_hang', 'nha_van_chuyen',
        'tinh_thanh_giao_hang', 'quan_huyen_giao_hang',
        'so_lan_giao', 'hinh_thuc_gui_hang', 'co_hang_doi_tra',
        'giao_luc', 'loai'
    ]].rename(columns={'tinh_thanh_giao_hang': 'tinh_thanh', 'quan_huyen_giao_hang': 'quan_huyen'})

    thoi_gian_giao_hang['loai'] = thoi_gian_giao_hang['loai'].map(LOAI_VAN_CHUYEN_DICT)
    thoi_gian_giao_hang = thoi_gian_giao_hang.loc[thoi_gian_giao_hang['giao_luc'].notna()]
    thoi_gian_giao_hang['thoi_gian_giao_hang'] = (
        thoi_gian_giao_hang['giao_luc'] - thoi_gian_giao_hang['tao_luc']
    ).astype('timedelta64[h]')
    
    # Transform bảng
    thoi_gian_giao_hang_agg = (
        thoi_gian_giao_hang
        .groupby(['tinh_thanh', 'quan_huyen', 'nha_van_chuyen', 'loai'])
        .agg(tong_don=('thoi_gian_giao_hang', 'count'), thoi_gian_giao_tb=('thoi_gian_giao_hang', 'mean'))
        .reset_index()
    )
    thoi_gian_giao_hang_agg_pivot1 = pd.pivot_table(
        data=thoi_gian_giao_hang_agg, 
        index=['tinh_thanh', 'quan_huyen', 'loai'], 
        columns=['nha_van_chuyen'], 
        values='tong_don',
        aggfunc=np.sum,
        fill_value=-1
    ).rename_axis(None, axis=1).reset_index()
    
    thoi_gian_giao_hang_agg_pivot1 = thoi_gian_giao_hang_agg_pivot1.rename(
        columns=dict(zip(LIST_NVC, [nvc + '_tong_don' for nvc in LIST_NVC]))
    )
    
    thoi_gian_giao_hang_agg_pivot2 = pd.pivot_table(
        data=thoi_gian_giao_hang_agg, 
        index=['tinh_thanh', 'quan_huyen', 'loai'], 
        columns=['nha_van_chuyen'], 
        values='thoi_gian_giao_tb',
        aggfunc=np.sum,
        fill_value=-1
    ).rename_axis(None, axis=1).reset_index()
    
    thoi_gian_giao_hang_agg_pivot2 = thoi_gian_giao_hang_agg_pivot2.rename(
        columns=dict(zip(LIST_NVC, [nvc + '_thoi_gian_giao_tb' for nvc in LIST_NVC]))
    )
    thoi_gian_giao_hang_agg_pivot = (
        thoi_gian_giao_hang_agg_pivot1.merge(
            thoi_gian_giao_hang_agg_pivot2, on=['tinh_thanh', 'quan_huyen', 'loai'], how='inner')
    )
    for col in LIST_NVC:
        if col+'_tong_don' not in thoi_gian_giao_hang_agg_pivot.columns.tolist():
            thoi_gian_giao_hang_agg_pivot[col+'_tong_don'] = -1 # không phát sinh đơn hàng
            thoi_gian_giao_hang_agg_pivot[col+'_thoi_gian_giao_tb'] = -1 # không phát sinh đơn hàng
            
    # Kết hợp bảng
    for col in LIST_NVC:
        thoi_gian_giao_hang_agg_pivot[col + '_stt'] = (
            thoi_gian_giao_hang_agg_pivot[[col+'_tong_don', col+'_thoi_gian_giao_tb', 'loai']]
            .apply(
                lambda x: score_thoi_gian_giao_hang(x[col+'_tong_don'], x[col+'_thoi_gian_giao_tb'], x['loai']), axis=1
            )
        )
        thoi_gian_giao_hang_agg_pivot[col + '_score'] = (
            thoi_gian_giao_hang_agg_pivot[[col + '_stt', 'loai']]
            .apply(
                lambda x: 
                TRONG_SO['Thời gian giao hàng']['Phân loại'][x['loai']][x[col + '_stt']], axis=1
            )
        )
    thoi_gian_giao_hang_agg_pivot['tieu_chi'] = 'Thời gian giao hàng'
    thoi_gian_giao_hang_agg_pivot['trong_so'] = TRONG_SO['Thời gian giao hàng']['Tiêu chí']
    thoi_gian_giao_hang_agg_pivot = thoi_gian_giao_hang_agg_pivot[SELECTED_COLS + ['loai']]

    # Kết hợp bảng
    thoi_gian_giao_hang_final1 = (
        thoi_gian_giao_hang_agg_pivot
        .groupby(['tinh_thanh', 'quan_huyen', 'tieu_chi', 'trong_so'])
        .apply(transform_dict)
    )
    thoi_gian_giao_hang_final2 = (
        thoi_gian_giao_hang_agg_pivot
        .groupby(['tinh_thanh', 'quan_huyen', 'tieu_chi', 'trong_so'])
        .agg('mean')
    )
    thoi_gian_giao_hang_final = thoi_gian_giao_hang_final1.join(thoi_gian_giao_hang_final2).reset_index()
    thoi_gian_giao_hang_final = thoi_gian_giao_hang_final[SELECTED_COLS]

    # Check data thời gian giao hàng toàn trình
    thoi_gian_giao_hang_final.isna().sum().all() == 0, 'Transform data không chính xác'

    return thoi_gian_giao_hang_final
    # Lưu thông tin
    # thoi_gian_giao_hang_final.to_parquet('../../output/thoi_gian_giao_hang_toan_trình.parquet', index=False)