from scripts.utilities.helper import *
from scripts.utilities.config import *


def status_chat_luong_noi_bo_ninja_van(series, col1='delivery_success_rate', col2='is_more_than_100'):
    if series[col1] == 0:
        return 'Không có thông tin'
    elif (series[col1] > 0.98) & series[col2]:
        return 'Ti lệ trên 98% và tổng số đơn giao hàng trên 100 đơn'
    elif (series[col1] > 0.94) & (series[col1] <= 0.98) & series[col2]:
        return 'Ti lệ trên 94% và tổng số đơn giao hàng trên 100 đơn'
    elif (series[col1] > 0.91) & (series[col1] <= 0.94) & series[col2]:
        return 'Ti lệ trên 91% và tổng số đơn giao hàng trên 100 đơn'
    elif (series[col1] <= 0.91) & series[col2]:
        return 'Ti lệ dưới 91% và tổng số đơn giao hàng trên 100 đơn'
    elif (series[col1] > 0.98) & (~series[col2]):
        return 'Ti lệ trên 98% và tổng số đơn giao hàng dưới 100 đơn'
    elif (series[col1] > 0.94) & (series[col1] <= 0.98) & (~series[col2]):
        return 'Ti lệ trên 94% và tổng số đơn giao hàng dưới 100 đơn'
    elif (series[col1] > 0.91) & (series[col1] <= 0.94) & (~series[col2]):
        return 'Ti lệ trên 91% và tổng số đơn giao hàng dưới 100 đơn'
    elif (series[col1] <= 0.91) & (~series[col2]):
        return 'Ti lệ dưới 91% và tổng số đơn giao hàng dưới 100 đơn'


def status_chat_luong_noi_bo_lazada(series, col='delivery_success_rate'):
    if series[col] == 0:
        return 'Không có thông tin'
    elif series[col] > 0.99:
        return 'Ti lệ trên 99%'
    elif series[col] > 0.98:
        return 'Ti lệ trên 98%'
    elif series[col] > 0.97:
        return 'Ti lệ trên 97%'
    elif series[col] > 0.965:
        return 'Ti lệ trên 96.5%'
    elif series[col] > 0.96:
        return 'Ti lệ trên 96%'
    elif series[col] > 0.955:
        return 'Ti lệ trên 95.5%'
    elif series[col] > 0.95:
        return 'Ti lệ trên 95%'
    elif series[col] > 0.94:
        return 'Ti lệ trên 94%'
    elif series[col] <= 0.94:
        return 'Ti lệ dưới 94%'


def transform_data_chat_luong_noi_bo_ninja_van():
    chat_luong_noi_bo_df = pd.read_parquet(ROOT_PATH + '/processed_data/chat_luong_noi_bo_njv.parquet')

    chat_luong_noi_bo_df['status'] = chat_luong_noi_bo_df.apply(status_chat_luong_noi_bo_ninja_van, axis=1)
    chat_luong_noi_bo_df['score'] = (
        chat_luong_noi_bo_df['status'].map(TRONG_SO['Chất lượng nội bộ']['Phân loại']['Ninja Van'])
    )

    chat_luong_noi_bo_df = (
        chat_luong_noi_bo_df.merge(
            PROVINCE_MAPPING_DISTRICT_DF[['province', 'district']].rename(columns={
                'province': 'receiver_province',
                'district': 'receiver_district'
            }), on=['receiver_province', 'receiver_district'], how='right')
    )
    chat_luong_noi_bo_df['status'] = chat_luong_noi_bo_df['status'].fillna('Không có thông tin')
    chat_luong_noi_bo_df['score'] = chat_luong_noi_bo_df['score'].fillna(5)

    chat_luong_noi_bo_df['carrier'] = 'Ninja Van'
    chat_luong_noi_bo_df['criteria'] = 'Chất lượng nội bộ'
    chat_luong_noi_bo_df['criteria_weight'] = TRONG_SO['Chất lượng nội bộ']['Tiêu chí']

    chat_luong_noi_bo_df = chat_luong_noi_bo_df[
        ['receiver_province', 'receiver_district', 'carrier', 'status', 'score', 'criteria', 'criteria_weight']]
    chat_luong_noi_bo_df.to_parquet(ROOT_PATH + '/transform/chat_luong_noi_bo_njv.parquet', index=False)

    return chat_luong_noi_bo_df


def transform_data_chat_luong_noi_bo_lazada():
    chat_luong_noi_bo_df = pd.read_parquet(ROOT_PATH + '/processed_data/chat_luong_noi_bo_lazada.parquet')
    chat_luong_noi_bo_df['status'] = chat_luong_noi_bo_df.apply(status_chat_luong_noi_bo_lazada, axis=1)
    chat_luong_noi_bo_df['score'] = (
        chat_luong_noi_bo_df['status'].map(TRONG_SO['Chất lượng nội bộ']['Phân loại']['Lazada Logistics'])
    )
    chat_luong_noi_bo_df = (
        chat_luong_noi_bo_df.merge(
            PROVINCE_MAPPING_DISTRICT_DF[['province', 'district']].rename(columns={
                'province': 'receiver_province',
                'district': 'receiver_district'
            }), on=['receiver_province', 'receiver_district'], how='right')
    )
    chat_luong_noi_bo_df['status'] = chat_luong_noi_bo_df['status'].fillna('Không có thông tin')
    chat_luong_noi_bo_df['score'] = chat_luong_noi_bo_df['score'].fillna(5)

    chat_luong_noi_bo_df['carrier'] = 'Lazada Logistics'
    chat_luong_noi_bo_df['criteria'] = 'Chất lượng nội bộ'
    chat_luong_noi_bo_df['criteria_weight'] = TRONG_SO['Chất lượng nội bộ']['Tiêu chí']

    chat_luong_noi_bo_df = chat_luong_noi_bo_df[
        ['receiver_province', 'receiver_district', 'carrier', 'status', 'score', 'criteria', 'criteria_weight']]
    chat_luong_noi_bo_df.to_parquet(ROOT_PATH + '/transform/chat_luong_noi_bo_lazada.parquet', index=False)

    return chat_luong_noi_bo_df
