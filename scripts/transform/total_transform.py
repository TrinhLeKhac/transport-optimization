import optparse
import os
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

ROOT_PATH = str(Path(__file__).parent.parent.parent)
sys.path.append(ROOT_PATH)

from scripts.transform.chat_luong_noi_bo import (
    transform_data_chat_luong_noi_bo_lazada,
    transform_data_chat_luong_noi_bo_ninja_van)
from scripts.transform.danh_gia_zns import transform_data_danh_gia_zns
from scripts.transform.don_ton_dong import get_khu_vuc_ton_dong
from scripts.transform.kho_giao_nhan import transform_data_kho_giao_nhan
from scripts.transform.ngung_giao_nhan import (
    transform_data_ngung_giao_nhan, transform_data_ngung_giao_nhan_level_3)
from scripts.transform.thoi_gian_giao_hang_toan_trinh import \
    transform_data_thoi_gian_giao_hang_toan_trinh
from scripts.transform.ti_le_giao_hang import transform_data_ti_le_giao_hang
from scripts.utilities.helper import *


@exception_wrapper
def total_transform(run_date_str, show_logs=True):

    if not os.path.exists(ROOT_PATH + "/transform"):
        os.makedirs(ROOT_PATH + "/transform")

    if show_logs:
        print("1. Transform data kho giao nhận...")
    ngung_giao_nhan = transform_data_ngung_giao_nhan()
    if show_logs:
        print("Done\n")

    if show_logs:
        print("2. Transform data đánh giá ZNS...")
    danh_gia_zns = transform_data_danh_gia_zns()
    if show_logs:
        print("Done\n")

    if show_logs:
        print("3. Transform data tỉ lệ giao hàng...")
    ti_le_giao_hang = transform_data_ti_le_giao_hang(run_date_str)
    if show_logs:
        print(">>> Done\n")

    if show_logs:
        print("4. Transform data chất lượng nội bộ...")
    chat_luong_noi_bo_ninja_van = transform_data_chat_luong_noi_bo_ninja_van()
    chat_luong_noi_bo_lazada = transform_data_chat_luong_noi_bo_lazada()
    chat_luong_noi_bo = pd.concat(
        [chat_luong_noi_bo_ninja_van, chat_luong_noi_bo_lazada], ignore_index=True
    )

    transform_data_ngung_giao_nhan_level_3()
    if show_logs:
        print(">>> Done\n")

    if show_logs:
        print("5. Transform data thời gian giao hàng toàn trình...")
    thoi_gian_giao_hang = transform_data_thoi_gian_giao_hang_toan_trinh()
    if show_logs:
        print(">>> Done\n")

    if show_logs:
        print("6. Transform data kho giao nhận...")
    kho_giao_nhan = transform_data_kho_giao_nhan()
    if show_logs:
        print(">>> Done\n")

    if show_logs:
        print("7. Transform data khu vực bị dồn đơn hàng...")
    don_ton_dong = get_khu_vuc_ton_dong(run_date_str)
    if show_logs:
        print(">>> Done\n")

    return (
        ngung_giao_nhan,
        danh_gia_zns,
        ti_le_giao_hang,
        chat_luong_noi_bo,
        thoi_gian_giao_hang,
        kho_giao_nhan,
        don_ton_dong,
    )


if __name__ == "__main__":
    parser = optparse.OptionParser(description="Running mode")
    parser.add_option(
        "-r",
        "--run_date",
        type=str,
        # action="store", dest="run_date",
        # help="run_date string",
        default=f"{datetime.now().strftime('%Y-%m-%d')}",
    )
    options, args = parser.parse_args()
    total_transform(options.run_date, show_logs=True)
