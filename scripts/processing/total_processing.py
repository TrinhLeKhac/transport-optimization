import os
import sys
from datetime import datetime
from pathlib import Path
import optparse

ROOT_PATH = str(Path(__file__).parent.parent.parent)
sys.path.append(ROOT_PATH)

from scripts.processing.bang_gia_cuoc import xu_ly_bang_gia_cuoc
from scripts.processing.chat_luong_noi_bo import xu_ly_chat_luong_noi_bo
from scripts.processing.kho_giao_nhan import xu_ly_kho_giao_nhan
from scripts.processing.danh_gia_zns import xu_ly_danh_gia_zns
from scripts.processing.ngung_giao_nhan import xu_ly_ngung_giao_nhan
from scripts.processing.phan_vung_nha_van_chuyen import xu_ly_phan_vung_nha_van_chuyen
from scripts.processing.giao_dich import xu_ly_giao_dich, xu_ly_giao_dich_co_khoi_luong, tong_hop_thong_tin_giao_dich


def total_processing(run_date_str, from_api=True):

    if not os.path.exists(ROOT_PATH + '/processed_data'):
        os.makedirs(ROOT_PATH + '/processed_data')

    print('1. Xử lý data bảng giá cước...')
    xu_ly_bang_gia_cuoc()
    print('>>> Done\n')

    print('2. Xử lý data chất lượng nội bộ Ninja Van...')
    xu_ly_chat_luong_noi_bo()
    print('>>> Done\n')

    print('3. Xử lý data kho giao nhận...')
    xu_ly_kho_giao_nhan()
    print('>>> Done\n')

    print('4. Xử lý data đánh giá ZNS...')
    xu_ly_danh_gia_zns(run_date_str, from_api=from_api)
    print('>>> Done\n')

    print('5. Xử lý data ngưng giao nhận...')
    xu_ly_ngung_giao_nhan()
    print('>>> Done\n')

    print('6. Xử lý data phân vùng nhà vận chuyển...')
    xu_ly_phan_vung_nha_van_chuyen()
    print('>>> Done\n')

    if from_api:
        print('7. Tổng hợp thông tin giao dịch...')
        tong_hop_thong_tin_giao_dich(run_date_str, from_api=from_api)
        print('>>> Done\n')
    else:
        print('7. Xử lý data giao dịch...')
        xu_ly_giao_dich()
        print('>>> Done\n')

        print('8. Xử lý data giao dịch có khối lượng...')
        xu_ly_giao_dich_co_khoi_luong()
        print('>>> Done\n')

        print('9. Tổng hợp thông tin giao dịch...')
        tong_hop_thong_tin_giao_dich(from_api=from_api)
        print('>>> Done\n')


if __name__ == '__main__':

    parser = optparse.OptionParser(description="Running mode")
    parser.add_option(
        '-m', '--mode',
        action="store", dest="mode",
        help="mode string", default="excel"
    )
    parser.add_option(
        '-r', '--run_date',
        action="store", dest="run_date",
        help="run_date string", default=f"{datetime.now().strftime('%Y-%m-%d')}"
    )
    options, args = parser.parse_args()
    # print(options.mode)
    # print(options.run_date)
    if options.mode == 'api':
        total_processing(options.run_date, from_api=True)
    elif options.mode == 'excel':
        total_processing(options.run_date, from_api=False)
