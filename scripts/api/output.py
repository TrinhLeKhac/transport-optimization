from pydantic import BaseModel
from scripts.auth.security import validate_token
from fastapi import Depends
from fastapi import APIRouter
from scripts.database.database import session
from scripts.database import models


class OutputModel(BaseModel):
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


db = session()
router = APIRouter()


@router.post("", dependencies=[Depends(validate_token)])
def get_all_rows(batch: int = 10):
    rows = db.query(models.Output29946API).limit(batch).all()
    if rows is None:
        return {
            "error": True,
            "message": "Resources not found",
            "data": [],
        }
    else:
        return {
            "error": False,
            "message": "",
            "data": rows,
        }


@router.post("/district", dependencies=[Depends(validate_token)])
def get_rows_by_district_code(district_code: str = "001"):
    rows = (
        db.query(models.Output29946API)
            .filter(models.Output29946API.receiver_district_code == district_code).all()
    )
    if rows is None:
        return {
            "error": True,
            "message": "Resources not found",
            "data": [],
        }
    else:
        return {
            "error": False,
            "message": "",
            "data": rows,
        }
