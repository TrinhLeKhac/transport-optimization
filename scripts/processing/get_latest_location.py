import requests
import pandas as pd
from scripts.utilities.helper import *


def get_latest_province_mapping_district():
    province_api_res = requests.get('https://api.mysupership.vn/v1/partner/areas/province', verify=False).json()

    province_df = pd.DataFrame(data={
        'province_code': [c['code'] for c in province_api_res['results']],
        'province': [c['name'] for c in province_api_res['results']]
    })

    list_df = []
    for province_code in province_df['province_code'].tolist():
        district_api_res = requests.get('https://api.mysupership.vn/v1/partner/areas/district?province={}'.format(province_code),
                              verify=False).json()['results']
        for item in district_api_res:
            tmp_df = pd.DataFrame(data={
                'district_code': [item['code']],
                'district': [item['name']],
                'province_code': [province_code]
            })
            list_df.append(tmp_df)
    district_df = pd.concat(list_df, ignore_index=True)

    province_district_df = (
        province_df.merge(
            district_df, on='province_code', how='inner')
        .sort_values(['province_code', 'district_code'])
        .reset_index(drop=True)
    )
    province_district_df.to_parquet(ROOT_PATH + '/input/province_mapping_district.parquet', index=False)


def get_latest_province_mapping_district_json():

    province_api_res = requests.get('https://api.mysupership.vn/v1/partner/areas/province', verify=False).json()

    province_mapping_district_dict = {}

    for province_code, province in zip(
        [c['code'] for c in province_api_res['results']],
        [c['name'] for c in province_api_res['results']]
    ):
        district_api_res = requests.get('https://api.mysupership.vn/v1/partner/areas/district?province={}'.format(province_code),
                     verify=False).json()['results']
        district_list = [item['name'] for item in district_api_res]
        province_mapping_district_dict[province] = district_list

    with open(ROOT_PATH + '/input/province_mapping_district_from_api.json') as file:
        json.dump(province_mapping_district_dict, file)


if __name__ == '__main__':
    get_latest_province_mapping_district()
    get_latest_province_mapping_district_json()
