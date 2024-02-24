import io

import psycopg2

from config import settings
from scripts.utilities.helper import *


@st.cache_data
def st_get_optimal_score():
    try:
        optimal_score_df = pd.read_parquet(ROOT_PATH + '/output/total_optimal_score.parquet')
        score = optimal_score_df.tail(1)['score'].values[0]
    except:
        score = 0
    return score


@st.cache_data
def st_get_province_mapping_district():
    return pd.read_parquet(ROOT_PATH + '/input/province_mapping_district.parquet')


@st.cache_data
def st_get_data_zns():
    return pd.read_parquet(ROOT_PATH + '/processed_data/danh_gia_zns.parquet')


@st.cache_data
def st_get_data_order():
    df_order = pd.read_parquet(
        ROOT_PATH + '/processed_data/order.parquet', columns=[
            'created_at',
            'order_code',
            'carrier',
            'weight',
            'sender_province',
            'sender_district',
            'receiver_province',
            'receiver_district',
            'carrier_status',
            'order_type',
            'delivery_type',
            'picked_at',
            'last_delivering_at',
            'carrier_delivered_at'
        ]
    )
    return df_order


@st.cache_data(experimental_allow_widgets=True)
def save_excel(df, key):
    # buffer to use for excel writer
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)

    buffer.seek(0)  # Move the buffer position to the beginning before downloading
    st.download_button(
        label="📥 Download data as Excel",
        data=buffer,
        file_name='data.xlsx',
        mime='application/vnd.ms-excel',
        key=key
    )


@st.cache_data
def st_get_don_ton_dong(run_date_str, n_days_back=30):
    run_date = datetime.strptime(run_date_str, '%Y-%m-%d')

    loai_van_chuyen_df = pd.DataFrame(THOI_GIAN_GIAO_HANG_DEFAULT.items(),
                                      columns=['order_type', 'default_delivery_time'])
    loai_van_chuyen_df['default_delivery_time_details'] = [48 + 12, 48 + 12, 48 + 12, 48 + 12, 24 + 12, 48 + 12,
                                                           72 + 12, 72 + 12, 72 + 12, 108 + 12]

    df_order = pd.read_parquet(ROOT_PATH + '/processed_data/order.parquet')
    df_order = df_order.sort_values('date', ascending=False).drop_duplicates('order_code', keep='first')
    df_order = df_order.loc[df_order['created_at'] >= (run_date - timedelta(days=n_days_back))]
    df_order = df_order[[
        'order_code', 'carrier', 'receiver_province', 'receiver_district',
        'order_type', 'picked_at', 'last_delivering_at'
    ]]

    max_delivering_time = df_order['last_delivering_at'].max()
    df_order['last_delivering_at'] = df_order['last_delivering_at'].fillna(max_delivering_time)
    df_order['delta_time_h'] = (df_order['last_delivering_at'] - df_order[
        'picked_at']).dt.total_seconds() / 60 / 60

    df_order = df_order.merge(loai_van_chuyen_df[['order_type', 'default_delivery_time_details']],
                              on='order_type', how='inner')
    df_order['is_late'] = df_order['delta_time_h'] > df_order['default_delivery_time_details']
    df_order_analytic = df_order.groupby(['receiver_province', 'receiver_district', 'carrier', 'order_type']).agg(
        n_order_late=('is_late', 'sum')).reset_index()
    df_order_analytic = df_order_analytic.loc[df_order_analytic['n_order_late'] > 0]

    return df_order_analytic


@st.cache_data
def st_get_data_viz():
    viz_df1 = pd.read_parquet(ROOT_PATH + '/output/st_data_visualization_p1.parquet')
    viz_df2 = pd.read_parquet(ROOT_PATH + '/output/st_data_visualization_p2.parquet')
    return viz_df1, viz_df2


# function support streamlit render
def save_uploaded_file(uploaded_file, folder):
    with open(os.path.join(folder, uploaded_file.name), "wb") as f:
        f.write(uploaded_file.getbuffer())
    return st.success("Saved File:{} to {}".format(folder, uploaded_file.name))


def get_st_dataframe_from_db(
        sender_province_code, sender_district_code,
        receiver_province_code, receiver_district_code,
        weight, pickup,
        item_price, money_get_first, is_returned
):
    # Create connection
    connection = psycopg2.connect(
        settings.SQLALCHEMY_DATABASE_URI
    )

    cursor = connection.cursor()

    table_query = QUERY_SQL_COMMAND_STREAMLIT.format(
        item_price, money_get_first, is_returned,
        sender_province_code, sender_district_code,
        receiver_province_code, receiver_district_code,
        weight, pickup
    )

    cursor.execute(table_query)
    result = cursor.fetchall()

    columns = [description[0] for description in cursor.description]
    result_df = pd.DataFrame(result, columns=columns)

    # Commit the transaction
    connection.commit()

    cursor.close()
    connection.close()

    return result_df
