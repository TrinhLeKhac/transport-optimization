from scripts.utilities.helper import *


def xu_ly_ngung_giao_nhan():
    # Đọc data ngưng giao nhận
    ngung_giao_nhan_df = pd.read_excel(ROOT_PATH + '/input/ngung_giao_nhan.xlsx')

    # Chọn lấy cột cần thiết và đổi tên cột
    ngung_giao_nhan_df.columns = [
        'id', 'id_receiver_district', 'receiver_province', 'receiver_district', 'short_receiver_district',
        'Ninja Van', 'GHN', 'BEST Express', 'SPX Express', 'GHTK', 'Viettel Post',
    ]
    ngung_giao_nhan_df = ngung_giao_nhan_df[['receiver_province', 'receiver_district',
                                             'Ninja Van', 'GHN', 'BEST Express', 'SPX Express', 'GHTK', 'Viettel Post']]

    # Chuẩn hóa thông tin quận/huyện, tỉnh/thành
    ngung_giao_nhan_df = normalize_province_district(ngung_giao_nhan_df, tinh_thanh='receiver_province',
                                                     quan_huyen='receiver_district')
    ngung_giao_nhan_filter_df = ngung_giao_nhan_df.loc[
        ngung_giao_nhan_df['receiver_province'].notna()
        & ngung_giao_nhan_df['receiver_district'].notna()
    ]

    assert len(ngung_giao_nhan_df) == len(ngung_giao_nhan_filter_df), 'File Excel cung cấp thông tin sai format tỉnh/thành, quận/huyện'

    ngung_giao_nhan_final_df = pd.melt(
        ngung_giao_nhan_filter_df,
        id_vars=['receiver_province', 'receiver_district'],
        value_vars=[
            'Ninja Van', 'GHN', 'BEST Express', 'SPX Express', 'GHTK', 'Viettel Post'
        ],
        var_name='carrier', value_name='status'
    )

    set_carrier = set(ngung_giao_nhan_final_df['carrier'].unique().tolist())
    set_norm_full_carrier = set(MAPPING_CARRIER_ID.keys())
    assert set_carrier - set_norm_full_carrier == set(), 'Ops, Tên nhà vận chuyển chưa được chuẩn hóa'

    # Lưu thông tin
    ngung_giao_nhan_final_df.to_parquet(ROOT_PATH + '/processed_data/ngung_giao_nhan.parquet', index=False)


def xu_ly_ngung_giao_nhan_2():
    # Đọc data shopee ngưng giao nhận
    ngung_giao_nhan_df = pd.read_excel(ROOT_PATH + '/input/shopee_ngung_giao_nhan.xlsx', header=None)

    ngung_giao_nhan_df.columns = ['country', 'receiver_province', 'receiver_district', 'receiver_commune']
    ngung_giao_nhan_df['status'] = 'Quá tải'

    # Chuẩn hoá thông tin tỉnh/thành, quận/huyện, phường/xã
    ngung_giao_nhan_final_df = normalize_province_district_ward(ngung_giao_nhan_df, tinh_thanh='receiver_province',
                                                                quan_huyen='receiver_district',
                                                                phuong_xa='receiver_commune')
    ngung_giao_nhan_final_df = PROVINCE_MAPPING_DISTRICT_MAPPING_WARD_DF.merge(ngung_giao_nhan_final_df, on=['receiver_province', 'receiver_district', 'receiver_commune'], how='left')
    ngung_giao_nhan_final_df['carrier'] = 'SPX Express'
    ngung_giao_nhan_final_df = ngung_giao_nhan_final_df[
        ['receiver_province', 'receiver_district', 'receiver_commune', 'carrier', 'status']]

    # Lưu thông tin
    ngung_giao_nhan_final_df.to_parquet(ROOT_PATH + '/processed_data/shopee_ngung_giao_nhan.parquet', index=False)
