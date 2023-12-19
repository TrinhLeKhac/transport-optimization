from fastapi import Depends, APIRouter
from sqlalchemy.ext.asyncio import async_sessionmaker,
from sqlalchemy.exc import ProgrammingError, IntegrityError
from scripts.api import schemas, models
from scripts.api.utilities.helper import *

router = APIRouter()


@router.post("")
def get_data_order(request_data: schemas.OrderModel, db: Session = Depends(get_db)):
    try:
        data_dict = request_data.model_dump()

        db_order = models.Order(**data_dict)
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
    except ProgrammingError as e:
        if 'relation "db_schema.order" does not exist' in str(e):
            create_tbl_if_not_exists('db_schema', 'order')
            return {
                "error": True,
                "message": "Table order does not exist. Already created. Please insert data",
                "data": {}
            }
    except IntegrityError as e:
        if "constraint_dup_" in str(e):
            return {
                "error": True,
                "message": "Duplicate row already exists",
                "data": {}
            }
