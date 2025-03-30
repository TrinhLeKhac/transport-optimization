from typing import Annotated

from fastapi import APIRouter, Body, Depends
from sqlalchemy.exc import IntegrityError, ProgrammingError
from sqlalchemy.ext.asyncio import AsyncSession

from scripts.api import models, schemas
from scripts.api.database import get_db
from scripts.api.utilities.helper import *

router = APIRouter()


@router.post("")
async def get_data_ngung_giao_nhan_rev(
    request_data: Annotated[schemas.NGNModel, Body(description="Data ngung giao nhan")],
    db_session: AsyncSession = Depends(get_db),
):
    try:
        data_dict = request_data.model_dump()
        ngung_giao_nhan_inf = models.NGN(**data_dict)

        db_session.add(ngung_giao_nhan_inf)
        await db_session.commit()
    except ProgrammingError as e:
        if 'relation "db_schema.tbl_ngung_giao_nhan_rev" does not exist' in str(e):
            create_tbl_if_not_exists("db_schema", "tbl_ngung_giao_nhan_rev")
            return {
                "error": True,
                "message": "Table tbl_ngung_giao_nhan_rev does not exist. Already created. Please insert data",
                "data": {},
            }
    else:
        return {
            "error": False,
            "message": "",
            "data": {
                "count": 1,
                "ngn_status": ngung_giao_nhan_inf,
            },
        }
