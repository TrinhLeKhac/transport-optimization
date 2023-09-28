
import sys
from pathlib import Path
sys.path.append(Path(__file__).parent)

from config import *
from helper import *

from processing.bang_gia_cuoc import xu_ly_bang_gia_cuoc
from processing.chat_luong_noi_bo import xu_ly_chat_luong_noi_bo_ninja_van, xu_ly_chat_luong_noi_bo_best
from processing.kho_giao_nhan import xu_ly_kho_giao_nhan
from processing.danh_gia_zns import xu_ly_danh_gia_zns
from processing.ngung_giao_nhan import xu_ly_ngung_giao_nhan
from processing.phan_vung_nha_van_chuyen import xu_ly_phan_vung_nha_van_chuyen
from processing.giao_dich import xu_ly_giao_dich, xu_ly_giao_dich_co_khoi_luong, tong_hop_thong_tin_giao_dich

def total_processing():
    print('Xử lý data bảng giá cước...')
    xu_ly_bang_gia_cuoc()
    print('>>> Done\n')
    
    print('Xử lý data chất lượng nội bộ ninja van...')
    xu_ly_chat_luong_noi_bo_ninja_van()
    print('>>> Done\n')
    
    print('Xử lý data chất lượng nội bộ best...')
    xu_ly_chat_luong_noi_bo_best()
    print('>>> Done\n')
    
    print('Xử lý data kho giao nhận...')
    xu_ly_kho_giao_nhan()
    print('>>> Done\n')
    
    print('Xử lý data đánh giá ZNS...')
    xu_ly_danh_gia_zns()
    print('>>> Done\n')
    
    print('Xử lý data ngưng giao nhận...')
    xu_ly_ngung_giao_nhan()
    print('>>> Done\n')
    
    print('Xử lý data phân vùng nhà vận chuyển...')
    xu_ly_phan_vung_nha_van_chuyen()
    print('>>> Done\n')
    
    print('Xử lý data giao dịch...')
    xu_ly_giao_dich()

    print('Xử lý data giao dịch có khối lượng...')
    xu_ly_giao_dich_co_khoi_luong()

    print('Tổng hợp thông tin giao dịch...')
    tong_hop_thong_tin_giao_dich()
    print('>>> Done\n')
    
if __name__=="__main__":
    
    total_processing()