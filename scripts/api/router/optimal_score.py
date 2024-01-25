import pandas as pd
from fastapi import APIRouter
from scripts.utilities.helper import *

router = APIRouter()


@router.get("")
async def get_optimal_score(
    date: str = "2024-01-01",
):
    optimal_score_df = pd.read_parquet(ROOT_PATH + '/output/total_optimal_score.parquet')
    # score = optimal_score_df.tail(1)['score'].values[0]
    try:
        score = optimal_score_df.loc[optimal_score_df['date'] == date]['score'].values[0]
        return {
            "error": False,
            "message": "",
            "data": score,
        }
    except:
        return {
            "error": True,
            "message": f"Optimal score not found",
            "data": -1,
        }