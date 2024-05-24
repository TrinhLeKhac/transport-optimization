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
        district_api_res = requests.get('https://api.mysupership.vn/v1/partner/areas/district?province={}'.format(province_code), verify=False).json()['results']
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
            district_df, on='province_code', how='inner'
        ).sort_values(['province_code', 'district_code'])
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
        district_api_res = requests.get('https://api.mysupership.vn/v1/partner/areas/district?province={}'.format(province_code), verify=False).json()['results']
        district_list = [item['name'] for item in district_api_res]
        province_mapping_district_dict[province] = district_list

    with open(ROOT_PATH + '/input/province_mapping_district_from_api.json', 'w') as file:
        json.dump(province_mapping_district_dict, file)


def get_latest_province_mapping_district_mapping_ward():
    province_api_res = requests.get('https://api.mysupership.vn/v1/partner/areas/province', verify=False).json()

    province_df = pd.DataFrame(data={
        'province_code': [c['code'] for c in province_api_res['results']],
        'province': [c['name'] for c in province_api_res['results']]
    })

    list_district_df = []
    for province_code in province_df['province_code'].tolist():
        district_api_res = requests.get('https://api.mysupership.vn/v1/partner/areas/district?province={}'.format(province_code), verify=False).json()['results']
        for item in district_api_res:
            tmp_df = pd.DataFrame(data={
                'district_code': [item['code']],
                'district': [item['name']],
                'province_code': [province_code]
            })
            list_district_df.append(tmp_df)
    district_df = pd.concat(list_district_df, ignore_index=True)

    list_commune_df = []
    for district, district_code in zip(district_df['district'].tolist(), district_df['district_code'].tolist()):
        commune_api_res = requests.get('https://api.mysupership.vn/v1/partner/areas/commune?district={}'.format(district_code), verify=False).json()['results']
        if len(commune_api_res) == 0:
            print(f'District {district} with code {district_code} has no commune')
        else:
            for item in commune_api_res:
                tmp_df = pd.DataFrame(data={
                    'commune_code': [item['code']],
                    'commune': [item['name']],
                    'district_code': [district_code]
                })
                list_commune_df.append(tmp_df)
    commune_df = pd.concat(list_commune_df, ignore_index=True)

    province_district_ward_df = (
        province_df
        .merge(
            district_df, on='province_code', how='inner'
        ).merge(
            commune_df, on='district_code', how='inner'
        )
        .sort_values(['province', 'district', 'commune', 'commune_code'], ascending=[True, True, True, False])
        .drop_duplicates(['province', 'district', 'commune'])
        .reset_index(drop=True)
    )

    province_district_ward_df.to_parquet(ROOT_PATH + '/input/province_mapping_district_mapping_ward.parquet', index=False)


def get_latest_province_mapping_district_mapping_ward_json():
    province_api_res = requests.get('https://api.mysupership.vn/v1/partner/areas/province', verify=False).json()
    province_mapping_district_mapping_ward_dict = {}

    for province_code, province in zip(
            [c['code'] for c in province_api_res['results']],
            [c['name'] for c in province_api_res['results']]
    ):
        district_api_res = requests.get('https://api.mysupership.vn/v1/partner/areas/district?province={}'.format(province_code), verify=False).json()['results']

        district_list = [item['name'] for item in district_api_res]
        district_code_list = [item['code'] for item in district_api_res]

        district_mapping_commune_dict = {}
        for district_code, district in zip(district_code_list, district_list):
            commune_api_res = requests.get('https://api.mysupership.vn/v1/partner/areas/commune?district={}'.format(district_code), verify=False).json()['results']
            commune_list = list(set([item['name'] for item in commune_api_res]))
            district_mapping_commune_dict[district] = commune_list

        province_mapping_district_mapping_ward_dict[province] = district_mapping_commune_dict

    with open(ROOT_PATH + '/input/province_mapping_district_mapping_ward_from_api.json', 'w') as file:
        json.dump(province_mapping_district_mapping_ward_dict, file)


# if __name__ == '__main__':
#     get_latest_province_mapping_district()
#     get_latest_province_mapping_district_json()
#     get_latest_province_mapping_district_mapping_ward()
#     get_latest_province_mapping_district_mapping_ward_json()
