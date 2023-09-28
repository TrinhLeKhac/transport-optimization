
import sys
from pathlib import Path
sys.path.append(Path(__file__).parent)

from config import *
from helper import *

from transform.chat_luong_noi_bo import transform_data_chat_luong_noi_bo
from transform.danh_gia_zns import transform_data_danh_gia_zns
from transform.kho_giao_nhan import transform_data_kho_giao_nhan
from transform.ngung_giao_nhan import transform_data_ngung_giao_nhan
from transform.thoi_gian_giao_hang_toan_trinh import transform_data_thoi_gian_giao_hang_toan_trinh
from transform.ti_le_giao_hang import transform_data_ti_le_giao_hang
from transform.tien_giao_dich import transform_data_tien_giao_dich

def merge_default_values(target_df, tieu_chi, trong_so, status, score):
    print('Reading normalize address...')
    province_district_norm_df = pd.read_parquet(ROOT_PATH + '/processed_data/province_mapping_district.parquet')

    print('Number rows before: ' + str(len(target_df)))
    target_df = province_district_norm_df.merge(target_df, on=['tinh_thanh', 'quan_huyen'], how='left')
    print('Number rows after: ' + str(len(target_df)))
    target_df['tieu_chi'] = tieu_chi
    target_df['trong_so'] = trong_so
    for col in STATUS_NVC:
        target_df.loc[target_df[col].isna(), col] = status
    for col in SCORE_NVC: 
        target_df.loc[target_df[col].isna(), col] = score
    return target_df
    
def total_transform():

    print('Transform data kho giao nhận...')
    ngung_giao_nhan = transform_data_ngung_giao_nhan()
    assert ngung_giao_nhan.isna().sum().all() == 0, 'Transform data không chính xác'
    
    ngung_giao_nhan = merge_default_values(
        ngung_giao_nhan, 
        tieu_chi='Ngưng giao nhận', 
        trong_so=10,
        status='Bình thường',
        score=1
    )
    print('>>> Done\n')

    print('Transform data đánh giá ZNS...')
    danh_gia_zns = transform_data_danh_gia_zns()
    assert danh_gia_zns.isna().sum().all() == 0, 'Transform data không chính xác'
    
    danh_gia_zns = merge_default_values(
        danh_gia_zns, 
        tieu_chi='Đánh giá ZNS', 
        trong_so=3,
        status='Không có thông tin',
        score=5,
    )
    print('>>> Done\n')

    print('Transform data tỉ lệ giao hàng...')
    ti_le_giao_hang = transform_data_ti_le_giao_hang()
    assert ti_le_giao_hang.isna().sum().all() == 0, 'Transform data không chính xác'
    
    ti_le_giao_hang = merge_default_values(
        ti_le_giao_hang, 
        tieu_chi='Tỉ lệ giao hàng', 
        trong_so=10,
        status={'tong_don': 0, 'ti_le_giao_thanh_cong': -4},
        score=5,
    )
    print('>>> Done\n')
    
    print('Transform data chất lượng nội bộ...')
    chat_luong_noi_bo = transform_data_chat_luong_noi_bo()
    assert chat_luong_noi_bo.isna().sum().all() == 0, 'Transform data không chính xác'
    
    chat_luong_noi_bo = merge_default_values(
        chat_luong_noi_bo, 
        tieu_chi='Chất lượng nội bộ', 
        trong_so=2,
        status='Không có thông tin',
        score=5,
    )
    print('>>> Done\n')

    print('Transform data thời gian giao hàng toàn trình...')
    thoi_gian_giao_hang = transform_data_thoi_gian_giao_hang_toan_trinh()
    assert thoi_gian_giao_hang.isna().sum().all() == 0, 'Transform data không chính xác'
    
    thoi_gian_giao_hang = merge_default_values(
        thoi_gian_giao_hang, 
        tieu_chi='Thời gian giao hàng', 
        trong_so=10,
        status={
            'Nội Thành Tỉnh': 5,
            'Ngoại Thành Tỉnh': 5,
            'Nội Miền': 5,
            'Cận Miền': 5,
        },
        score=5,
    )
    print('>>> Done\n')

    print('Transform data kho giao nhận...')
    kho_giao_nhan = transform_data_kho_giao_nhan()
    assert kho_giao_nhan.isna().sum().all() == 0, 'Transform data không chính xác'
    
    kho_giao_nhan = merge_default_values(
        kho_giao_nhan, 
        tieu_chi='Có kho giao nhận', 
        trong_so=3,
        status='Không có thông tin',
        score=5,
    )
    print('>>> Done\n')
    
    print('Transform data tiền giao dịch...')
    tien_giao_dich = transform_data_tien_giao_dich()
    print('>>> Done\n')

    return (
        ngung_giao_nhan, danh_gia_zns, 
        ti_le_giao_hang, chat_luong_noi_bo, 
        thoi_gian_giao_hang, kho_giao_nhan, 
        tien_giao_dich
    )