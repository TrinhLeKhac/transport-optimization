from scripts.utilities.config import *
from scripts.utilities.helper import *


@exception_wrapper
def transform_data_ngung_giao_nhan():

    # Đọc data ngưng giao nhận
    ngung_giao_nhan_df = pd.read_parquet(
        ROOT_PATH + "/processed_data/ngung_giao_nhan.parquet"
    )

    ngung_giao_nhan_df.loc[ngung_giao_nhan_df["status"].isna(), "status"] = (
        "Bình thường"
    )
    ngung_giao_nhan_df.loc[ngung_giao_nhan_df["status"] != "Bình thường", "status"] = (
        "Quá tải"
    )

    ngung_giao_nhan_df = PROVINCE_MAPPING_DISTRICT_CROSS_CARRIER_DF.merge(
        ngung_giao_nhan_df,
        on=["receiver_province", "receiver_district", "carrier"],
        how="left",
    )

    ngung_giao_nhan_df["carrier_id"] = ngung_giao_nhan_df["carrier"].map(
        MAPPING_CARRIER_ID
    )

    ngung_giao_nhan_df["sender_province"] = ngung_giao_nhan_df["receiver_province"]
    ngung_giao_nhan_df["sender_district"] = ngung_giao_nhan_df["receiver_district"]

    ngung_giao_nhan_df = ngung_giao_nhan_df.merge(
        PROVINCE_MAPPING_DISTRICT_DF.rename(
            columns={
                "province": "sender_province",
                "district": "sender_district",
                "province_code": "sender_province_code",
                "district_code": "sender_district_code",
            }
        ),
        on=["sender_province", "sender_district"],
        how="left",
    ).merge(
        PROVINCE_MAPPING_DISTRICT_DF.rename(
            columns={
                "province": "receiver_province",
                "district": "receiver_district",
                "province_code": "receiver_province_code",
                "district_code": "receiver_district_code",
            }
        ),
        on=["receiver_province", "receiver_district"],
        how="left",
    )

    ngung_giao_nhan_df["status"] = ngung_giao_nhan_df["status"].fillna("Bình thường")
    ngung_giao_nhan_df["score"] = ngung_giao_nhan_df["status"].map(
        TRONG_SO["Ngưng giao nhận"]["Phân loại"]
    )
    ngung_giao_nhan_df["criteria"] = "Ngưng giao nhận"
    ngung_giao_nhan_df["criteria_weight"] = TRONG_SO["Ngưng giao nhận"]["Tiêu chí"]

    database_df = ngung_giao_nhan_df[
        [
            "sender_province_code",
            "sender_district_code",
            "receiver_province_code",
            "receiver_district_code",
            "carrier_id",
            "status",
        ]
    ]
    return_df = ngung_giao_nhan_df[
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

    database_df.to_parquet(
        ROOT_PATH + "/transform/ngung_giao_nhan.parquet", index=False
    )

    return return_df


@exception_wrapper
def transform_data_ngung_giao_nhan_level_3():

    # Đọc data ngưng giao nhận
    ngung_giao_nhan_df = pd.read_parquet(
        ROOT_PATH + "/processed_data/ngung_giao_nhan_level_3.parquet"
    )

    ngung_giao_nhan_df.loc[ngung_giao_nhan_df["status"].isna(), "status"] = (
        "Bình thường"
    )
    ngung_giao_nhan_df.loc[ngung_giao_nhan_df["status"] != "Bình thường", "status"] = (
        "Quá tải"
    )

    ngung_giao_nhan_df = PROVINCE_MAPPING_DISTRICT_MAPPING_WARD_CROSS_CARRIER_DF.merge(
        ngung_giao_nhan_df,
        on=["receiver_province", "receiver_district", "receiver_commune", "carrier"],
        how="left",
    )

    ngung_giao_nhan_df["carrier_id"] = ngung_giao_nhan_df["carrier"].map(
        MAPPING_CARRIER_ID
    )

    ngung_giao_nhan_df = ngung_giao_nhan_df.merge(
        PROVINCE_MAPPING_DISTRICT_MAPPING_WARD_DF.rename(
            columns={
                "province": "receiver_province",
                "district": "receiver_district",
                "commune": "receiver_commune",
                "province_code": "receiver_province_code",
                "district_code": "receiver_district_code",
                "commune_code": "receiver_commune_code",
            }
        ),
        on=["receiver_province", "receiver_district", "receiver_commune"],
        how="left",
    )
    ngung_giao_nhan_df["status"] = ngung_giao_nhan_df["status"].fillna("Bình thường")

    database_df = ngung_giao_nhan_df[
        [
            "receiver_province_code",
            "receiver_district_code",
            "receiver_commune_code",
            "carrier_id",
            "status",
        ]
    ]

    database_df.to_parquet(
        ROOT_PATH + "/transform/ngung_giao_nhan_level_3.parquet", index=False
    )
