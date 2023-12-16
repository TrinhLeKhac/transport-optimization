from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session
from scripts.api import schemas, models
from scripts.api.database import *

router = APIRouter()


@router.post("")
def get_data_order(request_data: schemas.OrderModel, db: Session = Depends(get_db)):
    db_order = models.Order(**request_data.model_dump())
    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    return {
        "error": False,
        "message": "",
        "data": {
            "count": 1,
            "order": db_order,
        },
    }
