from scripts.utilities.config import *
from scripts.utilities.helper import *


def idx_tieu_chi_3(nvc_df, delivery_success_rate_col="modified_delivery_success_rate"):
    list_idx = nvc_df.index.tolist()[:10]  # top 10 after ordering
    th1 = nvc_df.loc[list_idx[-1], delivery_success_rate_col]
    th2 = nvc_df.loc[list_idx[-1], "total_order"]

    extra_idx = nvc_df.loc[
        (nvc_df[delivery_success_rate_col] == th1) & (nvc_df["total_order"] == th2)
    ].index.tolist()

    return list_idx + extra_idx


def _get_delivery_success_rate(df_order):
    hoan_hang = (
        df_order[df_order["carrier_status"].isin(HOAN_HANG_STATUS)]
        .groupby(["receiver_province", "receiver_district", "carrier"])["order_code"]
        .count()
        .rename("total_failed_order")
        .reset_index()
    )
    tong_don = (
        df_order.groupby(["receiver_province", "receiver_district", "carrier"])[
            "order_code"
        ]
        .count()
        .rename("total_order")
        .reset_index()
    )
    ti_le_giao_hang = hoan_hang.merge(
        tong_don, on=["receiver_province", "receiver_district", "carrier"], how="right"
    )
    ti_le_giao_hang["total_failed_order"] = (
        ti_le_giao_hang["total_failed_order"].fillna(0).astype(int)
    )
    ti_le_giao_hang["delivery_success_rate"] = (
        1 - ti_le_giao_hang["total_failed_order"] / ti_le_giao_hang["total_order"]
    )

    return ti_le_giao_hang[
        ["receiver_province", "receiver_district", "carrier", "delivery_success_rate"]
    ]


@exception_wrapper
def get_delivery_success_rate(df_order, run_date, n_days_back=30):

    nstep = n_days_back // 3

    df_order1 = df_order.loc[
        df_order["created_at"] >= (run_date - timedelta(days=nstep))
    ]
    df_order2 = df_order.loc[
        (df_order["created_at"] >= (run_date - timedelta(days=2 * nstep)))
        & (df_order["created_at"] < (run_date - timedelta(days=nstep)))
    ]
    df_order3 = df_order.loc[
        (df_order["created_at"] >= (run_date - timedelta(days=3 * nstep)))
        & (df_order["created_at"] < (run_date - timedelta(days=2 * nstep)))
    ]
    assert len(df_order1) + len(df_order2) + len(df_order3) == len(
        df_order
    ), "Ops, something wrong!"

    result_df1 = _get_delivery_success_rate(df_order1)
    result_df1.columns = [
        "receiver_province",
        "receiver_district",
        "carrier",
        "delivery_success_rate1",
    ]

    result_df2 = _get_delivery_success_rate(df_order2)
    result_df2.columns = [
        "receiver_province",
        "receiver_district",
        "carrier",
        "delivery_success_rate2",
    ]

    result_df3 = _get_delivery_success_rate(df_order3)
    result_df3.columns = [
        "receiver_province",
        "receiver_district",
        "carrier",
        "delivery_success_rate3",
    ]

    result_df = (
        result_df1.merge(
            result_df2,
            on=["receiver_province", "receiver_district", "carrier"],
            how="outer",
        )
        .merge(
            result_df3,
            on=["receiver_province", "receiver_district", "carrier"],
            how="outer",
        )
        .fillna(0)
    )
    result_df["delivery_success_rate"] = (
        result_df["delivery_success_rate1"] * 1.5
        + result_df["delivery_success_rate2"] * 1.2
        + result_df["delivery_success_rate3"]
    ) / (
        1.5 * np.where(result_df["delivery_success_rate1"], 1, 0)
        + 1.2 * np.where(result_df["delivery_success_rate2"], 1, 0)
        + 1 * np.where(result_df["delivery_success_rate3"], 1, 0)
    )
    result_df["delivery_success_rate"] = result_df["delivery_success_rate"].fillna(0)

    return result_df


def score_ti_le_giao_hang(tong_don, ti_le_thanh_cong):
    # group 1
    if (tong_don >= 30) and (ti_le_thanh_cong > 0.95):
        return (
            "Tổng đơn hàng từ 30 đơn trở lên và có tỷ lệ giao hàng thành công trên 95%"
        )
    elif (tong_don >= 20) and (ti_le_thanh_cong > 0.95):
        return (
            "Tổng đơn hàng từ 20 đơn trở lên và có tỷ lệ giao hàng thành công trên 95%"
        )
    elif (tong_don >= 10) and (ti_le_thanh_cong > 0.95):
        return (
            "Tổng đơn hàng từ 10 đơn trở lên và có tỷ lệ giao hàng thành công trên 95%"
        )
    # group 2
    elif (tong_don >= 30) and (ti_le_thanh_cong > 0.9):
        return (
            "Tổng đơn hàng từ 30 đơn trở lên và có tỷ lệ giao hàng thành công trên 90%"
        )
    elif (tong_don >= 20) and (ti_le_thanh_cong > 0.9):
        return (
            "Tổng đơn hàng từ 20 đơn trở lên và có tỷ lệ giao hàng thành công trên 90%"
        )
    elif (tong_don >= 10) and (ti_le_thanh_cong > 0.9):
        return (
            "Tổng đơn hàng từ 10 đơn trở lên và có tỷ lệ giao hàng thành công trên 90%"
        )
    # group 3
    elif (tong_don >= 5) and (ti_le_thanh_cong > 0.95):
        return (
            "Tổng đơn hàng từ 5 đơn trở lên và có tỷ lệ giao hàng thành công trên 95%"
        )
    elif (tong_don >= 5) and (ti_le_thanh_cong > 0.9):
        return (
            "Tổng đơn hàng từ 5 đơn trở lên và có tỷ lệ giao hàng thành công trên 90%"
        )
    elif (tong_don >= 5) and (ti_le_thanh_cong > 0.85):
        return (
            "Tổng đơn hàng từ 5 đơn trở lên và có tỷ lệ giao hàng thành công trên 85%"
        )
    elif (tong_don >= 5) and (ti_le_thanh_cong > 0.75):
        return (
            "Tổng đơn hàng từ 5 đơn trở lên và có tỷ lệ giao hàng thành công trên 75%"
        )
    elif (tong_don >= 5) and (ti_le_thanh_cong > 0.5):
        return (
            "Tổng đơn hàng từ 5 đơn trở lên và có tỷ lệ giao hàng thành công trên 50%"
        )
    elif ti_le_thanh_cong == -1:
        return "Tổng đơn hàng từ 10 đơn trở lên và có tỷ lệ hoàn từ 25% trở lên"
    elif ti_le_thanh_cong == -2:
        return "Tổng đơn hàng từ 4 đơn trở lên và có tỷ lệ hoàn từ 50% trở lên"
    elif ti_le_thanh_cong == -3:
        return "TOP 10 KHU VỰC có số lượng đơn hàng từ 3 đơn trở lên và có tỷ lệ hoàn hơn 20%"
    elif ti_le_thanh_cong == -4:
        return "Không có thông tin"
    else:
        return "Trường hợp khác"


@exception_wrapper
def transform_data_ti_le_giao_hang(run_date_str, n_days_back=30):
    run_date = datetime.strptime(run_date_str, "%Y-%m-%d")
    print(run_date)
    # 1. Đọc thông tin giao dịch valid
    df_order = pd.read_parquet(ROOT_PATH + "/processed_data/order.parquet")
    df_order = df_order.loc[
        df_order["created_at"] >= (run_date - timedelta(days=n_days_back))
    ]
    df_order = df_order[
        df_order["carrier_status"].isin(THANH_CONG_STATUS + HOAN_HANG_STATUS)
    ]

    # 2.1 Transform data hoàn hàng
    hoan_hang = (
        df_order[df_order["carrier_status"].isin(HOAN_HANG_STATUS)]
        .groupby(["receiver_province", "receiver_district", "carrier"])["order_code"]
        .count()
        .rename("total_failed_order")
        .reset_index()
    )

    tong_don = (
        df_order.groupby(["receiver_province", "receiver_district", "carrier"])[
            "order_code"
        ]
        .count()
        .rename("total_order")
        .reset_index()
    )

    ti_le_giao_hang = hoan_hang.merge(
        tong_don, on=["receiver_province", "receiver_district", "carrier"], how="right"
    )
    ti_le_giao_hang["total_failed_order"] = (
        ti_le_giao_hang["total_failed_order"].fillna(0).astype(int)
    )
    # ti_le_giao_hang['delivery_success_rate'] = 1 - ti_le_giao_hang['total_failed_order'] / ti_le_giao_hang['total_order']
    # ti_le_giao_hang['modified_delivery_success_rate'] = ti_le_giao_hang['delivery_success_rate']

    # 2.2 Tính tỉ lệ giao hàng có trọng sô
    result_df = get_delivery_success_rate(df_order, run_date)

    ti_le_giao_hang = ti_le_giao_hang.merge(
        result_df[
            [
                "receiver_province",
                "receiver_district",
                "carrier",
                "delivery_success_rate",
            ]
        ],
        on=["receiver_province", "receiver_district", "carrier"],
        how="left",
    )
    ti_le_giao_hang["modified_delivery_success_rate"] = ti_le_giao_hang[
        "delivery_success_rate"
    ]

    # 3.1 Tiêu chí loại 1
    condition1 = (ti_le_giao_hang["total_order"] >= 10) & (
        1 - ti_le_giao_hang["modified_delivery_success_rate"] >= 0.25
    )
    # 3.2 Tiêu chí loại 2
    condition2 = (ti_le_giao_hang["total_order"] >= 4) & (
        1 - ti_le_giao_hang["modified_delivery_success_rate"] >= 0.5
    )
    ti_le_giao_hang.loc[condition1, "modified_delivery_success_rate"] = (
        -1
    )  # loại theo tiêu chí 1
    ti_le_giao_hang.loc[condition2, "modified_delivery_success_rate"] = (
        -2
    )  # loại theo tiêu chí 2

    # 3.3 Tiêu chí loại 3
    # # Loại top 10 khu vực có số đơn hàng >= 3 đơn + tỷ lệ hoàn > 20% (đã loại trừ tiêu chí 1, 2) theo từng nhà vận chuyển
    # # top 10 chọn theo tiêu chí tổng đơn (nhiều) + tỉ lệ giao hàng thành công (ít)
    filter_df = ti_le_giao_hang.loc[
        ~ti_le_giao_hang["modified_delivery_success_rate"].isin([-1, -2])
        & ((1 - ti_le_giao_hang["modified_delivery_success_rate"]) > 0.2)
        & (ti_le_giao_hang["total_order"] >= 3)
    ].sort_values(
        ["carrier", "total_order", "modified_delivery_success_rate"],
        ascending=[True, False, True],
    )[
        ["carrier", "total_order", "modified_delivery_success_rate"]
    ]

    total_remove_idx = []
    for carrier in filter_df["carrier"].unique().tolist():
        carrier_df = filter_df.loc[filter_df["carrier"] == carrier]
        tmp_remove_idx = idx_tieu_chi_3(carrier_df)
        total_remove_idx.extend(tmp_remove_idx)

    ti_le_giao_hang.loc[total_remove_idx, "modified_delivery_success_rate"] = -3

    # 4. Tính status + score
    ti_le_giao_hang["status"] = ti_le_giao_hang.apply(
        lambda x: score_ti_le_giao_hang(
            x["total_order"], x["modified_delivery_success_rate"]
        ),
        axis=1,
    )
    ti_le_giao_hang = PROVINCE_MAPPING_DISTRICT_CROSS_CARRIER_DF.merge(
        ti_le_giao_hang,
        on=["receiver_province", "receiver_district", "carrier"],
        how="left",
    )
    ti_le_giao_hang["total_failed_order"] = (
        ti_le_giao_hang["total_failed_order"].fillna(0).astype(int)
    )
    ti_le_giao_hang["total_order"] = (
        ti_le_giao_hang["total_order"].fillna(0).astype(int)
    )
    ti_le_giao_hang["delivery_success_rate"] = ti_le_giao_hang[
        "delivery_success_rate"
    ].fillna(0)
    ti_le_giao_hang["modified_delivery_success_rate"] = ti_le_giao_hang[
        "modified_delivery_success_rate"
    ].fillna(0)
    ti_le_giao_hang["status"] = ti_le_giao_hang["status"].fillna("Không có thông tin")
    ti_le_giao_hang["score"] = ti_le_giao_hang["status"].map(
        TRONG_SO["Tỉ lệ giao hàng"]["Phân loại"]
    )
    ti_le_giao_hang["criteria"] = "Tỉ lệ giao hàng"
    ti_le_giao_hang["criteria_weight"] = TRONG_SO["Tỉ lệ giao hàng"]["Tiêu chí"]

    ti_le_giao_hang = ti_le_giao_hang[
        [
            "receiver_province",
            "receiver_district",
            "carrier",
            "total_failed_order",
            "total_order",
            "delivery_success_rate",
            "status",
            "score",
            "criteria",
            "criteria_weight",
        ]
    ]
    ti_le_giao_hang.to_parquet(
        ROOT_PATH + "/transform/ti_le_giao_hang.parquet", index=False
    )

    return ti_le_giao_hang
