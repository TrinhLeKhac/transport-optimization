from typing import Annotated

from fastapi import Depends, APIRouter, Body
from sqlalchemy.exc import ProgrammingError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from scripts.api import schemas, models
from scripts.api.database import *
from scripts.api.utilities.helper import *

router = APIRouter()


@router.post("")
async def get_data_zns(
    request_data: Annotated[schemas.MessageZNSModel, Body(description="Data zns")],
    db_session: AsyncSession = Depends(get_db)
):
    try:
        data_dict = request_data.model_dump()
        zns_inf = models.MessageZNS(**data_dict)

        db_session.add(zns_inf)
        await db_session.commit()
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
    else:
        return {
            "error": False,
            "message": "",
            "data": {
                "count": 1,
                "zns": zns_inf,
            },
        }
