from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session
from scripts.api import models
from scripts.api.database import *

router = APIRouter()


@router.get("")
def get_all_rows(batch: int = 10, db: Session = Depends(get_db)):
    db_api = db.query(models.API).limit(batch).all()
    if db_api is None:
        return {
            "error": True,
            "message": "Resources not found",
            "data": [],
        }
    else:
        return {
            "error": False,
            "message": "",
            "data": db_api,
        }


@router.get("/district")
def get_rows_by_district_code(district_code: str = "001", db: Session = Depends(get_db)):
    db_api_by_district = db.query(models.API).filter(models.API.receiver_district_code == district_code).all()
    if db_api_by_district is None:
        return {
            "error": True,
            "message": "Resources not found",
            "data": [],
        }
    else:
        return {
            "error": False,
            "message": "",
            "data": db_api_by_district,
        }
