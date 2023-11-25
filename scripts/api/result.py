from scripts.output.out_data_final import *
from pydantic import BaseModel
from scripts.auth.security import validate_token
from fastapi import Depends
from fastapi import APIRouter
router = APIRouter()


class ResultModel(BaseModel):
    # order_code: str
    carrier_id: int
    # new_type: int
    route_type: str
    price: int
    status: str
    description: str
    time_data: float
    time_display: str
    rate: float
    score: float
    star: float
    for_shop: int
    for_partner: int
    price_ranking: int
    speed_ranking: int
    score_ranking: int

    class Config:
        orm_mode = True


@router.post("", dependencies=[Depends(validate_token)])
def calculate(
        sender_province: str, sender_district: str,
        receiver_province: str, receiver_district: str,
        weight: int, pickup: str,
):
    pickup_type = None
    if pickup == "0":
        pickup_type = 'Gửi Bưu Cục'
    elif pickup == "1":
        pickup_type = 'Lấy Tận Nơi'

    df_input = pd.DataFrame(data={
        'order_id': ['order'],
        'weight': [weight],
        'delivery_type': [pickup_type],
        'sender_province_id': [sender_province],
        'sender_district_id': [sender_district],
        'receiver_province_id': [receiver_province],
        'receiver_district_id': [receiver_district],
    })
    df_output = out_data_final(df_input, show_logs=False)
    df_output = df_output[[
        # 'order_code',
        'carrier_id',
        # 'new_type',
        'route_type',
        'price',
        'status',
        'description',
        'time_data',
        'time_display',
        'rate',
        'score',
        'star',
        'for_shop',
        'for_partner',
        'price_ranking',
        'speed_ranking',
        'score_ranking',

    ]]
    df_output['route_type'] = df_output['route_type'].astype(str)
    df_output['status'] = df_output['status'].astype(str)

    final_list = []
    for i in range(len(df_output)):
        result_dict = {
            # 'order_code': df_output.loc[i, :]['order_code'],
            'carrier_id': df_output.loc[i, :]['carrier_id'],
            # 'new_type': df_output.loc[i, :]['new_type'],
            'route_type': df_output.loc[i, :]['route_type'],
            'price': df_output.loc[i, :]['price'],
            'status': df_output.loc[i, :]['status'],
            'description': df_output.loc[i, :]['description'],
            'time_data': df_output.loc[i, :]['time_data'],
            'time_display': df_output.loc[i, :]['time_display'],
            'rate': df_output.loc[i, :]['rate'],
            'score': df_output.loc[i, :]['score'],
            'star': df_output.loc[i, :]['star'],
            'for_shop': df_output.loc[i, :]['for_shop'],
            'for_partner': df_output.loc[i, :]['for_partner'],
            'price_ranking': df_output.loc[i, :]['price_ranking'],
            'speed_ranking': df_output.loc[i, :]['speed_ranking'],
            'score_ranking': df_output.loc[i, :]['score_ranking'],

        }

        final_list.append(ResultModel(**result_dict))

    return {
        'error': False,
        'message': '',
        'data': final_list
    }
