from scripts.utilities.config import *
from scripts.utilities.helper import *

BAD_COMMENTS = [
    "Nhân viên không nhiệt tình",
    "Cải thiện thời gian chờ và thời gian giải quyết",
    "Cải thiện thời gian chờ và thời gian giải quyết nhanh hơn",
    "Cải thiện nghiệp vụ",
    "Cải thiện nghiệp vụ hơn",
]


@exception_wrapper
def transform_data_danh_gia_zns():

    # Đọc thông tin data ZNS
    danh_gia_zns = pd.read_parquet(ROOT_PATH + "/processed_data/danh_gia_zns.parquet")

    comment = danh_gia_zns[
        ["receiver_province", "receiver_district", "carrier", "comment"]
    ].explode(column="comment")
    comment = comment.loc[comment["comment"].notna()]
    comment.loc[comment["comment"].isin(BAD_COMMENTS), "comment"] = "Đánh giá xấu"
    comment.loc[comment["comment"] != "Đánh giá xấu", "comment"] = "Đánh giá khác"
    comment = comment.sort_values(["comment"], ascending=False).drop_duplicates(
        ["receiver_province", "receiver_district", "carrier"], keep="first"
    )
    danh_gia_zns = danh_gia_zns.drop("comment", axis=1).merge(
        comment, on=["receiver_province", "receiver_district", "carrier"], how="left"
    )
    danh_gia_zns["comment"] = danh_gia_zns["comment"].fillna("Không có thông tin")

    danh_gia_zns = danh_gia_zns[
        [
            "receiver_province",
            "receiver_district",
            "carrier",
            "comment",
            "n_stars",
            "reviewed_at",
        ]
    ]

    # Tách nhóm loại bỏ
    zns_1_2_sao = (
        danh_gia_zns.loc[danh_gia_zns["n_stars"].isin([1, 2])]
        .groupby(["receiver_province", "receiver_district", "carrier"])["n_stars"]
        .count()
        .reset_index()
        .rename(columns={"n_stars": "so_lan_danh_gia_1_2_sao"})
    )
    zns_total = (
        danh_gia_zns.groupby(["receiver_province", "receiver_district", "carrier"])[
            "n_stars"
        ]
        .count()
        .reset_index()
        .rename(columns={"n_stars": "tong_so_lan_danh_gia"})
    )
    zns_total = zns_total.merge(
        zns_1_2_sao,
        on=["receiver_province", "receiver_district", "carrier"],
        how="left",
    )
    zns_total["so_lan_danh_gia_1_2_sao"] = (
        zns_total["so_lan_danh_gia_1_2_sao"].fillna(0).astype(int)
    )
    zns_total["pct"] = (
        zns_total["so_lan_danh_gia_1_2_sao"] / zns_total["tong_so_lan_danh_gia"]
    )
    zns_loai_bo = zns_total[zns_total["pct"] >= 0.3]
    zns_loai_bo["status"] = "Loại"

    # Filter phần còn lại
    danh_gia_zns_filter1 = merge_left_only(
        danh_gia_zns,
        zns_loai_bo,
        keys=["receiver_province", "receiver_district", "carrier"],
    )

    # Tách nhóm đánh giá 1 sao loại 1
    zns_1_sao_type_1 = danh_gia_zns_filter1.loc[
        (danh_gia_zns_filter1["n_stars"] == 1)
        & (danh_gia_zns_filter1["comment"] == "Đánh giá xấu")
    ][["receiver_province", "receiver_district", "carrier"]].drop_duplicates()
    zns_1_sao_type_1["status"] = "1 sao & Đánh giá xấu"

    # Filter phần còn lại
    danh_gia_zns_filter2 = merge_left_only(
        danh_gia_zns_filter1,
        zns_1_sao_type_1,
        keys=["receiver_province", "receiver_district", "carrier"],
    )

    # Tách nhóm đánh giá 1 sao loại 2
    zns_1_sao_type_2 = (
        danh_gia_zns_filter2.loc[(danh_gia_zns_filter2["n_stars"] == 1)]
        .groupby(["receiver_province", "receiver_district", "carrier"])["n_stars"]
        .count()
        .reset_index()
    )
    zns_1_sao_type_2 = zns_1_sao_type_2.loc[zns_1_sao_type_2["n_stars"] > 1].drop(
        "n_stars", axis=1
    )
    zns_1_sao_type_2["status"] = "Nhiều hơn 1 lần đánh giá 1 sao"

    # Filter phần còn lại
    danh_gia_zns_filter3 = merge_left_only(
        danh_gia_zns_filter2,
        zns_1_sao_type_2,
        keys=["receiver_province", "receiver_district", "carrier"],
    )

    # Tách nhóm đánh giá 5 sao
    zns_5_sao = (
        danh_gia_zns_filter3.loc[danh_gia_zns_filter3["n_stars"].isin([5])]
        .groupby(["receiver_province", "receiver_district", "carrier"])["n_stars"]
        .count()
        .reset_index()
        .rename(columns={"n_stars": "so_lan_danh_gia_5_sao"})
    )
    zns_total_filter3 = (
        danh_gia_zns_filter3.groupby(
            ["receiver_province", "receiver_district", "carrier"]
        )["n_stars"]
        .count()
        .reset_index()
        .rename(columns={"n_stars": "tong_so_lan_danh_gia"})
    )
    zns_total_filter3 = zns_total_filter3.merge(
        zns_5_sao, on=["receiver_province", "receiver_district", "carrier"], how="left"
    )
    zns_total_filter3["so_lan_danh_gia_5_sao"] = (
        zns_total_filter3["so_lan_danh_gia_5_sao"].fillna(0).astype(int)
    )
    zns_total_filter3["pct"] = (
        zns_total_filter3["so_lan_danh_gia_5_sao"]
        / zns_total_filter3["tong_so_lan_danh_gia"]
    )
    zns_5_sao = zns_total_filter3[zns_total_filter3["pct"] >= 0.95]
    zns_5_sao["status"] = "Đánh giá 5 sao trên 95% đơn"

    # Filter phần còn lại
    danh_gia_zns_filter4 = merge_left_only(
        danh_gia_zns_filter3,
        zns_5_sao,
        keys=["receiver_province", "receiver_district", "carrier"],
    )

    # Tách nhóm 1, 2 sao đánh giá gần đây
    max_time = danh_gia_zns["reviewed_at"].max()
    zns_have_1_2_sao_recently = danh_gia_zns_filter4.loc[
        danh_gia_zns_filter4["n_stars"].isin([1, 2])
        & (danh_gia_zns_filter4["reviewed_at"] >= (max_time - timedelta(days=5)))
    ][["receiver_province", "receiver_district", "carrier"]].drop_duplicates()
    zns_have_1_2_sao_recently["status"] = "Đánh giá 1, 2 sao gần đây (<= 5 ngày)"

    danh_gia_zns_filter5 = merge_left_only(
        danh_gia_zns_filter4,
        zns_have_1_2_sao_recently,
        keys=["receiver_province", "receiver_district", "carrier"],
    )

    # chỉ có 4, 5 sao
    only_4_5_sao = danh_gia_zns_filter5.loc[
        danh_gia_zns_filter5["n_stars"].isin([4, 5])
    ][["receiver_province", "receiver_district", "carrier"]].drop_duplicates()
    only_4_5_sao["status"] = "Không phát sinh đánh giá 1, 2, 3 sao"

    # Còn lại
    danh_gia_zns_filter6 = merge_left_only(
        danh_gia_zns_filter5,
        only_4_5_sao,
        keys=["receiver_province", "receiver_district", "carrier"],
    )
    other = danh_gia_zns_filter6[
        ["receiver_province", "receiver_district", "carrier"]
    ].drop_duplicates()
    other["status"] = "Bình thường"

    # Tổng hợp thông tin
    final_zns = pd.concat(
        [
            zns_loai_bo,
            zns_1_sao_type_1,
            zns_1_sao_type_2,
            zns_5_sao,
            zns_have_1_2_sao_recently,
            only_4_5_sao,
            other,
        ]
    )[["receiver_province", "receiver_district", "carrier", "status"]].reset_index(
        drop=True
    )

    # Fill thông tin default
    final_zns = PROVINCE_MAPPING_DISTRICT_CROSS_CARRIER_DF.merge(
        final_zns, on=["receiver_province", "receiver_district", "carrier"], how="left"
    )
    final_zns["status"] = final_zns["status"].fillna("Không có thông tin")
    final_zns["score"] = final_zns["status"].map(TRONG_SO["Đánh giá ZNS"]["Phân loại"])
    final_zns["criteria"] = "Đánh giá ZNS"
    final_zns["criteria_weight"] = TRONG_SO["Đánh giá ZNS"]["Tiêu chí"]

    return final_zns[
        [
            "receiver_province",
            "receiver_district",
            "carrier",
            "status",
            "score",
            "criteria",
            "criteria_weight",
        ]
    ]
