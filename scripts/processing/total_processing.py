import optparse
import os
import sys
from datetime import datetime
from pathlib import Path

ROOT_PATH = str(Path(__file__).parent.parent.parent)
sys.path.append(ROOT_PATH)

from scripts.processing.bang_gia_cuoc import xu_ly_bang_gia_cuoc
from scripts.processing.chat_luong_noi_bo import (
    xu_ly_chat_luong_noi_bo_lazada, xu_ly_chat_luong_noi_bo_ninja_van)
from scripts.processing.danh_gia_zns import (xu_ly_danh_gia_zns,
                                             xu_ly_danh_gia_zns_1_sao)
from scripts.processing.get_latest_location import (
    get_latest_province_mapping_district,
    get_latest_province_mapping_district_json,
    get_latest_province_mapping_district_mapping_ward,
    get_latest_province_mapping_district_mapping_ward_json)
from scripts.processing.giao_dich import (tong_hop_thong_tin_giao_dich,
                                          xu_ly_giao_dich,
                                          xu_ly_giao_dich_co_khoi_luong)
from scripts.processing.kho_giao_nhan import xu_ly_kho_giao_nhan
from scripts.processing.ngung_giao_nhan import (xu_ly_ngung_giao_nhan,
                                                xu_ly_ngung_giao_nhan_lazada,
                                                xu_ly_ngung_giao_nhan_level_3,
                                                xu_ly_ngung_giao_nhan_shopee)
from scripts.processing.phan_vung_nha_van_chuyen import \
    xu_ly_phan_vung_nha_van_chuyen
from scripts.utilities.helper import *


@exception_wrapper
def total_processing(run_date_str, from_api=True, n_days_back=30):

    print(
        "0. Lấy thông tin metadata tỉnh thành, quận huyện, phường xã mới nhất từ API..."
    )

    print("0.1 Lấy thông tin mapping tỉnh thành, quận huyện mới nhất ...")
    get_latest_province_mapping_district()

    print("0.2 Lấy thông tin mapping tỉnh thành, quận huyện mới nhất (dạng json) ...")
    get_latest_province_mapping_district_json()

    # print('0.3 Lấy thông tin mapping tỉnh thành, quận huyện, phường xã mới nhất ...')
    # get_latest_province_mapping_district_mapping_ward()
    #
    # print('0.4 Lấy thông tin mapping tỉnh thành, quận huyện, phường xã mới nhất (dạng json)...')
    # get_latest_province_mapping_district_mapping_ward_json()
    print(">>> Done\n")

    if not os.path.exists(ROOT_PATH + "/processed_data"):
        os.makedirs(ROOT_PATH + "/processed_data")

    print("1. Xử lý data bảng giá cước...")
    xu_ly_bang_gia_cuoc()
    print(">>> Done\n")

    print("2. Xử lý data chất lượng nội bộ Ninja Van, Lazada...")
    xu_ly_chat_luong_noi_bo_ninja_van()
    xu_ly_chat_luong_noi_bo_lazada()
    print(">>> Done\n")

    print("3. Xử lý data kho giao nhận...")
    xu_ly_kho_giao_nhan()
    print(">>> Done\n")

    print("4. Xử lý data đánh giá ZNS...")
    xu_ly_danh_gia_zns(run_date_str, from_api=from_api, n_days_back=n_days_back)
    if from_api:
        xu_ly_danh_gia_zns_1_sao(run_date_str)
    print(">>> Done\n")

    print("5. Xử lý data ngưng giao nhận...")
    xu_ly_ngung_giao_nhan()
    xu_ly_ngung_giao_nhan_shopee()
    xu_ly_ngung_giao_nhan_lazada()
    xu_ly_ngung_giao_nhan_level_3()
    print(">>> Done\n")

    print("6. Xử lý data phân vùng nhà vận chuyển...")
    xu_ly_phan_vung_nha_van_chuyen()
    print(">>> Done\n")

    if from_api:
        print("7. Tổng hợp thông tin giao dịch...")
        tong_hop_thong_tin_giao_dich(
            run_date_str, from_api=from_api, n_days_back=n_days_back, save_output=True
        )
        print(">>> Done\n")

        print("8. Tổng hợp thông tin giao dịch tổng...")
        valid_order_df = tong_hop_thong_tin_giao_dich(
            run_date_str, from_api=from_api, n_days_back=70, save_output=False
        )
        valid_order_df.to_parquet(
            ROOT_PATH + "/processed_data/total_order.parquet", index=False
        )
        print(">>> Done\n")
    else:
        print("7. Xử lý data giao dịch...")
        xu_ly_giao_dich()
        print(">>> Done\n")

        print("8. Xử lý data giao dịch có khối lượng...")
        xu_ly_giao_dich_co_khoi_luong()
        print(">>> Done\n")

        print("9. Tổng hợp thông tin giao dịch...")
        tong_hop_thong_tin_giao_dich(
            run_date_str, from_api=from_api, n_days_back=n_days_back, save_output=True
        )
        print(">>> Done\n")


if __name__ == "__main__":

    parser = optparse.OptionParser(description="Running mode")
    parser.add_option(
        "-m",
        "--mode",
        type=str,
        # action="store", dest="mode",
        # help="mode string",
        default="excel",
    )
    parser.add_option(
        "-r",
        "--run_date",
        type=str,
        # action="store", dest="run_date",
        # help="run_date string",
        default=f"{datetime.now().strftime('%Y-%m-%d')}",
    )
    options, args = parser.parse_args()
    # print(options.mode)
    # print(options.run_date)

    n_days_back = 30

    if options.mode == "api":
        print(
            f"Processing data on date = {options.run_date} with interval = {n_days_back} from API get data order, zns..."
        )
        total_processing(options.run_date, from_api=True, n_days_back=n_days_back)
    elif options.mode == "excel":
        print("Processing data from Excel File...")
        total_processing(options.run_date, from_api=False, n_days_back=n_days_back)
