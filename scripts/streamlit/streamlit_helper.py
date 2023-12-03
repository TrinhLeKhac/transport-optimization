from scripts.utilities.helper import *
from scripts.database.helper import *


@st.cache_data
def st_get_province_mapping_district():
    return pd.read_parquet(ROOT_PATH + '/input/province_mapping_district.parquet')


def _get_data_viz(target_df, threshold=0.6):
    good_df = target_df.loc[target_df['score'] >= threshold].sort_values(['order_code', 'price'],
                                                                         ascending=[True, True]).drop_duplicates(
        'order_code', keep='first')
    bad_df = target_df.loc[target_df['score'] < threshold].sort_values(['order_code', 'score'],
                                                                       ascending=[True, False]).drop_duplicates(
        'order_code', keep='first')
    bad_filter_df = bad_df.loc[~bad_df['order_code'].isin(good_df['order_code'])]

    print(f'n_order >= threshold: {len(good_df)}')
    print(f'n_order < threshold: {len(bad_filter_df)}')

    result_df = pd.concat([good_df, bad_filter_df], ignore_index=True)
    monetary = result_df['price'].sum()

    err_df = result_df.loc[result_df['status'].isin(['1', '2'])]
    err_df['error_type'] = err_df['description'].str.split(r' \+ ')
    err_df = err_df.explode('error_type')
    analyze_df = err_df.groupby(['carrier', 'error_type', 'order_type'])['order_code'].count().rename(
        'n_errors').reset_index()

    analyze_df['score'] = threshold
    analyze_df['monetary'] = monetary
    analyze_df['n_good_order'] = len(good_df)
    analyze_df['n_bad_order'] = len(bad_filter_df)
    analyze_df['total_error'] = len(err_df)
    analyze_df = analyze_df[[
        'score', 'monetary', 'n_good_order', 'n_bad_order', 'total_error',
        'carrier', 'error_type', 'order_type', 'n_errors'
    ]]

    return analyze_df


def get_data_viz(target_df):
    thresholds = np.linspace(0.5, 1, 101)
    analyze_df_list = []

    for th in thresholds:
        print('Threshold: ', th)
        analyze_df = _get_data_viz(target_df, th)
        analyze_df_list.append(analyze_df)
        print('-' * 100)
    total_analyze_df = pd.concat(analyze_df_list, ignore_index=True)

    return total_analyze_df


@st.cache_data
def st_get_data_viz():
    data_history_df = pd.read_parquet(ROOT_PATH + '/output/data_check_output.parquet')
    viz_df = get_data_viz(data_history_df)
    return viz_df


# function support streamlit render
def save_uploaded_file(uploaded_file, folder):
    with open(os.path.join(folder, uploaded_file.name), "wb") as f:
        f.write(uploaded_file.getbuffer())
    return st.success("Saved File:{} to {}".format(folder, uploaded_file.name))


def get_st_dataframe_from_db(
        sender_province_code, sender_district_code,
        receiver_province_code, receiver_district_code,
        weight, pickup
):
    # Create connection
    connection = psycopg2.connect(
        settings.SQLALCHEMY_DATABASE_URI
    )

    cursor = connection.cursor()

    table_query = """
        WITH carrier_information AS (
            SELECT 
            tbl_ord.carrier_id, tbl_ord.route_type, 
            tbl_fee.price, 
            tbl_api.status, tbl_api.description, tbl_api.time_data,
            tbl_api.time_display, tbl_api.rate, tbl_api.score, tbl_api.star, 
            tbl_api.for_shop, tbl_api.speed_ranking, tbl_api.score_ranking, tbl_api.rate_ranking, 
            CAST (DENSE_RANK() OVER (
                ORDER BY tbl_fee.price ASC
            ) AS smallint) AS price_ranking
            FROM db_schema.tbl_order_type tbl_ord
            INNER JOIN db_schema.tbl_data_api tbl_api
            ON tbl_ord.carrier_id = tbl_api.carrier_id --6
            AND tbl_ord.receiver_province_code = tbl_api.receiver_province_code
            AND tbl_ord.receiver_district_code = tbl_api.receiver_district_code --713
            AND tbl_ord.new_type = tbl_api.new_type --7
            INNER JOIN db_schema.tbl_service_fee tbl_fee
            ON tbl_ord.carrier_id = tbl_fee.carrier_id --6
            AND tbl_ord.new_type = tbl_fee.new_type  --7
            WHERE tbl_ord.sender_province_code = '{}' 
            AND tbl_ord.sender_district_code = '{}'
            AND tbl_ord.receiver_province_code = '{}' 
            AND tbl_ord.receiver_district_code = '{}' 
            AND tbl_fee.weight = CEIL({}/500.0)*500 
            AND tbl_fee.pickup = '{}'
        )
        select carrier_id, route_type, price, status::varchar(1) AS status, description, time_data, time_display,
        rate, score, star, for_shop, 
        CAST (DENSE_RANK() OVER (
            ORDER BY
                (1.4 * price_ranking + 1.2 * rate_ranking + score_ranking)
            ASC
        ) AS smallint) AS for_partner,
        price_ranking, speed_ranking, score_ranking
        FROM carrier_information
        ORDER BY carrier_id;
    """.format(
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
