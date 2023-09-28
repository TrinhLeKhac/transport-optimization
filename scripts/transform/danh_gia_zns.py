
import sys
from pathlib import Path
sys.path.append(Path(__file__).parent)

from config import *
from helper import *
    
def transform_data_danh_gia_zns():
    
    # Đọc thông tin data ZNS
    danh_gia_zns = pd.read_parquet(ROOT_PATH + '/processed_data/danh_gia_zns.parquet')
    
    # Xử lý data
    danh_gia_zns['nhan_xet'] = danh_gia_zns['nhan_xet'].fillna('Khác')
    danh_gia_zns['nhan_xet'] = danh_gia_zns['nhan_xet'].apply(lambda s: unidecode(' '.join(s.split()).strip().lower()))
    danh_gia_zns.loc[
        danh_gia_zns['nhan_xet'].str.contains('nhan vien khong nhiet tinh'), 'nhan_xet'
    ] = 'Nhân viên không nhiệt tình'
    danh_gia_zns.loc[danh_gia_zns['nhan_xet'] != 'Nhân viên không nhiệt tình', 'nhan_xet'] = 'Khác'
    
    danh_gia_zns = danh_gia_zns[[
        'tinh_thanh_giao_hang', 'quan_huyen_giao_hang', 
        'nha_van_chuyen', 'nhan_xet', 'so_sao'
    ]].rename(columns={
        'tinh_thanh_giao_hang': 'tinh_thanh', 
        'quan_huyen_giao_hang': 'quan_huyen'
    })
    
    danh_gia_zns = danh_gia_zns.loc[danh_gia_zns['nha_van_chuyen'] != 'SuperShip'] # bỏ SuperShip
    danh_gia_zns['nha_van_chuyen'] = danh_gia_zns['nha_van_chuyen'].map({
        'BEST Express': 'best',
        'Ninja Van': 'ninja_van',
        'GHN': 'ghn',
        'Shopee Express': 'shopee_express',
        'Viettel Post': 'viettel_post',
        'GHTK': 'ghtk',
        'TikiNow':'tikinow',
    })

    # Tách nhóm loại bỏ
    zns_1_2_sao = (
        danh_gia_zns.loc[
            danh_gia_zns['so_sao'].isin([1, 2])
        ].groupby(['tinh_thanh', 'quan_huyen', 'nha_van_chuyen'])
        ['so_sao']
        .count()
        .reset_index()
        .rename(columns = {'so_sao': 'so_lan_danh_gia_1_2_sao'})
    )
    zns_total = (
        danh_gia_zns
        .groupby(['tinh_thanh', 'quan_huyen', 'nha_van_chuyen'])
        ['so_sao']
        .count()
        .reset_index()
        .rename(columns = {'so_sao': 'tong_so_lan_danh_gia'})
    )
    zns_total = zns_total.merge(zns_1_2_sao, on=['tinh_thanh', 'quan_huyen', 'nha_van_chuyen'], how='left')
    zns_total['so_lan_danh_gia_1_2_sao'] = zns_total['so_lan_danh_gia_1_2_sao'].fillna(0).astype(int)
    zns_total['pct'] = zns_total['so_lan_danh_gia_1_2_sao']/zns_total['tong_so_lan_danh_gia']
    zns_loai_bo = zns_total[zns_total['pct'] >= 0.3]
    zns_loai_bo['loai_danh_gia'] = 'Loại'

    # Filter phần còn lại
    danh_gia_zns_filter1 = merge_left_only(danh_gia_zns, zns_loai_bo, keys=['tinh_thanh', 'quan_huyen', 'nha_van_chuyen'])

    # Tách nhóm đánh giá 1 sao loại 1
    zns_1_sao_type_1 = danh_gia_zns_filter1.loc[
        (danh_gia_zns_filter1['so_sao'] == 1) &
        (danh_gia_zns_filter1['nhan_xet'] == 'Nhân viên không nhiệt tình')
    ][['tinh_thanh', 'quan_huyen', 'nha_van_chuyen']].drop_duplicates()
    zns_1_sao_type_1['loai_danh_gia'] = '1 sao & Nhân viên không nhiệt tình'

    # Filter phần còn lại
    danh_gia_zns_filter2 = merge_left_only(danh_gia_zns_filter1, zns_1_sao_type_1, keys=['tinh_thanh', 'quan_huyen', 'nha_van_chuyen'])

    # Tách nhóm đánh giá 1 sao loại 2
    zns_1_sao_type_2 = (
        danh_gia_zns_filter2.loc[
            (danh_gia_zns_filter2['so_sao'] == 1)
        ].groupby(['tinh_thanh', 'quan_huyen', 'nha_van_chuyen'])
        ['so_sao'].count().reset_index()
    )
    zns_1_sao_type_2 = zns_1_sao_type_2.loc[zns_1_sao_type_2['so_sao'] > 1].drop('so_sao', axis=1)
    zns_1_sao_type_2['loai_danh_gia'] = 'Nhiều hơn 1 lần đánh giá 1 sao'

    # Filter phần còn lại
    danh_gia_zns_filter3 = merge_left_only(danh_gia_zns_filter2, zns_1_sao_type_2, keys=['tinh_thanh', 'quan_huyen', 'nha_van_chuyen'])

    # Tách nhóm đánh giá 5 sao
    zns_5_sao = (
        danh_gia_zns_filter3.loc[
            danh_gia_zns_filter3['so_sao'].isin([5])
        ].groupby(['tinh_thanh', 'quan_huyen', 'nha_van_chuyen'])
        ['so_sao']
        .count()
        .reset_index()
        .rename(columns = {'so_sao': 'so_lan_danh_gia_5_sao'})
    )
    zns_total_filter3 = (
        danh_gia_zns_filter3
        .groupby(['tinh_thanh', 'quan_huyen', 'nha_van_chuyen'])
        ['so_sao']
        .count()
        .reset_index()
        .rename(columns = {'so_sao': 'tong_so_lan_danh_gia'})
    )
    zns_total_filter3 = zns_total_filter3.merge(zns_5_sao, on=['tinh_thanh', 'quan_huyen', 'nha_van_chuyen'], how='left')
    zns_total_filter3['so_lan_danh_gia_5_sao'] = zns_total_filter3['so_lan_danh_gia_5_sao'].fillna(0).astype(int)
    zns_total_filter3['pct'] = zns_total_filter3['so_lan_danh_gia_5_sao']/zns_total_filter3['tong_so_lan_danh_gia']
    zns_5_sao = zns_total_filter3[zns_total_filter3['pct'] >= 0.95]
    zns_5_sao['loai_danh_gia'] = 'Đánh giá 5 sao trên 95% đơn'

    # Filter phần còn lại
    danh_gia_zns_filter4 = merge_left_only(danh_gia_zns_filter3, zns_5_sao, keys=['tinh_thanh', 'quan_huyen', 'nha_van_chuyen'])

    # Tách nhóm còn lại
    zns_have_1_2_3_sao = (
        # có 1, 2, 3 sao
        danh_gia_zns_filter4.loc[
            danh_gia_zns_filter4['so_sao'].isin([1, 2, 3])]
        [['tinh_thanh', 'quan_huyen', 'nha_van_chuyen']]
        .drop_duplicates()
    )
    zns_have_1_2_3_sao['loai_danh_gia'] = 'Bình thường'
    
    # chỉ có 4, 5 sao
    danh_gia_zns_filter5 = merge_left_only(danh_gia_zns_filter4, zns_have_1_2_3_sao, keys=['tinh_thanh', 'quan_huyen', 'nha_van_chuyen'])
    only_4_5_sao = danh_gia_zns_filter5[['tinh_thanh', 'quan_huyen', 'nha_van_chuyen']].drop_duplicates()
    only_4_5_sao['loai_danh_gia'] = 'Không phát sinh đánh giá 1, 2, 3 sao'

    # Tổng hợp thông tin
    final_zns = pd.concat([
        zns_loai_bo,
        zns_1_sao_type_1,
        zns_1_sao_type_2,
        zns_5_sao,
        zns_have_1_2_3_sao,
        only_4_5_sao
    ])[['tinh_thanh', 'quan_huyen', 'nha_van_chuyen', 'loai_danh_gia']].reset_index(drop=True)

    # Transform thông tin
    final_zns_pivot = pd.pivot_table(
        data=final_zns, 
        index=['tinh_thanh', 'quan_huyen'], 
        columns=['nha_van_chuyen'], 
        values='loai_danh_gia',
        aggfunc=np.sum,
        fill_value='Không có thông tin'
    ).rename_axis(None, axis=1).reset_index()
    final_zns_pivot['tieu_chi'] = 'Đánh giá ZNS'
    final_zns_pivot['trong_so'] = TRONG_SO['Đánh giá ZNS']['Tiêu chí']
    for c in LIST_NVC:
        if c not in final_zns_pivot.columns.tolist():
            final_zns_pivot[c] = 'Không có thông tin'
        final_zns_pivot[c + '_stt'] = final_zns_pivot[c]
        final_zns_pivot[c + '_score'] = final_zns_pivot[c + '_stt'].map(TRONG_SO['Đánh giá ZNS']['Phân loại'])
    final_zns_pivot = final_zns_pivot[SELECTED_COLS]

    # Check logic transform 
    assert final_zns_pivot.isna().sum().all() == 0, 'Tranform data hoặc mapping score+status có vấn đề'

    return final_zns_pivot
    # Lưu thông tin
    # final_zns_pivot.to_parquet('../../output/danh_gia_zns.parquet', index=False)
    