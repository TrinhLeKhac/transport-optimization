from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session
from scripts.api import schemas, models
from scripts.api.database import *

router = APIRouter()


@router.post("")
def get_data_zns(request_data: schemas.MessageZNSModel, db: Session = Depends(get_db)):
    data_dict = request_data.model_dump()

    db_zns = models.MessageZNS(**data_dict)
    db.add(db_zns)
    db.commit()
    db.refresh(db_zns)

    return {
        "error": False,
        "message": "",
        "data": {
            "count": 1,
            "zns": db_zns,
        },
    }
