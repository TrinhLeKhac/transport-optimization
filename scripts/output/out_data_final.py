import optparse
import sys
from pathlib import Path

ROOT_PATH = str(Path(__file__).parent.parent.parent)
sys.path.append(ROOT_PATH)

import gc

from scripts.output.out_data_api import assign_supership_carrier, out_data_api
from scripts.utilities.config import *
from scripts.utilities.helper import *

FINAL_FULL_COLS = [
    "order_code",
    "sender_province_code",
    "sender_province",
    "sender_district_code",
    "sender_district",
    "receiver_province_code",
    "receiver_province",
    "receiver_district_code",
    "receiver_district",
    "carrier_id",
    "carrier",
    "order_type",
    "order_type_id",
    "sys_order_type_id",
    "weight",
    "service_fee",
    "delivery_type",
    "carrier_status",
    "carrier_status_comment",
    "estimate_delivery_time_details",
    "estimate_delivery_time",
    "total_order",
    "delivery_success_rate",
    "delivery_success_rate_id",
    "customer_best_carrier_id",
    "partner_best_carrier_id",
    "score",
    "star",
    "cheapest_carrier_id",
    "fastest_carrier_id",
    "highest_score_carrier_id",
]
FINAL_FULL_COLS_RENAMED = [
    "order_code",
    "sender_province_code",
    "sender_province",
    "sender_district_code",
    "sender_district",
    "receiver_province_code",
    "receiver_province",
    "receiver_district_code",
    "receiver_district",
    "carrier_id",
    "carrier",
    "order_type",
    "new_type",
    "route_type",
    "weight",
    "price",
    "pickup_type",
    "status",
    "description",
    "time_data",
    "time_display",
    "total_order",
    "rate",
    "rate_ranking",
    "for_shop",
    "for_partner",
    "score",
    "star",
    "price_ranking",
    "speed_ranking",
    "score_ranking",
]
FINAL_COLS = [
    "order_code",
    "carrier_id",
    "carrier",
    "order_type",
    "order_type_id",
    "sys_order_type_id",
    "service_fee",
    "carrier_status",
    "carrier_status_comment",
    "estimate_delivery_time_details",
    "estimate_delivery_time",
    "total_order",
    "delivery_success_rate",
    "customer_best_carrier_id",
    "partner_best_carrier_id",
    "score",
    "star",
    "cheapest_carrier_id",
    "fastest_carrier_id",
    "highest_score_carrier_id",
]
FINAL_COLS_RENAMED = [
    "order_code",
    "carrier_id",
    "carrier",
    "order_type",
    "new_type",
    "route_type",
    "price",
    "status",
    "description",
    "time_data",
    "time_display",
    "total_order",
    "rate",
    "for_shop",
    "for_partner",
    "score",
    "star",
    "price_ranking",
    "speed_ranking",
    "score_ranking",
]


def combine_info_from_api(
    input_df,
    run_date_str,
    carriers=ACTIVE_CARRIER,
    show_logs=False,
    include_supership=True,
):
    api_data_api = out_data_api(
        run_date_str, carriers=carriers, save_output=False, show_logs=show_logs
    )
    if include_supership:
        api_data_api = assign_supership_carrier(api_data_api, save_output=False)
    api_data_api = api_data_api[
        [
            "receiver_province_code",
            "receiver_district_code",
            "carrier_id",
            "new_type",
            "status",
            "description",
            "time_data",
            "time_display",
            "for_shop",
            "speed_ranking",
            "score_ranking",
            "rate_ranking",
            "rate",
            "score",
            "star",
            "total_order",
        ]
    ]
    api_data_api.columns = [
        "receiver_province_code",
        "receiver_district_code",
        "carrier_id",
        "order_type_id",
        "carrier_status",
        "carrier_status_comment",
        "estimate_delivery_time_details",
        "estimate_delivery_time",
        "customer_best_carrier_id",
        "fastest_carrier_id",
        "highest_score_carrier_id",
        "delivery_success_rate_id",
        "delivery_success_rate",
        "score",
        "star",
        "total_order",
    ]
    result_df = input_df.merge(
        api_data_api,
        on=[
            "receiver_province_code",
            "receiver_district_code",
            "carrier_id",
            "order_type_id",
        ],
        how="left",
    )
    del input_df, api_data_api
    gc.collect()

    return result_df


def calculate_service_fee_old(target_df):

    target_df.loc[target_df["weight"] > 50000, "weight"] = 50000
    target_df["weight"] = target_df["weight"].where(
        target_df["weight"] % 500 == 0, 500 * (target_df["weight"] // 500 + 1)
    )

    cuoc_phi_df = pd.read_parquet(ROOT_PATH + "/processed_data/cuoc_phi.parquet")
    cuoc_phi_df = cuoc_phi_df[
        ["carrier", "order_type", "lt_or_eq", "service_fee"]
    ].rename(columns={"lt_or_eq": "weight"})

    result_df = target_df.merge(
        cuoc_phi_df, on=["carrier", "order_type", "weight"], how="inner"
    )

    del cuoc_phi_df, target_df
    gc.collect()

    # Ninja Van lấy tận nơi cộng cước phí 1,500
    result_df.loc[
        result_df["carrier"].isin(["Ninja Van"])
        & result_df["delivery_type"].isin(["Lấy Tận Nơi"]),
        "service_fee",
    ] = (
        result_df["service_fee"] + 1500
    )

    # GHN lấy tận nơi cộng cước phí 1,000
    result_df.loc[
        result_df["carrier"].isin(["GHN"])
        & result_df["delivery_type"].isin(["Lấy Tận Nơi"]),
        "service_fee",
    ] = (
        result_df["service_fee"] + 1000
    )

    return result_df


def calculate_service_fee(target_df, carriers):

    target_df.loc[target_df["weight"] > 50000, "weight"] = 50000
    target_df["weight"] = target_df["weight"].where(
        target_df["weight"] % 500 == 0, 500 * (target_df["weight"] // 500 + 1)
    )

    cuoc_phi_df = pd.read_parquet(ROOT_PATH + "/processed_data/cuoc_phi.parquet")
    cuoc_phi_df = cuoc_phi_df[
        ["carrier", "order_type", "lt_or_eq", "service_fee"]
    ].rename(columns={"lt_or_eq": "weight"})

    result_dfs = []
    for carrier in carriers:
        carrier_df = target_df[target_df["carrier"] == carrier]
        carrier_df = carrier_df.drop("carrier", axis=1)

        # Merge with cuoc_phi_df specific to carrier
        carrier_result_df = carrier_df.merge(
            cuoc_phi_df[cuoc_phi_df["carrier"] == carrier],
            on=["order_type", "weight"],
            how="inner",
        )

        # Apply additional fees based on carrier and delivery type
        if carrier == "Ninja Van":
            carrier_result_df.loc[
                carrier_result_df["delivery_type"] == "Lấy Tận Nơi", "service_fee"
            ] = (carrier_result_df["service_fee"] + 1500)

        elif carrier == "GHN":
            carrier_result_df.loc[
                carrier_result_df["delivery_type"] == "Lấy Tận Nơi", "service_fee"
            ] = (carrier_result_df["service_fee"] + 1000)

        result_dfs.append(carrier_result_df)

        # Clean up memory
        del carrier_df, carrier_result_df
        gc.collect()

    # Concatenate all carrier-specific results
    result_df = pd.concat(result_dfs, ignore_index=True)

    # Further cleanup
    del result_dfs
    gc.collect()

    return result_df


def calculate_notification(result_df):

    result_df["cheapest_carrier_id"] = result_df.groupby("order_code")[
        "service_fee"
    ].rank(method="dense", ascending=True)
    result_df["cheapest_carrier_id"] = result_df["cheapest_carrier_id"].astype(int)

    return result_df


def partner_best_carrier(data_api_df):
    data_api_df["wscore"] = (
        data_api_df["cheapest_carrier_id"] * 1.4
        + data_api_df["delivery_success_rate_id"] * 1.2
        + data_api_df["highest_score_carrier_id"]
    )
    data_api_df["partner_best_carrier_id"] = (
        data_api_df.groupby(["order_code"])["wscore"]
        .rank(method="dense", ascending=True)
        .astype(int)
    )

    return data_api_df.drop(["wscore"], axis=1)


@exception_wrapper
def out_data_final(
    run_date_str, carriers=ACTIVE_CARRIER, show_logs=False, include_supership=True
):
    final_df = pd.read_parquet(
        ROOT_PATH + "/processed_data/order.parquet",
        columns=[
            "order_code",
            "weight",
            "delivery_type",
            "sender_province",
            "sender_district",
            "sender_province_code",
            "sender_district_code",
            "receiver_province",
            "receiver_district",
            "receiver_province_code",
            "receiver_district_code",
            "order_type",
            "order_type_id",
            "sys_order_type_id",
        ],
    )

    print("Số dòng input dữ liệu: ", len(final_df))

    if include_supership:
        final_df = final_df.merge(
            pd.DataFrame(data={"carrier": carriers + ["SuperShip"]}), how="cross"
        )
    else:
        final_df = final_df.merge(pd.DataFrame(data={"carrier": carriers}), how="cross")

    final_df["carrier_id"] = final_df["carrier"].map(MAPPING_CARRIER_ID)

    final_df = final_df[
        [
            "order_code",
            "weight",
            "delivery_type",
            "sender_province",
            "sender_district",
            "sender_province_code",
            "sender_district_code",
            "receiver_province",
            "receiver_district",
            "receiver_province_code",
            "receiver_district_code",
            "carrier",
            "carrier_id",
            "order_type",
            "order_type_id",
            "sys_order_type_id",
        ]
    ]
    final_df["delivery_type"] = final_df["delivery_type"].fillna("Gửi Bưu Cục")
    final_df["order_type_id"] = final_df["order_type_id"].astype(str)
    final_df["sys_order_type_id"] = final_df["sys_order_type_id"].astype(str)
    final_df = final_df.dropna(how="any")

    print("i. Gắn thông tin tính toán từ API")
    final_df = combine_info_from_api(
        final_df,
        run_date_str,
        carriers=carriers,
        show_logs=show_logs,
        include_supership=include_supership,
    )

    print("ii. Tính phí dịch vụ")
    # Thêm phân vùng mới 'Liên Thành' cho đúng Ninja Van
    # Bảng cước phí cập nhật giá đủ 11 phân vùng => effect chỉ mỗi Ninja Van
    final_df.loc[
        (final_df["carrier_id"] == 7)
        & (
            (
                (final_df["sender_province_code"] == "01")
                & (final_df["receiver_province_code"] == "79")
            )
            | (
                (final_df["sender_province_code"] == "79")
                & (final_df["receiver_province_code"] == "01")
            )
        ),
        "order_type",
    ] = "Liên Thành"

    final_df = calculate_service_fee(final_df, carriers)

    print("iii. Tính ranking nhà vận chuyển theo tiêu chí rẻ nhất")
    final_df = calculate_notification(final_df)

    print("iv. Tính nhà vận chuyển tốt nhất cho đối tác")
    final_df = partner_best_carrier(final_df)

    print("v. Lưu data tính toán...")
    final_df = final_df[FINAL_COLS]  # FINAL_FULL_COLS
    final_df.columns = FINAL_COLS_RENAMED  # FINAL_FULL_COLS_RENAMED
    print("Shape: ", final_df.shape)

    if not os.path.exists(ROOT_PATH + "/output"):
        os.makedirs(ROOT_PATH + "/output")
    final_df.to_parquet(ROOT_PATH + "/output/data_visualization.parquet", index=False)

    del final_df
    gc.collect()

    print("-" * 100)


def _get_data_viz(target_df, threshold=0.6):
    good_df = (
        target_df.loc[target_df["score"] >= threshold]
        .sort_values(["order_code", "price"], ascending=[True, True])
        .drop_duplicates("order_code", keep="first")
    )
    good_df["quality"] = "good"
    bad_df = (
        target_df.loc[target_df["score"] < threshold]
        .sort_values(["order_code", "score"], ascending=[True, False])
        .drop_duplicates("order_code", keep="first")
    )
    bad_filter_df = bad_df.loc[~bad_df["order_code"].isin(good_df["order_code"])]
    bad_filter_df["quality"] = "bad"

    print(f"n_order >= threshold: {len(good_df)}")
    print(f"n_order < threshold: {len(bad_filter_df)}")

    result_df = pd.concat([good_df, bad_filter_df], ignore_index=True)

    # 1. Data viz_1
    monetary = result_df["price"].sum()

    err_df = result_df.loc[result_df["status"].isin(["1", "2"])]
    err_df["error_type"] = err_df["description"].str.split(r" \+ ")
    err_df = err_df.explode("error_type")
    analyze_df1 = (
        err_df.groupby(["carrier", "error_type", "order_type"])["order_code"]
        .count()
        .rename("n_errors")
        .reset_index()
    )

    analyze_df1["score"] = threshold
    analyze_df1["monetary"] = monetary
    analyze_df1["n_good_order"] = len(good_df)
    analyze_df1["n_bad_order"] = len(bad_filter_df)
    analyze_df1["total_error"] = len(err_df)
    analyze_df1 = analyze_df1[
        [
            "score",
            "monetary",
            "n_good_order",
            "n_bad_order",
            "total_error",
            "carrier",
            "error_type",
            "order_type",
            "n_errors",
        ]
    ]
    # 2. Data viz_2
    analyze_df2 = (
        result_df.groupby(["carrier", "quality"])
        .agg(n_orders=("order_code", "count"), monetary=("price", "sum"))
        .reset_index()
    )
    analyze_df2["score"] = threshold
    analyze_df2 = analyze_df2[["score", "carrier", "quality", "n_orders", "monetary"]]
    return analyze_df1, analyze_df2


@exception_wrapper
def get_data_viz():

    target_df = pd.read_parquet(ROOT_PATH + "/output/data_visualization.parquet")

    # Thay đổi lại khi range score change từ [0-1] -> [0-5]
    thresholds = np.linspace(2.5, 5, 101)
    analyze_df1_list = []
    analyze_df2_list = []

    for th in thresholds:
        print("Threshold: ", th)
        analyze_df1, analyze_df2 = _get_data_viz(target_df, th)
        analyze_df1_list.append(analyze_df1)
        analyze_df2_list.append(analyze_df2)
        print("-" * 100)
    total_analyze_df1 = pd.concat(analyze_df1_list, ignore_index=True)
    total_analyze_df2 = pd.concat(analyze_df2_list, ignore_index=True)

    total_analyze_df1.to_parquet(
        ROOT_PATH + "/output/st_data_visualization_p1.parquet", index=False
    )
    total_analyze_df2.to_parquet(
        ROOT_PATH + "/output/st_data_visualization_p2.parquet", index=False
    )


def find_intersection(x1, y1, x2, y2, x3, y3, x4, y4):
    """
    the first line is defined by the line between point1(x1, y1) and point2(x2, y2)
    the first line is defined by the line between point3(x3, y3) and point4(x4, y4)
    """
    px = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / (
        (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    )
    py = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / (
        (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    )
    return px, py


@exception_wrapper
def get_optimal_point(run_date_str, delta=0.9, step=2):
    input_df = pd.read_parquet(
        ROOT_PATH + "/output/st_data_visualization_p1.parquet",
        columns=["score", "monetary", "total_error"],
    )
    target_df = input_df.drop_duplicates().reset_index(drop=True)

    optimal_point = -1
    error_max = target_df["total_error"].max()
    error_min = target_df["total_error"].min()

    monetary_max = target_df["monetary"].max()
    monetary_min = target_df["monetary"].min()

    monetary_range = monetary_max - monetary_min
    error_range = error_max - error_min
    scale = monetary_range / error_range

    score = 2.75
    for idx in range(len(target_df) - step):
        # print(idx)
        # (x - amin)/(amax - amin) = (y - bmin)/(bmax - bmin)
        # x - amin = (y - bmin)/scale
        # x = (y - bmin)/scale + amin
        point1 = (
            target_df.loc[idx, "score"],
            (target_df.loc[idx, "monetary"] - monetary_min) / scale + error_min,
        )
        point2 = (
            target_df.loc[idx + step, "score"],
            (target_df.loc[idx + step, "monetary"] - monetary_min) / scale + error_min,
        )
        point3 = (target_df.loc[idx, "score"], target_df.loc[idx, "total_error"])
        point4 = (
            target_df.loc[idx + step, "score"],
            target_df.loc[idx + step, "total_error"],
        )

        R = find_intersection(*point1, *point2, *point3, *point4)

        # print(point1, point2, point3, point4, idx, R)

        if (R[0] >= target_df.loc[idx, "score"]) and (
            R[0] <= target_df.loc[idx + step, "score"]
        ):
            optimal_point = idx + step // 2
            score = target_df.loc[optimal_point, "score"] - delta
            score = round(score, 3)
            print(">>> FOUND OPTIMAL SCORE !!!")
            break
    print("Optimal score: ", score)
    try:
        total_score_df = pd.read_parquet(
            ROOT_PATH + "/output/total_optimal_score.parquet"
        )
    except:
        total_score_df = pd.DataFrame(columns=["score", "date"])
    tmp_df = pd.DataFrame(data={"score": [score], "date": [run_date_str]})
    total_score_df = pd.concat([total_score_df, tmp_df]).drop_duplicates(
        "date", keep="last"
    )
    total_score_df.to_parquet(
        ROOT_PATH + "/output/total_optimal_score.parquet", index=False
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
    # parser.add_option(
    #     '-d', '--delta',
    #     type=float,
    #     # action="store", dest="delta",
    #     # help="delta float",
    #     default=0.9
    # )
    options, args = parser.parse_args()

    # print(options.delta)
    # print(type(options.delta))

    include_supership = False
    if include_supership:
        print("Out data visualization and assigning SuperShip carrier...")
    else:
        print("Out data visualization...")
    out_data_final(
        run_date_str=options.run_date,
        carriers=ACTIVE_CARRIER,
        show_logs=False,
        include_supership=include_supership,
    )
    get_data_viz()
    get_optimal_point(run_date_str=options.run_date, delta=DELTA, step=2)
