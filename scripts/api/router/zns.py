from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy.exc import ProgrammingError, IntegrityError
from scripts.api import schemas, models
from scripts.api.database import *
from scripts.api.utilities.helper import *

router = APIRouter()


@router.post("")
def get_data_zns(request_data: schemas.MessageZNSModel, db: Session = Depends(get_db)):
    try:
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
    except ProgrammingError as e:
        if 'relation "db_schema.zns" does not exist' in str(e):
            create_tbl_if_not_exists('db_schema', 'zns')
            return {
                "error": True,
                "message": "Table ZNS does not exist. Already created. Please insert data",
                "data": {}
            }
    except IntegrityError as e:
        if "constraint_dup_" in str(e):
            return {
                "error": True,
                "message": "Duplicate row already exists",
                "data": {}
            }
