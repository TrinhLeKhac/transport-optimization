from scripts.output.out_data_final import *
from pydantic import BaseModel, conint, constr, confloat
from scripts.auth.security import validate_token
from fastapi import Depends
from fastapi import APIRouter
from scripts.database.helper import *

router = APIRouter()


class RequestModel(BaseModel):
    sender_province: constr(strict=True)
    sender_district: constr(strict=True)
    receiver_province: constr(strict=True)
    receiver_district: constr(strict=True)
    weight: conint(strict=True)
    pickup: constr(strict=True)


class ResultModel(BaseModel):
    # order_code: constr(strict=True)
    carrier_id: conint(strict=True)
    # new_type: conint(strict=True)
    route_type: constr(strict=True)
    price: conint(strict=True)
    status: constr(strict=True)
    description: constr(strict=True)
    time_data: confloat(strict=True)
    time_display: constr(strict=True)
    rate: confloat(strict=True)
    score: confloat(strict=True)
    star: confloat(strict=True)
    for_shop: conint(strict=True)
    for_partner: conint(strict=True)
    price_ranking: conint(strict=True)
    speed_ranking: conint(strict=True)
    score_ranking: conint(strict=True)

    class Config:
        orm_mode = True


@router.post("", dependencies=[Depends(validate_token)])
def calculate(data: RequestModel):

    sender_province = data.sender_province
    sender_district = data.sender_district
    receiver_province = data.receiver_province
    receiver_district = data.receiver_district
    weight = data.weight
    pickup = data.pickup

    pickup_type = None
    if pickup == "0":
        pickup_type = "Gửi Bưu Cục"
    elif pickup == "1":
        pickup_type = "Lấy Tận Nơi"

    df_input = pd.DataFrame(data={
        "order_id": ["order"],
        "weight": [weight],
        "delivery_type": [pickup_type],
        "sender_province_id": [sender_province],
        "sender_district_id": [sender_district],
        "receiver_province_id": [receiver_province],
        "receiver_district_id": [receiver_district],
    })
    df_output = out_data_final(df_input, show_logs=False)
    df_output = df_output[[
        # "order_code",
        "carrier_id",
        # "new_type",
        "route_type",
        "price",
        "status",
        "description",
        "time_data",
        "time_display",
        "rate",
        "score",
        "star",
        "for_shop",
        "for_partner",
        "price_ranking",
        "speed_ranking",
        "score_ranking",

    ]]
    df_output["route_type"] = df_output["route_type"].astype(str)
    df_output["status"] = df_output["status"].astype(str)

    result_dict_list = []
    for i in range(len(df_output)):
        result_dict = {
            # "order_code": df_output.loc[i, :]["order_code"],
            "carrier_id": df_output.loc[i, :]["carrier_id"],
            # "new_type": df_output.loc[i, :]["new_type"],
            "route_type": df_output.loc[i, :]["route_type"],
            "price": df_output.loc[i, :]["price"],
            "status": df_output.loc[i, :]["status"],
            "description": df_output.loc[i, :]["description"],
            "time_data": df_output.loc[i, :]["time_data"],
            "time_display": df_output.loc[i, :]["time_display"],
            "rate": df_output.loc[i, :]["rate"],
            "score": df_output.loc[i, :]["score"],
            "star": df_output.loc[i, :]["star"],
            "for_shop": df_output.loc[i, :]["for_shop"],
            "for_partner": df_output.loc[i, :]["for_partner"],
            "price_ranking": df_output.loc[i, :]["price_ranking"],
            "speed_ranking": df_output.loc[i, :]["speed_ranking"],
            "score_ranking": df_output.loc[i, :]["score_ranking"],

        }

        result_dict_list.append(ResultModel(**result_dict))

    return {
        "error": False,
        "message": "",
        "data": result_dict_list
    }
