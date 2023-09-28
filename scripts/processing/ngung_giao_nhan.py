
import sys
from pathlib import Path
sys.path.append(Path(__file__).parent)

from config import *
from helper import *

def xu_ly_ngung_giao_nhan():

    # Đọc data ngưng giao nhận
    ngung_giao_nhan_df = pd.read_excel(ROOT_PATH + '/raw_data/Cập nhật thủ công khu vực giao hàng NVC.xlsx')

    # Chọn lấy cột cần thiết và đổi tên cột
    ngung_giao_nhan_df = ngung_giao_nhan_df.iloc[:, 1:]
    ngung_giao_nhan_df.drop(['Tên Ngắn', 'Mã Quận/Huyện'], axis=1, inplace=True)
    ngung_giao_nhan_df.columns = [
        'tinh_thanh', 'quan_huyen', 
        'ninja_van', 'ghn', 'best', 'shopee_express', 'ghtk', 'viettel_post'
    ]

    # Chuẩn hóa thông tin quận/huyện, tỉnh/thành
    ngung_giao_nhan_df = normalize_province_district(ngung_giao_nhan_df, tinh_thanh='tinh_thanh', quan_huyen='quan_huyen')
    ngung_giao_nhan_df.loc[ngung_giao_nhan_df['tinh_thanh'].notna() & ngung_giao_nhan_df['quan_huyen'].notna()]
    
    # Bổ sung thêm nvc cho đủ schema
    ngung_giao_nhan_df.drop(['ghtk', 'viettel_post'], axis=1, inplace=True)
    ngung_giao_nhan_df['ghtk'] = None
    ngung_giao_nhan_df['viettel_post'] = None
    ngung_giao_nhan_df['tikinow'] = None

    # Lưu thông tin
    ngung_giao_nhan_df.to_parquet(ROOT_PATH + '/processed_data/ngung_giao_nhan.parquet', index=False)