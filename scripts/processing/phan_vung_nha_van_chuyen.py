from scripts.utilities.helper import *


@exception_wrapper
def xu_ly_phan_vung_nha_van_chuyen():
    # 1. Đọc thông tin raw
    try:
        phan_vung_nvc = pd.read_excel(ROOT_PATH + '/user_input/phan_vung_ghep_supership.xlsx')
    except FileNotFoundError:
        print(f"Error: The file {ROOT_PATH}/user_input/phan_vung_ghep_supership.xlsx was not found. Use file {ROOT_PATH}/input/phan_vung_ghep_supership.xlsx instead.")
        phan_vung_nvc = pd.read_excel(ROOT_PATH + '/input/phan_vung_ghep_supership.xlsx')

    phan_vung_nvc = phan_vung_nvc.iloc[3:, 2:25]
    phan_vung_nvc.columns = [
        'receiver_province', 'receiver_district', 'short_receiver_district',
        'ghn_outer_region', 'ghn_inner_region',
        'njv_outer_region', 'njv_inner_region',
        'vtp_outer_region', 'vtp_inner_region',
        'spx_outer_region', 'spx_inner_region',
        'best_outer_region', 'best_inner_region',
        'ghtk_outer_region', 'ghtk_inner_region',
        'supership_outer_region', 'supership_inner_region',
        'tikinow_outer_region', 'tikinow_inner_region',
        'vnpost_outer_region', 'vnpost_inner_region',
        'lazada_outer_region', 'lazada_inner_region',
    ]
    phan_vung_nvc = phan_vung_nvc.drop('short_receiver_district', axis=1)

    # 2. Thông tin từng nhà vận chuyển
    ghn = phan_vung_nvc[[
        'receiver_province', 'receiver_district',
        'ghn_outer_region', 'ghn_inner_region']].rename(columns={
        'ghn_outer_region': 'outer_region',
        'ghn_inner_region': 'inner_region'
    })
    ghn['carrier'] = 'GHN'

    njv = phan_vung_nvc[[
        'receiver_province', 'receiver_district',
        'njv_outer_region', 'njv_inner_region']].rename(columns={
        'njv_outer_region': 'outer_region',
        'njv_inner_region': 'inner_region'
    })
    njv['carrier'] = 'Ninja Van'

    vtp = phan_vung_nvc[[
        'receiver_province', 'receiver_district',
        'vtp_outer_region', 'vtp_inner_region']].rename(columns={
        'vtp_outer_region': 'outer_region',
        'vtp_inner_region': 'inner_region'
    })
    vtp['carrier'] = 'Viettel Post'

    spx = phan_vung_nvc[[
        'receiver_province', 'receiver_district',
        'spx_outer_region', 'spx_inner_region']].rename(columns={
        'spx_outer_region': 'outer_region',
        'spx_inner_region': 'inner_region'
    })
    spx['carrier'] = 'SPX Express'

    best = phan_vung_nvc[[
        'receiver_province', 'receiver_district',
        'best_outer_region', 'best_inner_region']].rename(columns={
        'best_outer_region': 'outer_region',
        'best_inner_region': 'inner_region'
    })
    best['carrier'] = 'BEST Express'

    ghtk = phan_vung_nvc[[
        'receiver_province', 'receiver_district',
        'ghtk_outer_region', 'ghtk_inner_region']].rename(columns={
        'ghtk_outer_region': 'outer_region',
        'ghtk_inner_region': 'inner_region'
    })
    ghtk['carrier'] = 'GHTK'

    vnpost = phan_vung_nvc[[
        'receiver_province', 'receiver_district',
        'vnpost_outer_region', 'vnpost_inner_region']].rename(columns={
        'vnpost_outer_region': 'outer_region',
        'vnpost_inner_region': 'inner_region'
    })
    vnpost['carrier'] = 'VNPost'

    lazada = phan_vung_nvc[[
        'receiver_province', 'receiver_district',
        'lazada_outer_region', 'lazada_inner_region']].rename(columns={
        'lazada_outer_region': 'outer_region',
        'lazada_inner_region': 'inner_region'
    })
    lazada['carrier'] = 'Lazada Logistics'

    phan_vung_nvc_final = pd.concat([ghn, njv, vtp, spx, best, ghtk, vnpost, lazada], ignore_index=True)
    phan_vung_nvc_final = phan_vung_nvc_final[
        ['carrier', 'receiver_province', 'receiver_district', 'outer_region', 'inner_region']]
    phan_vung_nvc_final['inner_region'] = phan_vung_nvc_final['inner_region'].map({
        'Nội thành': 'Nội Thành',
        'Ngoại thành': 'Ngoại Thành'
    }).fillna('inner_region')

    # 3. Đưa thông tin quận/huyện, tỉnh/thành về dạng chuẩn
    phan_vung_nvc_final = normalize_province_district(phan_vung_nvc_final, tinh_thanh='receiver_province',
                                                      quan_huyen='receiver_district')
    phan_vung_nvc_final = phan_vung_nvc_final.loc[
        phan_vung_nvc_final['receiver_province'].notna()
        & phan_vung_nvc_final['receiver_district'].notna()
        ]

    # 4. Check tên nhà vận chuyển đã được chuẩn hóa chưa
    set_carrier = set(phan_vung_nvc_final['carrier'].unique().tolist())
    set_norm_full_carrier = set(MAPPING_CARRIER_ID.keys())
    assert set_carrier - set_norm_full_carrier == set(), 'Ops, Tên nhà vận chuyển chưa được chuẩn hóa'

    # 5. Mapping ID column
    phan_vung_nvc_final = (
        phan_vung_nvc_final
            .merge(
            PROVINCE_MAPPING_DISTRICT_DF.rename(columns={
                'province_code': 'receiver_province_code',
                'district_code': 'receiver_district_code',
                'province': 'receiver_province',
                'district': 'receiver_district'
            }), on=['receiver_province', 'receiver_district'], how='left')
    )
    phan_vung_nvc_final['outer_region_id'] = phan_vung_nvc_final['outer_region'].map(
        {'Miền Bắc': 0, 'Miền Trung': 1, 'Miền Nam': 2})
    phan_vung_nvc_final['inner_region_id'] = phan_vung_nvc_final['inner_region'].map({'Nội Thành': 0, 'Ngoại Thành': 1})
    phan_vung_nvc_final['carrier_id'] = phan_vung_nvc_final['carrier'].map(MAPPING_CARRIER_ID)
    phan_vung_nvc_final = phan_vung_nvc_final[[
        'carrier_id', 'carrier',
        'receiver_province_code', 'receiver_province', 'receiver_district_code', 'receiver_district',
        'outer_region_id', 'outer_region', 'inner_region_id', 'inner_region'
    ]]

    # 5. Lưu thông tin
    phan_vung_nvc_final.to_parquet(ROOT_PATH + '/processed_data/phan_vung_nvc.parquet', index=False)
