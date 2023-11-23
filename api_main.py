from fastapi import FastAPI, status, HTTPException
from pydantic import BaseModel
from scripts.database.database import session
from scripts.database import models
from typing import List
from scripts.api.out_data_final import *
from scripts.auth.token import *
from scripts.auth.security import reusable_oauth2, validate_token
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
    order_code: str
    carrier_id: int
    new_type: int
    route_type: int
    price: int
    status: int
    description: str
    time_data: float
    time_display: str
    rate: float
    for_shop: int
    for_partner: int
    price_ranking: int
    speed_ranking: int
    score_ranking: int
    score: float
    star: float

    class Config:
        orm_mode = True


@app.post('/login')
def login(request_data: LoginRequest):
    print(f'[x] request_data: {request_data.__dict__}')
    if verify_password(username=request_data.username, password=request_data.password):
        token = generate_token(request_data.username, request_data.password)
        return {
            'token': token
        }
    else:
        raise HTTPException(status_code=404, detail="User not found")


@app.get("/api/v1/output/", dependencies=[Depends(validate_token)], response_model=List[RowAPI], status_code=status.HTTP_200_OK)
def get_all_rows(batch: int = 10):
    rows = db.query(models.RowAPI).limit(batch).all()
    if rows is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resources Not Found")
    return rows


@app.get("/api/v1/output/district/", dependencies=[Depends(validate_token)], response_model=List[RowAPI], status_code=status.HTTP_200_OK)
def get_rows_by_district_code(district_code: str = '001'):
    rows = (
        db.query(models.RowAPI)
            .filter(models.RowAPI.receiver_district_code == district_code).all()
    )
    if rows is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resources Not Found")
    return rows


@app.get("/api/v1/calculation/", dependencies=[Depends(validate_token)], response_model=List[RowCalc], status_code=200)
def calculate(
        order_code: str, weight: int, pickup_type_id: int,
        sender_province_code: str, sender_district_code: str,
        receiver_province_code: str, receiver_district_code: str
):
    pickup_type = None
    if pickup_type_id == 0:
        pickup_type = 'Gửi Bưu Cục'
    elif pickup_type_id == 1:
        pickup_type = 'Lấy Tận Nơi'

    df_input = pd.DataFrame(data={
        'order_id': [order_code],
        'weight': [weight],
        'delivery_type': [pickup_type],
        'sender_province_id': [sender_province_code],
        'sender_district_id': [sender_district_code],
        'receiver_province_id': [receiver_province_code],
        'receiver_district_id': [receiver_district_code],
    })
    df_output = out_data_final(df_input, show_logs=False)
    df_output = df_output[[
        'order_code', 'carrier_id', 'new_type', 'route_type',
        'price', 'status', 'description',
        'time_data', 'time_display', 'rate',
        'for_shop', 'for_partner',
        'price_ranking', 'speed_ranking', 'score_ranking',
        'score', 'star',
    ]]
    # print(df_output)
    final_list = []
    for i in range(len(df_output)):
        result_dict = {
            'order_code': df_output.loc[i, :]['order_code'],
            'carrier_id': df_output.loc[i, :]['carrier_id'],
            'new_type': df_output.loc[i, :]['new_type'],
            'route_type': df_output.loc[i, :]['route_type'],
            'price': df_output.loc[i, :]['price'],
            'status': df_output.loc[i, :]['status'],
            'description': df_output.loc[i, :]['description'],
            'time_data': df_output.loc[i, :]['time_data'],
            'time_display': df_output.loc[i, :]['time_display'],
            'rate': df_output.loc[i, :]['rate'],
            'for_shop': df_output.loc[i, :]['for_shop'],
            'for_partner': df_output.loc[i, :]['for_partner'],
            'price_ranking': df_output.loc[i, :]['price_ranking'],
            'speed_ranking': df_output.loc[i, :]['speed_ranking'],
            'score_ranking': df_output.loc[i, :]['score_ranking'],
            'score': df_output.loc[i, :]['score'],
            'star': df_output.loc[i, :]['star'],
        }

        final_list.append(RowCalc(**result_dict))

    return final_list
