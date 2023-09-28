
import sys
from pathlib import Path
sys.path.append(Path(__file__).parent)

from config import *
from helper import *

from transform.total_transform import merge_default_values, total_transform

############################################################################################################################

def out_data_api_full():
    
    # Lấy toàn bộ các dữ liệu đã được transform
    *target_df_tuple, tien_giao_dich = total_transform()

    # Tính toán các bảng status
    status_list = []
    for target_df in target_df_tuple:
        for col in LIST_NVC:
            target_df[col] = (
                target_df[['tieu_chi', 'trong_so', col + '_stt', col + '_score']]
                .to_dict(orient='records') 
            )
        target_df = target_df[['tinh_thanh', 'quan_huyen'] + LIST_NVC]
        status_list.append(target_df)
    status = pd.concat(status_list, ignore_index=True)
    
    status_agg_list = []
    for col in LIST_NVC:
        tmp_df = (
            status
            .groupby(['tinh_thanh', 'quan_huyen'])[col]
            .apply(list)
            .reset_index()
        )
        status_agg_list.append(tmp_df)
    status_agg = reduce(lambda x, y: x.merge(y, on=['tinh_thanh', 'quan_huyen'], how='outer'), status_agg_list)
    status_agg_final = pd.melt(
        status_agg, 
        id_vars = ['tinh_thanh', 'quan_huyen'], 
        value_vars =LIST_NVC,
        var_name ='nha_van_chuyen',
        value_name ='status'
    ).rename_axis(None, axis=1)

    status_agg_final['id_nvc'] = status_agg_final['nha_van_chuyen'].map(MAPPING_ID_NVC)
    status_agg_final = status_agg_final[['tinh_thanh', 'quan_huyen', 'id_nvc', 'status']]

    # Tính toán tiền giao dịch
    tien_giao_dich_final = pd.melt(
        tien_giao_dich, 
        id_vars = ['tinh_thanh', 'quan_huyen', 'ma_don_hang'], 
        value_vars =LIST_NVC,
        var_name ='nha_van_chuyen',
        value_name ='monetary'
    ).rename_axis(None, axis=1)
    tien_giao_dich_final['id_nvc'] = tien_giao_dich_final['nha_van_chuyen'].map(MAPPING_ID_NVC)
    tien_giao_dich_final = tien_giao_dich_final[['tinh_thanh', 'quan_huyen', 'ma_don_hang', 'id_nvc', 'monetary']]

    # Kết hợp dữ liệu status và tiền giao dịch
    final_df = tien_giao_dich_final.merge(status_agg_final, on=['tinh_thanh', 'quan_huyen', 'id_nvc'], how='left')

    # Lưu output dưới dạng json
    with open(ROOT_PATH + '/output/data_api_full.json', 'w', encoding='utf-8') as file:
        final_df.to_json(file, force_ascii=False)

############################################################################################################################

def out_data_api():
    
    # 1. Lấy toàn bộ data
    print('1. Lấy toàn bộ data')
    (
        ngung_giao_nhan, danh_gia_zns, 
        ti_le_giao_hang, chat_luong_noi_bo, 
        thoi_gian_giao_hang, kho_giao_nhan, 
        tien_giao_dich
    )  = total_transform()

    # 2. Xử lý ngưng giao nhận
    print('2. Xử lý ngưng giao nhận')
    ngung_giao_nhan_final = pd.melt(
        ngung_giao_nhan, 
        id_vars = ['tinh_thanh', 'quan_huyen'], 
        value_vars = STATUS_NVC,
        var_name ='nha_van_chuyen',
        value_name ='status'
    ).rename_axis(None, axis=1)
    ngung_giao_nhan_final['id_nvc'] = ngung_giao_nhan_final['nha_van_chuyen'].str.replace('_stt', '').map(MAPPING_ID_NVC)
    ngung_giao_nhan_final = ngung_giao_nhan_final[['tinh_thanh', 'quan_huyen', 'id_nvc', 'status']]
    assert ngung_giao_nhan_final[['tinh_thanh', 'quan_huyen']].drop_duplicates().shape[0] == province_district_norm_df.shape[0], 'Tính toán dữ liệu sai'

    # 3. Xử lý data tiền giao dịch
    print('3. Xử lý data tiền giao dịch')
    tien_giao_dich_final = pd.melt(
        tien_giao_dich, 
        id_vars = ['tinh_thanh', 'quan_huyen', 'ma_don_hang', 'loai'], 
        value_vars =LIST_NVC,
        var_name ='nha_van_chuyen',
        value_name ='monetary'
    ).rename_axis(None, axis=1)
    tien_giao_dich_final['id_nvc'] = tien_giao_dich_final['nha_van_chuyen'].map(MAPPING_ID_NVC)
    tien_giao_dich_final['loai'] = tien_giao_dich_final['loai'].map({
        'noi_mien': 'Nội Miền',
        'can_mien': 'Cận Miền',
        'noi_thanh_tinh': 'Nội Thành Tỉnh',
        'ngoai_thanh_tinh': 'Ngoại Thành Tỉnh',
        'noi_thanh_tphcm_hn': 'Nội Thành Tỉnh',
        'ngoai_thanh_tphcm_hn': 'Ngoại Thành Tỉnh', 
    })
    tien_giao_dich_final = tien_giao_dich_final[['tinh_thanh', 'quan_huyen', 'ma_don_hang', 'id_nvc', 'loai', 'monetary']]

    # 4. Xử lý data thời gian giao dịch
    print('4. Xử lý data thời gian giao dịch')
    LOAI_VAN_CHUYEN_DICT = {
        'Nội Miền': 'Nội Miền',
        'Nội Miền Đặc Biệt': 'Nội Miền',
        'Liên Miền': 'Cận Miền',
        'Liên Miền Đặc Biệt': 'Cận Miền',
        'Liên Vùng': 'Cận Miền',
        'Nội Tỉnh': 'Ngoại Thành Tỉnh',
        'Nội Thành': 'Nội Thành Tỉnh',
    }
    
    THOI_GIAN_GIAO_HANG_DEFAULT = {
        'Nội Miền': '2-4 ngày',
        'Cận Miền': '3-5 ngày',
        'Nội Thành Tỉnh': '1-3 ngày',
        'Ngoại Thành Tỉnh': '1-3 ngày',
    }
    
    giao_dich_valid = pd.read_parquet(ROOT_PATH + '/processed_data/giao_dich_combine_valid.parquet')
    # Xử lý data
    giao_dich_valid = giao_dich_valid[giao_dich_valid['trang_thai_van_don'].isin([
        'Giao hàng thành công',
        'Đã hoàn thành',
        'Delivered | Giao hàng thành công',
        'Thành công - Phát thành công',
        'Đã giao hàng/Chưa đối soát',
        'Đã đối soát',
    ])]
    
    giao_dich_valid['nha_van_chuyen'] = giao_dich_valid['nha_van_chuyen'].map({
        'BEST Express': 'best',
        'Ninja Van': 'ninja_van',
        'GHN': 'ghn',
        'Shopee Express': 'shopee_express',
        'Viettel Post': 'viettel_post',
        'GHTK': 'ghtk',
        'TikiNow': 'tikinow',
    })
    thoi_gian_giao_hang_df = giao_dich_valid[[
        'tao_luc', 'ma_don_hang', 'nha_van_chuyen',
        'tinh_thanh_giao_hang', 'quan_huyen_giao_hang',
        'so_lan_giao', 'hinh_thuc_gui_hang', 'co_hang_doi_tra',
        'giao_luc', 'loai'
    ]].rename(columns={'tinh_thanh_giao_hang': 'tinh_thanh', 'quan_huyen_giao_hang': 'quan_huyen'})
    
    thoi_gian_giao_hang_df['loai'] = thoi_gian_giao_hang_df['loai'].map(LOAI_VAN_CHUYEN_DICT)
    thoi_gian_giao_hang_df = thoi_gian_giao_hang_df.loc[thoi_gian_giao_hang_df['giao_luc'].notna()]
    thoi_gian_giao_hang_df['thoi_gian_giao_hang'] = (
        thoi_gian_giao_hang_df['giao_luc'] - thoi_gian_giao_hang_df['tao_luc']
    ).astype('timedelta64[h]')
    
    # Transform bảng
    thoi_gian_giao_hang_final = (
        thoi_gian_giao_hang_df
        .groupby(['tinh_thanh', 'quan_huyen', 'nha_van_chuyen', 'loai'])
        .agg(estimate_delivery_time_h=('thoi_gian_giao_hang', 'mean'))
        .reset_index()
    )
    thoi_gian_giao_hang_final['id_nvc'] = thoi_gian_giao_hang_final['nha_van_chuyen'].map(MAPPING_ID_NVC)
    thoi_gian_giao_hang_final['estimate_delivery_time'] = (
        thoi_gian_giao_hang_final['estimate_delivery_time_h'].apply(lambda hour: str(int(hour/24)) + ' - ' + str(int(hour/24)+2) + ' ngày')
    )
    thoi_gian_giao_hang_final = thoi_gian_giao_hang_final[[
        'tinh_thanh', 'quan_huyen', 'id_nvc', 'loai', 
        'estimate_delivery_time_h', 'estimate_delivery_time'
    ]]
    
    # Thời gian giao hàng default
    nvc_df = pd.DataFrame(data={
        'id_nvc': list(MAPPING_ID_NVC.values()),
    })
    loai_van_chuyen_df = pd.DataFrame(THOI_GIAN_GIAO_HANG_DEFAULT.items(), columns=['loai', 'default_delivery_time'])
    loai_van_chuyen_df['default_delivery_time_h'] = [72, 96, 48, 48]
    
    thoi_gian_giao_hang_default = (
        province_district_norm_df
        .merge(
            nvc_df.merge(loai_van_chuyen_df, how='cross'), 
            how='cross'
        )
    )
    
    thoi_gian_giao_hang_final = (
        thoi_gian_giao_hang_default.merge(thoi_gian_giao_hang_final, on=['tinh_thanh', 'quan_huyen', 'id_nvc', 'loai'], how='left')
    )
    thoi_gian_giao_hang_final.loc[
        thoi_gian_giao_hang_final['estimate_delivery_time'].isna(), 
        'estimate_delivery_time'
    ] = thoi_gian_giao_hang_final['default_delivery_time']
    
    thoi_gian_giao_hang_final.loc[
        thoi_gian_giao_hang_final['estimate_delivery_time_h'].isna(), 
        'estimate_delivery_time_h'
    ] = thoi_gian_giao_hang_final['default_delivery_time_h']

    # 5. Xủ lý score (
        # zns_score, ti_le_giao_hang_score, chat_luong_noi_bo_score, 
        # thoi_gian_giao_hang_score, kho_giao_nhan_score
    # )
    print('5. Xủ lý score')
    score_df_list = []
    
    for target_df in [danh_gia_zns, ti_le_giao_hang, chat_luong_noi_bo, thoi_gian_giao_hang, kho_giao_nhan]:
        for col in LIST_NVC:
            target_df[col + '_score'] = target_df[col + '_score']*target_df['trong_so']
        
        target_final_df = pd.melt(
            target_df, 
            id_vars = ['tinh_thanh', 'quan_huyen'], 
            value_vars = SCORE_NVC,
            var_name ='nha_van_chuyen',
            value_name ='score'
        ).rename_axis(None, axis=1)
        target_final_df['id_nvc'] = target_final_df['nha_van_chuyen'].str.replace('_score', '').map(MAPPING_ID_NVC)
        
        score_df_list.append(target_final_df[['tinh_thanh', 'quan_huyen', 'id_nvc', 'score']])
        
    score_df = pd.concat(score_df_list, ignore_index=False)
    score_final = score_df.groupby(['tinh_thanh', 'quan_huyen', 'id_nvc']).mean().reset_index()
    # score_final['score'] = score_final['score']/score_final['score'].max()
    q_lower = score_final['score'].quantile(0.005)
    q_upper = score_final['score'].quantile(0.995)
    score_final.loc[score_final['score'] < q_lower, 'score'] = q_lower
    score_final.loc[score_final['score'] > q_upper, 'score'] = q_upper
    score_final['score'] = (score_final['score'] - q_lower)/(q_upper - q_lower)
    
    score_final['stars'] = 1
    score_final.loc[score_final['score'] > 0.15, 'stars'] = 2
    score_final.loc[score_final['score'] > 0.3, 'stars'] = 3
    score_final.loc[score_final['score'] > 0.5, 'stars'] = 4
    score_final.loc[score_final['score'] > 0.8, 'stars'] = 5

    # 6. Combine api data
    print('6. Combine api data')
    api_data_final = (
        ngung_giao_nhan_final
        .merge(thoi_gian_giao_hang_final, on=['tinh_thanh', 'quan_huyen', 'id_nvc'], how='inner')
        .merge(score_final, on=['tinh_thanh', 'quan_huyen', 'id_nvc'], how='inner')
    )
    api_data_final = tien_giao_dich_final.merge(api_data_final, on=['tinh_thanh', 'quan_huyen', 'id_nvc', 'loai'], how='left')
    assert len(api_data_final) == len(tien_giao_dich_final), 'Transform data không chính xác'

    # 7. Processing api data
    print('7. Processing api data')
    re_nhat_df = api_data_final.groupby(['ma_don_hang'])['monetary'].min().reset_index()
    re_nhat_df['notification'] = 'Rẻ nhất'
    re_nhat_df = re_nhat_df.merge(api_data_final, on=['ma_don_hang', 'monetary'], how='inner')
    
    api_data_final1 = merge_left_only(api_data_final, re_nhat_df, keys=['ma_don_hang', 'monetary'])
    
    nhanh_nhat_df = api_data_final1.groupby(['ma_don_hang'])['estimate_delivery_time_h'].min().reset_index()
    nhanh_nhat_df['notification'] = 'Nhanh nhất'
    nhanh_nhat_df = nhanh_nhat_df.merge(api_data_final1, on=['ma_don_hang', 'estimate_delivery_time_h'], how='inner')
    
    api_data_final2 = merge_left_only(api_data_final1, nhanh_nhat_df, keys=['ma_don_hang', 'estimate_delivery_time_h'])
    
    hieu_qua_nhat_df = api_data_final2.groupby(['ma_don_hang'])['score'].max().reset_index()
    hieu_qua_nhat_df['notification'] = 'Hiệu quả nhất'
    hieu_qua_nhat_df = hieu_qua_nhat_df.merge(api_data_final2, on=['ma_don_hang', 'score'], how='inner')
    
    api_data_final3 = merge_left_only(api_data_final2, hieu_qua_nhat_df, keys=['ma_don_hang', 'score'])
    
    gia_tot_df = api_data_final3.groupby(['ma_don_hang'])['monetary'].min().reset_index()
    gia_tot_df['notification'] = 'Giá tốt'
    gia_tot_df = gia_tot_df.merge(api_data_final3, on=['ma_don_hang', 'monetary'], how='inner')
    
    api_data_final4 = merge_left_only(api_data_final3, gia_tot_df, keys=['ma_don_hang', 'monetary'])
    
    dich_vu_tot_df = api_data_final4.groupby(['ma_don_hang'])['score'].max().reset_index()
    dich_vu_tot_df['notification'] = 'Dịch vụ tốt'
    dich_vu_tot_df = dich_vu_tot_df.merge(api_data_final4, on=['ma_don_hang', 'score'], how='inner')
    
    api_data_final5 = merge_left_only(api_data_final4, dich_vu_tot_df, keys=['ma_don_hang', 'score'])
    api_data_final5['notification'] = 'Bình thường'

    api_data_final = pd.concat([
        re_nhat_df,
        nhanh_nhat_df,
        hieu_qua_nhat_df,
        gia_tot_df,
        dich_vu_tot_df,
        api_data_final5
    ], ignore_index=True)
    api_data_final = api_data_final[[
        'tinh_thanh', 'quan_huyen', 'ma_don_hang', 'id_nvc',
        'loai', 'status', 'monetary', 'estimate_delivery_time', 
        'score', 'stars', 'notification'
    ]]

    assert api_data_final.isna().sum().all() == 0, 'Transform data không chính xác'

    # Lưu output dưới dạng json
    with open(ROOT_PATH + '/output/data_api.json', 'w', encoding='utf-8') as file:
        api_data_final.to_json(file, force_ascii=False)

if __name__=="__main__":
    
    out_data_api_full()
    out_data_api()
    