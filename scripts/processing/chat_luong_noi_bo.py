from scripts.utilities.helper import *


def get_pct_ninja_van(s):
    if '<=' in s:
        return int(s.split('<=')[1].split('%')[0]) / 100
    elif '-' in s:
        first = int(s.split('-')[0].strip().split('%')[0])
        second = int(s.split('-')[1].strip().split('%')[0])
        return (first + second) / 2.0 / 100
    else:
        return 0


def xu_ly_chat_luong_noi_bo_old():
    # 1. Đọc data raw
    try:
        clnb_njv_df = pd.read_excel(ROOT_PATH + '/user_input/chat_luong_noi_bo_njv.xlsx')
    except FileNotFoundError:
        print(f"Error: The file {ROOT_PATH}/user_input/chat_luong_noi_bo_njv.xlsx was not found. Use file {ROOT_PATH}/input/chat_luong_noi_bo_njv.xlsx instead.")
        clnb_njv_df = pd.read_excel(ROOT_PATH + '/input/chat_luong_noi_bo_njv.xlsx')
    clnb_njv_df = clnb_njv_df[1:]
    clnb_njv_df.columns = [
        'region', 'receiver_province', 'id_receiver_district', 'receiver_district',
        'short_receiver_district', 'njv_post_office', 'delivery_success_rate', 'is_more_than_100'
    ]
    clnb_njv_df = clnb_njv_df[[
        'receiver_province', 'receiver_district',
        'njv_post_office', 'delivery_success_rate', 'is_more_than_100'
    ]]

    # 2. Xử lý data
    clnb_njv_df.loc[clnb_njv_df['is_more_than_100'].isna(), 'is_more_than_100'] = False
    clnb_njv_df['is_more_than_100'] = clnb_njv_df['is_more_than_100'].astype(bool)
    clnb_njv_df['njv_post_office'] = clnb_njv_df['njv_post_office'].astype(str).apply(lambda x: x.replace('\xa0', ' '))

    # 3. Tách percentage
    clnb_njv_df['delivery_success_rate'] = clnb_njv_df['delivery_success_rate'].astype(str).apply(get_pct_ninja_van)

    # 4. Chuẩn hóa tên quận/huyện, tỉnh/thành
    clnb_njv_df = normalize_province_district(
        clnb_njv_df,
        tinh_thanh='receiver_province',
        quan_huyen='receiver_district'
    )
    clnb_njv_df = clnb_njv_df.loc[clnb_njv_df['receiver_province'].notna() & clnb_njv_df['receiver_district'].notna()]

    return clnb_njv_df


def xu_ly_chat_luong_noi_bo():

    # 1. Dữ liệu chất lượng nội bộ cũ
    old_njv = xu_ly_chat_luong_noi_bo_old()

    # 2. Dữ liệu chất lượng nội bộ mới
    try:
        raw_njv = pd.read_excel(ROOT_PATH + '/user_input/rst_cao_njv.xlsx')
    except FileNotFoundError:
        print(f"Error: The file {ROOT_PATH}/user_input/rst_cao_njv.xlsx was not found. Use file {ROOT_PATH}/input/rst_cao_njv.xlsx instead.")
        raw_njv = pd.read_excel(ROOT_PATH + '/input/rst_cao_njv.xlsx')

    raw_njv.columns = ['receiver_province', 'njv_post_office', 'delivery_failed_rate']
    raw_njv['njv_post_office'] = raw_njv['njv_post_office'].astype(str).apply(lambda x: x.replace('\xa0', ' '))

    new_njv = (
        raw_njv
        .sort_values('delivery_failed_rate', ascending=False)
        .drop_duplicates(subset=['receiver_province', 'njv_post_office'], keep='first')
    )

    # 3. Xử lý phần giao nhau
    new_njv1 = old_njv.merge(new_njv[['njv_post_office', 'delivery_failed_rate']], on='njv_post_office', how='inner')

    # 3.1. Tạo cột tmp_district
    new_njv1['tmp_district'] = new_njv1['receiver_district'].str.strip().str.title()
    new_njv1['tmp_district'] = new_njv1['tmp_district'].apply(unidecode)
    new_njv1['tmp_district'] = (
        new_njv1['tmp_district']
        .str.replace('Quan ', '')
        .str.replace('Huyen ', '')
        .str.replace('Thi Xa ', '')
        .str.replace('Thanh Pho ', '')
        .str.replace('.', '')
        .str.replace(',', '')
    )

    # 3.2. Tạo cột tmp_post_office
    new_njv1['tmp_post_office'] = new_njv1['njv_post_office'].str.split('-').str[1]
    new_njv1['tmp_post_office'] = new_njv1['tmp_post_office'].str.strip()

    # 3.3. Lấy đúng office thuộc quận/huyện
    new_njv1 = new_njv1.loc[new_njv1['tmp_district'] == new_njv1['tmp_post_office']]

    # 3.4. Update delivery_success_rate từ delivery_failed_rate
    new_njv1['delivery_success_rate'] = 1 - new_njv1['delivery_failed_rate']

    # 3.5. Chọn thông tin cần thiết
    new_njv1 = new_njv1[['receiver_province', 'receiver_district', 'njv_post_office', 'delivery_success_rate', 'is_more_than_100']]

    # 4. Xử lý phần riêng
    new_njv2 = new_njv.loc[~new_njv['njv_post_office'].isin(new_njv1['njv_post_office'])]

    # 4.1. Xử lý thông tin cần thiết
    new_njv2['receiver_district'] = new_njv2['njv_post_office'].str.split('-').str[1]
    new_njv2['receiver_district'] = new_njv2['receiver_district'].str.strip()

    new_njv2['delivery_success_rate'] = 1 - new_njv2['delivery_failed_rate']

    # 4.2. Chuẩn hóa tên quận/huyện, tỉnh/thành
    new_njv2 = normalize_province_district(
        new_njv2,
        tinh_thanh='receiver_province',
        quan_huyen='receiver_district'
    )
    new_njv2 = new_njv2.loc[new_njv2['receiver_province'].notna() & new_njv2['receiver_district'].notna()]

    new_njv2 = new_njv2.merge(
        old_njv[['receiver_province', 'receiver_district', 'is_more_than_100']],
        on=['receiver_province', 'receiver_district'],
        how='inner'
    )
    # new_njv2['is_more_than_100'] = True

    # 4.3. Chọn thông tin cần thiết
    new_njv2 = new_njv2[[
        'receiver_province', 'receiver_district',
        'njv_post_office', 'delivery_success_rate', 'is_more_than_100'
    ]]

    # 5. Tổng hợp thông tin
    clnb_njv_df = pd.concat([new_njv1, new_njv2, old_njv], ignore_index=True)
    clnb_njv_df = clnb_njv_df.drop_duplicates(subset=['receiver_province', 'receiver_district'], keep='first')
    clnb_njv_df.to_parquet(ROOT_PATH + '/processed_data/chat_luong_noi_bo_njv.parquet', index=False)