from scripts.utilities.helper import *

COLUMNS_CUOC_PHI = ['gt', 'lt_or_eq'] + list(MAPPING_ORDER_TYPE_ID.keys()) + ['Liên Thành']


@exception_wrapper
def xu_ly_bang_gia_cuoc():
    # 1. Lấy thông tin bảng giá cước
    try:
        bang_gia_cuoc_df = pd.read_excel(ROOT_PATH + '/user_input/bang_cuoc_phi.xlsx')
    except FileNotFoundError:
        print(
            f"Warning: The file {ROOT_PATH}/user_input/bang_gia_cuoc.xlsx was not found. Use file {ROOT_PATH}/input/bang_gia_cuoc.xlsx instead.")
        bang_gia_cuoc_df = pd.read_excel(ROOT_PATH + '/input/bang_cuoc_phi.xlsx')

    # 2.1 Tách lấy thông tin bảng giá cước Ninja Van và xử lý
    ninja_van_df = pd.concat([bang_gia_cuoc_df.iloc[1:101, :2], bang_gia_cuoc_df.iloc[1:101, 2:13]],
                             axis=1).reset_index(
        drop=True)
    ninja_van_df.columns = COLUMNS_CUOC_PHI
    ninja_van_df['carrier'] = 'Ninja Van'
    ninja_van_df['carrier_id'] = 7

    # 2.2 Tách lấy thông tin bảng giá cước BEST Express và xử lý
    best_df = pd.concat([bang_gia_cuoc_df.iloc[1:101, :2], bang_gia_cuoc_df.iloc[1:101, 13:24]], axis=1).reset_index(
        drop=True)
    best_df.columns = COLUMNS_CUOC_PHI
    best_df['carrier'] = 'BEST Express'
    best_df['carrier_id'] = 6

    # 2.3 Tách lấy thông tin bảng giá cước SPX Express và xử lý
    shopee_express_df = pd.concat([bang_gia_cuoc_df.iloc[1:101, :2], bang_gia_cuoc_df.iloc[1:101, 24:35]],
                                  axis=1).reset_index(drop=True)
    shopee_express_df.columns = COLUMNS_CUOC_PHI
    shopee_express_df['carrier'] = 'SPX Express'
    shopee_express_df['carrier_id'] = 10

    # 2.4 Tách lấy thông tin bảng giá cước GHN và xử lý
    ghn_df = pd.concat([bang_gia_cuoc_df.iloc[1:101, :2], bang_gia_cuoc_df.iloc[1:101, 35:46]], axis=1).reset_index(
        drop=True)
    ghn_df.columns = COLUMNS_CUOC_PHI
    ghn_df['carrier'] = 'GHN'
    ghn_df['carrier_id'] = 2

    # 2.5 Tách lấy thông tin bảng giá cước Viettel Post và xử lý
    viettel_post_df = pd.concat([bang_gia_cuoc_df.iloc[1:101, :2], bang_gia_cuoc_df.iloc[1:101, 46:57]],
                                axis=1).reset_index(drop=True)
    viettel_post_df.columns = COLUMNS_CUOC_PHI
    viettel_post_df['carrier'] = 'Viettel Post'
    viettel_post_df['carrier_id'] = 4

    # 2.6 Tách lấy thông tin bảng giá cước GHTK và xử lý
    ghtk_df = pd.concat([bang_gia_cuoc_df.iloc[1:101, :2], bang_gia_cuoc_df.iloc[1:101, 57:68]], axis=1).reset_index(
        drop=True)
    ghtk_df.columns = COLUMNS_CUOC_PHI
    ghtk_df['carrier'] = 'GHTK'
    ghtk_df['carrier_id'] = 1

    # 2.7 Tách lấy thông tin bảng giá cước VNPost và xử lý
    vnpost_df = pd.concat([bang_gia_cuoc_df.iloc[1:101, :2], bang_gia_cuoc_df.iloc[1:101, 79:90]],
                          axis=1).reset_index(
        drop=True)
    vnpost_df.columns = COLUMNS_CUOC_PHI
    vnpost_df['carrier'] = 'VNPost'
    vnpost_df['carrier_id'] = 13

    # 2.8 Tách lấy thông tin bảng giá cước Lazada Logistics và xử lý
    lazada_df = pd.concat([bang_gia_cuoc_df.iloc[1:101, :2], bang_gia_cuoc_df.iloc[1:101, 90:101]],
                          axis=1).reset_index(
        drop=True)
    lazada_df.columns = COLUMNS_CUOC_PHI
    lazada_df['carrier'] = 'Lazada Logistics'
    lazada_df['carrier_id'] = 14

    # 3. Tổng hợp thông tin
    cuoc_phi_df = pd.concat(
        [ninja_van_df, best_df, shopee_express_df, ghn_df, viettel_post_df, ghtk_df, vnpost_df, lazada_df],
        ignore_index=True)
    cuoc_phi_df = cuoc_phi_df[['carrier_id', 'carrier'] + COLUMNS_CUOC_PHI]
    cuoc_phi_df = cuoc_phi_df.set_index(['carrier_id', 'carrier', 'gt', 'lt_or_eq'])
    cuoc_phi_df = (cuoc_phi_df * 1000).astype(int).reset_index()
    cuoc_phi_df = pd.melt(
        cuoc_phi_df,
        id_vars=['carrier_id', 'carrier', 'gt', 'lt_or_eq'],
        value_vars=list(MAPPING_ORDER_TYPE_ID.keys()) + ['Liên Thành'],
        var_name='order_type', value_name='service_fee'
    )

    # 3. Check tên nhà vận chuyển đã chuẩn hóa chưa
    set_carrier = set(cuoc_phi_df['carrier'].unique().tolist())
    set_norm_full_carrier = set(MAPPING_CARRIER_ID.keys())
    assert set_carrier - set_norm_full_carrier == set(), 'Ops, Tên nhà vận chuyển chưa được chuẩn hóa'

    # 4. Lưu thông tin đã xử lý
    cuoc_phi_df.to_parquet(ROOT_PATH + '/processed_data/cuoc_phi.parquet', index=False)
