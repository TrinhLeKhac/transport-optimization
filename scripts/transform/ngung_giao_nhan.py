
import sys
from pathlib import Path
sys.path.append(Path(__file__).parent)

from config import *
from helper import *

def transform_data_ngung_giao_nhan():

    # Đọc data ngưng giao nhận
    ngung_giao_nhan_df = pd.read_parquet(ROOT_PATH + '/processed_data/ngung_giao_nhan.parquet')

    # Chọn lấy cột cần thiết và đổi tên cột
    ngung_giao_nhan_df['tieu_chi'] = 'Ngưng giao nhận'
    ngung_giao_nhan_df['trong_so'] = TRONG_SO['Ngưng giao nhận']['Tiêu chí']
    for c in LIST_NVC:
        ngung_giao_nhan_df[c + '_stt'] = ngung_giao_nhan_df[c]
        ngung_giao_nhan_df[c + '_stt'] = ngung_giao_nhan_df[c + '_stt'].fillna('Bình thường')
        ngung_giao_nhan_df[c + '_stt'] = (
            ngung_giao_nhan_df[c + '_stt'].apply(lambda s: unidecode(' '.join(s.split()).strip().lower()))
        )
        ngung_giao_nhan_df.loc[ngung_giao_nhan_df[c + '_stt'].isin(['chuyen ngoai', 'cham tuyen']), c + '_stt'] = 'Quá tải'
        ngung_giao_nhan_df.loc[ngung_giao_nhan_df[c + '_stt'] != 'Quá tải', c + '_stt'] = 'Bình thường'
        
        ngung_giao_nhan_df[c + '_score'] = ngung_giao_nhan_df[c + '_stt'].map(TRONG_SO['Ngưng giao nhận']['Phân loại'])
    ngung_giao_nhan_df = ngung_giao_nhan_df[SELECTED_COLS]

    return ngung_giao_nhan_df
    # Lưu thông tin
    # ngung_giao_nhan_df.to_parquet('../../output/ngung_giao_nhan.parquet', index=False)