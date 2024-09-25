from scripts.utilities.helper import *


@exception_wrapper
def xu_ly_ngung_giao_nhan():
    # Đọc data ngưng giao nhận
    try:
        ngung_giao_nhan_df = pd.read_excel(ROOT_PATH + '/user_input/ngung_giao_nhan.xlsx')
    except FileNotFoundError:
        print(f"Error: The file {ROOT_PATH}/user_input/ngung_giao_nhan.xlsx was not found. Use file {ROOT_PATH}/input/ngung_giao_nhan.xlsx instead.")
        ngung_giao_nhan_df = pd.read_excel(ROOT_PATH + '/input/ngung_giao_nhan.xlsx')

    # Chọn lấy cột cần thiết và đổi tên cột
    ngung_giao_nhan_df.columns = [
        'id', 'id_receiver_district', 'receiver_province', 'receiver_district', 'short_receiver_district',
        'Ninja Van', 'GHN', 'BEST Express', 'SPX Express', 'GHTK', 'Viettel Post', 'VNPost', 'Lazada Logistics'
    ]
    ngung_giao_nhan_df = ngung_giao_nhan_df[['receiver_province', 'receiver_district',
                                             'Ninja Van', 'GHN', 'BEST Express', 'SPX Express', 'GHTK', 'Viettel Post', 'VNPost', 'Lazada Logistics']]

    # Chuẩn hóa thông tin quận/huyện, tỉnh/thành
    ngung_giao_nhan_df = normalize_province_district(ngung_giao_nhan_df, tinh_thanh='receiver_province',
                                                     quan_huyen='receiver_district')
    ngung_giao_nhan_filter_df = ngung_giao_nhan_df.loc[
        ngung_giao_nhan_df['receiver_province'].notna()
        & ngung_giao_nhan_df['receiver_district'].notna()
    ]

    # assert len(ngung_giao_nhan_df) == len(ngung_giao_nhan_filter_df), 'File Excel cung cấp thông tin sai format tỉnh/thành, quận/huyện'

    ngung_giao_nhan_final_df = pd.melt(
        ngung_giao_nhan_filter_df,
        id_vars=['receiver_province', 'receiver_district'],
        value_vars=[
            'Ninja Van', 'GHN', 'BEST Express', 'SPX Express', 'GHTK', 'Viettel Post', 'VNPost', 'Lazada Logistics'
        ],
        var_name='carrier', value_name='status'
    )

    set_carrier = set(ngung_giao_nhan_final_df['carrier'].unique().tolist())
    set_norm_full_carrier = set(MAPPING_CARRIER_ID.keys())
    assert set_carrier - set_norm_full_carrier == set(), 'Ops, Tên nhà vận chuyển chưa được chuẩn hóa'
    ngung_giao_nhan_final_df.loc[ngung_giao_nhan_final_df['status'].notna(), 'status'] = 'Quá tải'

    # Lưu thông tin
    ngung_giao_nhan_final_df.to_parquet(ROOT_PATH + '/processed_data/ngung_giao_nhan.parquet', index=False)


@exception_wrapper
def xu_ly_ngung_giao_nhan_shopee():
    # Đọc data shopee ngưng giao nhận
    try:
        ngung_giao_nhan_df = pd.read_excel(ROOT_PATH + '/user_input/shopee_ngung_giao_nhan.xlsx', header=None)
    except FileNotFoundError:
        print(f"Error: The file {ROOT_PATH}/user_input/shopee_ngung_giao_nhan.xlsx was not found. Use file {ROOT_PATH}/input/shopee_ngung_giao_nhan.xlsx instead.")
        ngung_giao_nhan_df = pd.read_excel(ROOT_PATH + '/input/shopee_ngung_giao_nhan.xlsx', header=None)

    ngung_giao_nhan_df.columns = ['country', 'receiver_province', 'receiver_district', 'receiver_commune']
    ngung_giao_nhan_df['status'] = 'Quá tải'

    # Chuẩn hoá thông tin tỉnh/thành, quận/huyện, phường/xã
    ngung_giao_nhan_final_df = normalize_province_district_ward(ngung_giao_nhan_df, tinh_thanh='receiver_province',
                                                                quan_huyen='receiver_district',
                                                                phuong_xa='receiver_commune')

    # sort_values theo status, giá trị 'Quá Tải' xếp trên giá trị None
    ngung_giao_nhan_final_df = ngung_giao_nhan_final_df.sort_values('status').drop_duplicates(
        ['receiver_province', 'receiver_district', 'receiver_commune'], keep='first')

    # Mapping thông tin
    mapping_address = PROVINCE_MAPPING_DISTRICT_MAPPING_WARD_DF[['province', 'district', 'commune']]
    mapping_address.columns = ['receiver_province', 'receiver_district', 'receiver_commune']
    ngung_giao_nhan_final_df = mapping_address.merge(ngung_giao_nhan_final_df,
                                                     on=['receiver_province', 'receiver_district', 'receiver_commune'],
                                                     how='left')
    ngung_giao_nhan_final_df['carrier'] = 'SPX Express'
    ngung_giao_nhan_final_df = ngung_giao_nhan_final_df[
        ['receiver_province', 'receiver_district', 'receiver_commune', 'carrier', 'status']]

    # Lưu thông tin
    ngung_giao_nhan_final_df.to_parquet(ROOT_PATH + '/processed_data/shopee_ngung_giao_nhan.parquet', index=False)


@exception_wrapper
def xu_ly_ngung_giao_nhan_lazada():
    # Đọc data Lazada Logistics ngưng giao nhận
    try:
        ngung_giao_nhan_df = pd.read_excel(ROOT_PATH + '/user_input/lex_ngung_giao_nhan.xlsx', header=None)
    except FileNotFoundError:
        print(f"Error: The file {ROOT_PATH}/user_input/lex_ngung_giao_nhan.xlsx was not found. Use file {ROOT_PATH}/input/shopee_ngung_giao_nhan.xlsx instead.")
        ngung_giao_nhan_df = pd.read_excel(ROOT_PATH + '/input/lex_ngung_giao_nhan.xlsx', header=None)

    ngung_giao_nhan_df.columns = ['receiver_province', 'receiver_district', 'receiver_commune', 'lm_coverage']
    ngung_giao_nhan_df = ngung_giao_nhan_df.loc[ngung_giao_nhan_df['lm_coverage'] == '3PLs COVERAGE']
    ngung_giao_nhan_df['status'] = 'Quá tải'

    # Chuẩn hoá thông tin tỉnh/thành, quận/huyện, phường/xã
    ngung_giao_nhan_final_df = normalize_province_district_ward(ngung_giao_nhan_df, tinh_thanh='receiver_province',
                                                                quan_huyen='receiver_district',
                                                                phuong_xa='receiver_commune')

    # sort_values theo status, giá trị 'Quá Tải' xếp trên giá trị None
    ngung_giao_nhan_final_df = ngung_giao_nhan_final_df.sort_values('status').drop_duplicates(
        ['receiver_province', 'receiver_district', 'receiver_commune'], keep='first')

    # Mapping thông tin
    mapping_address = PROVINCE_MAPPING_DISTRICT_MAPPING_WARD_DF[['province', 'district', 'commune']]
    mapping_address.columns = ['receiver_province', 'receiver_district', 'receiver_commune']
    ngung_giao_nhan_final_df = mapping_address.merge(ngung_giao_nhan_final_df,
                                                     on=['receiver_province', 'receiver_district', 'receiver_commune'],
                                                     how='left')
    ngung_giao_nhan_final_df['carrier'] = 'Lazada Logistics'
    ngung_giao_nhan_final_df = ngung_giao_nhan_final_df[
        ['receiver_province', 'receiver_district', 'receiver_commune', 'carrier', 'status']]

    # Lưu thông tin
    ngung_giao_nhan_final_df.to_parquet(ROOT_PATH + '/processed_data/lazada_ngung_giao_nhan.parquet', index=False)


@exception_wrapper
def xu_ly_ngung_giao_nhan_level_3():
    ngung_giao_nhan = pd.read_parquet(ROOT_PATH + '/processed_data/ngung_giao_nhan.parquet')

    mapping_address = PROVINCE_MAPPING_DISTRICT_MAPPING_WARD_DF[['province', 'district', 'commune']]
    mapping_address.columns = ['receiver_province', 'receiver_district', 'receiver_commune']

    ngung_giao_nhan = ngung_giao_nhan.merge(mapping_address, on=['receiver_province', 'receiver_district'], how='left')
    ngung_giao_nhan = ngung_giao_nhan[
        ['receiver_province', 'receiver_district', 'receiver_commune', 'carrier', 'status']]

    shoppe_ngung_giao_nhan = pd.read_parquet(ROOT_PATH + '/processed_data/shopee_ngung_giao_nhan.parquet')
    lazada_ngung_giao_nhan = pd.read_parquet(ROOT_PATH + '/processed_data/lazada_ngung_giao_nhan.parquet')

    ngung_giao_nhan_level_3 = pd.concat([
        shoppe_ngung_giao_nhan,
        lazada_ngung_giao_nhan,
        ngung_giao_nhan
    ]).sort_values(['status', 'receiver_province', 'receiver_district', 'receiver_commune', 'carrier']).drop_duplicates(
        subset=['receiver_province', 'receiver_district', 'receiver_commune', 'carrier'])

    ngung_giao_nhan_level_3.to_parquet(ROOT_PATH + '/processed_data/ngung_giao_nhan_level_3.parquet', index=False)
