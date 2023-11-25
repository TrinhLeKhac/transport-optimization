from fastapi import FastAPI, status, HTTPException
from pydantic import BaseModel
from scripts.database.database import session
from scripts.database import models
from typing import List
from scripts.api.out_data_final import *
from scripts.auth.token import *
from scripts.auth.security import validate_token
from fastapi import Depends

app = FastAPI(
    title="API SUPERSHIP",
    description="There are APIs getting calculation result from history transactions of SUPERSHIP",
    docs_url="/"
)

db = session()


class LoginRequest(BaseModel):
    username: str
    password: str


class RowAPI(BaseModel):
    id: int
    receiver_province_code: str
    receiver_district_code: str
    carrier_id: int
    new_type: int
    status: int
    description: str
    time_data: float
    time_display: str
    speed_ranking: int
    score_ranking: int
    for_shop: int
    total_order: int
    rate: float
    score: float
    star: float

    # import_date: str

    class Config:
        orm_mode = True


class RowCalc(BaseModel):
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


@app.post('/superai/auth')
def login(request_data: LoginRequest):
    print(f'[x] request_data: {request_data.__dict__}')
    if verify_password(username=request_data.username, password=request_data.password):
        token = generate_token(request_data.username, request_data.password)
        return {
            "error": False,
            "message": "",
            "data": {
                "token": token
            }
        }
    else:
        return {
            "error": True,
            "message": "User not found",
            "data": {
                "token": "Invalid"
            }
        }


@app.post("/superai/result", dependencies=[Depends(validate_token)])
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

        final_list.append(RowCalc(**result_dict))

    return {
        'error': False,
        'message': '',
        'data': final_list
    }


@app.post("/superai/zns", dependencies=[Depends(validate_token)])
def get_data_zns(
    date: str,
    receiver_province: str, receiver_district: str,
    carrier_id: int, message_count: int,
    star: int, feedbacks: List[str],
    note: str, submitted_at: str
):
    return {
        'error': False,
        'message': "",
        'data': {
            'count': 1,
            'zns': {
                'date': date,
                'receiver_province': receiver_province,
                'receiver_district': receiver_district,
                'carrier_id': carrier_id,
                'message_count': message_count,
                'star': star,
                'feedbacks': feedbacks,
                'note': note,
                'submitted_at': submitted_at
            },
        },
    }


@app.post("/superai/order", dependencies=[Depends(validate_token)])
def get_data_order(
    date: str,
    order_code: str,
    created_at: str, sent_at: str, order_status: str,
    carrier_id: int, carrier_status: str,
    sender_province: str, sender_district: str,
    receiver_province: str, receiver_district: str,
    delivery_count: int, pickup: str,
    barter: str, carrier_delivered_at: str,
    picked_at: str, last_delivering_at: str, carrier_updated_at: str
):
    return {
        'error': False,
        'message': "",
        'data': {
            'count': 1,
            'order': {
                'date': date,
                'order_code': order_code,
                'created_at': created_at,
                'sent_at': sent_at,
                'order_status': order_status,
                'carrier_id': carrier_id,
                'carrier_status': carrier_status,
                'sender_province': sender_province,
                'sender_district': sender_district,
                'receiver_province': receiver_province,
                'receiver_district': receiver_district,
                'delivery_count': delivery_count,
                'pickup': pickup,
                'barter': barter,
                'carrier_delivered_at': carrier_delivered_at,
                'picked_at': picked_at,
                'last_delivering_at': last_delivering_at,
                'carrier_updated_at': carrier_updated_at,
            },
        },
    }


@app.post("/superai/output", dependencies=[Depends(validate_token)])
def get_all_rows(batch: int = 10):
    rows = db.query(models.RowAPI).limit(batch).all()
    if rows is None:
        # raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resources Not Found")
        return {
            'error': True,
            'message': "Resources not found",
            'data': [],
        }
    else:
        return {
            'error': False,
            'message': "",
            'data': rows,
        }


@app.post("/superai/output/district", dependencies=[Depends(validate_token)])
def get_rows_by_district_code(district_code: str = '001'):
    rows = (
        db.query(models.RowAPI)
            .filter(models.RowAPI.receiver_district_code == district_code).all()
    )
    if rows is None:
        return {
            'error': True,
            'message': "Resources not found",
            'data': [],
        }
    else:
        return {
            'error': False,
            'message': "",
            'data': rows,
        }
