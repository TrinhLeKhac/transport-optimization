
import sys
from pathlib import Path
sys.path.append(Path(__file__).parent)

from config import *
from helper import *

def transform_data_chat_luong_noi_bo():

    # Đọc data clnb ninja_van
    clnb_njv_all = pd.read_parquet(ROOT_PATH + '/processed_data/chat_luong_noi_bo_njv_all.parquet')

    # Xử lý data
    clnb_njv_all['ninja_van_stt'] = clnb_njv_all.apply(status_chat_luong_noi_bo_ninja_van, axis=1)
    clnb_njv_all['ninja_van_score'] = (
        clnb_njv_all['ninja_van_stt'].map(TRONG_SO['Chất lượng nội bộ']['Phân loại']['ninja_van'])
    )
    clnb_njv_all['tieu_chi'] = 'Chất lượng nội bộ'
    clnb_njv_all['trong_so'] = TRONG_SO['Chất lượng nội bộ']['Tiêu chí']
    clnb_njv_all = clnb_njv_all[['tinh_thanh', 'quan_huyen', 'tieu_chi', 'trong_so', 'ninja_van_stt', 'ninja_van_score']]

    # Đọc data clnb best
    clnb_best_all = pd.read_parquet(ROOT_PATH + '/processed_data/chat_luong_noi_bo_best_all.parquet')
    
    # Xử lý data
    clnb_best_all['so_don_giao'] = clnb_best_all['tong_don_giao'] * clnb_best_all['ty_le_ky_nhan_ca_dau']
    clnb_best_all['so_don_giao'] = np.round(clnb_best_all['so_don_giao'], 0).astype(int)
    clnb_best_all['backlog_cuoi_ngay'] = np.round(clnb_best_all['backlog_cuoi_ngay'], 0).astype(int)
    clnb_best_all = (
        clnb_best_all
        .groupby(['tinh_thanh'])
        .agg(
            so_don_giao = ('so_don_giao', 'sum'), 
            don_ton_dong = ('backlog_cuoi_ngay', 'sum')
        ).reset_index()
    )
    clnb_best_all['pct'] = 1 - (clnb_best_all['don_ton_dong'] / clnb_best_all['so_don_giao'])
    
    col = 'pct'
    conditions = [
        clnb_best_all[col] > 0.98, 
        (clnb_best_all[col] <= 0.98) & (clnb_best_all[col] > 0.95), 
        (clnb_best_all[col] <= 0.95) & (clnb_best_all[col] > 0.9),
        (clnb_best_all[col] <= 0.9) & (clnb_best_all[col] > 0.8),
        clnb_best_all[col] <= 0.8,
    ]
    scores = [10, 9, 8, 7, -10]
    status = [
        'Tỉ lệ trên 98%',
        'Tỉ lệ trên 95%',
        'Tỉ lệ trên 90%',
        'Tỉ lệ trên 80%',
        'Tỉ lệ bé hơn hoặc bằng 80%',
    ]
    clnb_best_all["best_stt"] = np.select(conditions, status)
    clnb_best_all["best_score"] = np.select(conditions, scores)

    # Lấy thông tin quận/huyện, tỉnh/thành mới nhất
    province_district_norm_df = pd.read_parquet(ROOT_PATH + '/processed_data/province_mapping_district.parquet')

    # Thông tin chất lượng ở cấp Tỉnh được share đều cho các quận huyện
    clnb_best_all = (
        clnb_best_all[['tinh_thanh', 'best_stt', 'best_score']].merge(
            province_district_norm_df, on='tinh_thanh', how='inner')
    )
    clnb_best_all['tieu_chi'] = 'Chất lượng nội bộ'
    clnb_best_all['trong_so'] = TRONG_SO['Chất lượng nội bộ']['Tiêu chí']
    clnb_best_all = clnb_best_all[['tinh_thanh', 'quan_huyen', 'tieu_chi', 'trong_so', 'best_stt', 'best_score']]
    
    # Tổng hợp clnb all nhà vận chuyển
    clbn_all = (
        clnb_njv_all.merge(clnb_best_all, on=['tinh_thanh', 'quan_huyen', 'tieu_chi', 'trong_so'], how='outer')
    )

    # Các nhà vận chuyển không có thông tin, fillna status = 'Không có thông tin', fillna score = 5
    clbn_all['ninja_van_stt'] = clbn_all['ninja_van_stt'].fillna('Không có thông tin')
    clbn_all['best_stt'] = clbn_all['best_stt'].fillna('Không có thông tin')

    clbn_all['ninja_van_score'] = clbn_all['ninja_van_score'].fillna(5).astype(int)
    clbn_all['best_score'] = clbn_all['best_score'].fillna(5).astype(int)
    
    clbn_all['ghn_score'] = 5
    clbn_all['shopee_express_score'] = 5
    clbn_all['viettel_post_score'] = 5
    clbn_all['ghtk_score'] = 5
    clbn_all['tikinow_score'] = 5
    
    clbn_all['ghn_stt'] = 'Không có thông tin'
    clbn_all['shopee_express_stt'] = 'Không có thông tin'
    clbn_all['viettel_post_stt'] = 'Không có thông tin'
    clbn_all['ghtk_stt'] = 'Không có thông tin'
    clbn_all['tikinow_stt'] = 'Không có thông tin'
    
    clbn_all = clbn_all[SELECTED_COLS]

    return clbn_all
    # Lưu thông tin
    # clbn_all.to_parquet('../../output/chat_luong_noi_bo_all.parquet', index=False)
    