from typing import Annotated

from fastapi import APIRouter, Depends, Body
from sqlalchemy.ext.asyncio import AsyncSession
from scripts.api.database import get_db
from sqlalchemy.exc import ProgrammingError, IntegrityError
from scripts.api import schemas, models
from scripts.api.utilities.helper import *

router = APIRouter()


@router.post("")
async def get_data_ngung_giao_nhan_level_3_rev(
    request_data: Annotated[schemas.NGNLV3Model, Body(description="Data ngung giao nhan level 3")],
    db_session: AsyncSession = Depends(get_db)
):
    try:
        data_dict = request_data.model_dump()
        ngung_giao_nhan_level_3_inf = models.NGNLV3(**data_dict)

        db_session.add(ngung_giao_nhan_level_3_inf)
        await db_session.commit()
    except ProgrammingError as e:
        if 'relation "db_schema.tbl_ngung_giao_nhan_level_3_rev" does not exist' in str(e):
            create_tbl_if_not_exists('db_schema', 'tbl_ngung_giao_nhan_level_3_rev')
            return {
                "error": True,
                "message": "Table tbl_ngung_giao_nhan_level_3_rev does not exist. Already created. Please insert data",
                "data": {}
            }
    else:
        return {
            "error": False,
            "message": "",
            "data": {
                "count": 1,
                "ngn_status": ngung_giao_nhan_level_3_inf,
            },
        }
