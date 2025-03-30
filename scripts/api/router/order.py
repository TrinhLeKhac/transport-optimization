from typing import Annotated

from fastapi import APIRouter, Body, Depends
from sqlalchemy.exc import IntegrityError, ProgrammingError
from sqlalchemy.ext.asyncio import AsyncSession

from scripts.api import models, schemas
from scripts.api.database import get_db
from scripts.api.utilities.helper import *

router = APIRouter()


@router.post("")
async def get_data_order(
    request_data: Annotated[schemas.OrderModel, Body(description="Data order")],
    db_session: AsyncSession = Depends(get_db),
):
    try:
        data_dict = request_data.model_dump()
        order_inf = models.Order(**data_dict)

        db_session.add(order_inf)
        await db_session.commit()
    except ProgrammingError as e:
        if 'relation "db_schema.order" does not exist' in str(e):
            create_tbl_if_not_exists("db_schema", "order")
            return {
                "error": True,
                "message": "Table order does not exist. Already created. Please insert data",
                "data": {},
            }
    except IntegrityError as e:
        if "constraint_dup_" in str(e):
            return {
                "error": True,
                "message": "Duplicate row already exists",
                "data": {},
            }
    else:
        return {
            "error": False,
            "message": "",
            "data": {
                "count": 1,
                "order": order_inf,
            },
        }
