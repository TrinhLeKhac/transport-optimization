from fastapi import Depends, APIRouter
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from scripts.api import models
from scripts.api.database import *


router = APIRouter()


@router.post("")
async def get_rows_by_district_code(
    date: str,
    district_code: str = "001",
    db_session: AsyncSession = Depends(get_db)
):
    try:
        result = await models.API.find_by_district(db_session, date, district_code)
    except SQLAlchemyError as e:
        return {
            "error": True,
            "message": "Request to the API can not be processed",
            "data": []
        }
    else:
        if result is None:
            return {
                "error": True,
                "message": "Resources not found",
                "data": [],
            }
        else:
            return {
                "error": False,
                "message": "",
                "data": result,
            }
