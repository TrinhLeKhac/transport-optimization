from scripts.streamlit.streamlit_helper import *


def get_order_type_str(target_df, order_type_col='new_type'):
    final_str = 'Phân loại tuyến  '

    if target_df[order_type_col].nunique() == 1:
        new_type = MAPPING_ID_ORDER_TYPE[int(target_df[order_type_col].values[0])]
        final_str = final_str + f"""\n✅:red[**{new_type}**]"""
    else:
        for odt_id in target_df[order_type_col].unique():
            tmp_new_type = MAPPING_ID_ORDER_TYPE[int(odt_id)]
            tmp_carrier = ', '.join(target_df.loc[target_df[order_type_col] == odt_id]['carrier'].tolist())
            final_str = final_str + f"""\n✅:red[**{tmp_new_type}:**] :blue[**{tmp_carrier}**]  """
    return final_str


def handle_submit_form():
    print('Weight inside callback function:', st.session_state['weight'])
    sender_province_code = (
        PROVINCE_MAPPING_DISTRICT_DF.loc[
            PROVINCE_MAPPING_DISTRICT_DF['province'] == st.session_state['sender_province']
            ]['province_code'].values[0]
    )
    sender_district_code = (
        PROVINCE_MAPPING_DISTRICT_DF.loc[
            (PROVINCE_MAPPING_DISTRICT_DF['province'] == st.session_state['sender_province'])
            & (PROVINCE_MAPPING_DISTRICT_DF['district'] == st.session_state['sender_district'])
            ]['district_code'].values[0]
    )
    receiver_province_code = (
        PROVINCE_MAPPING_DISTRICT_DF.loc[
            PROVINCE_MAPPING_DISTRICT_DF['province'] == st.session_state['receiver_province']
            ]['province_code'].values[0]
    )
    receiver_district_code = (
        PROVINCE_MAPPING_DISTRICT_DF.loc[
            (PROVINCE_MAPPING_DISTRICT_DF['province'] == st.session_state['receiver_province'])
            & (PROVINCE_MAPPING_DISTRICT_DF['district'] == st.session_state['receiver_district'])
            ]['district_code'].values[0]
    )
    if st.session_state['pickup'] == 'Lấy Tận Nơi':
        pickup = '0'
    elif st.session_state['pickup'] == 'Gửi Bưu Cục':
        pickup = '1'
    weight = st.session_state['weight']

    # print(sender_province_code, sender_district_code, receiver_province_code, receiver_district_code)

    result_df = get_st_dataframe_from_db(
        sender_province_code, sender_district_code,
        receiver_province_code, receiver_district_code,
        weight, pickup
    )
    # print(result_df.columns)
    st.session_state['submit_result'] = result_df
    st.session_state['is_submitted_at_least_one_time'] = True


def create_customer_tab():
    st.info(
        """
        Page show :red[**kết quả trả về từ API**]  
        :red[**Input**]  
        ✅ Tỉnh/Thành Phố của Người Gửi    
        ✅ Quận/Huyện của Người Gửi    
        ✅ Tỉnh/Thành Phố của Người Nhận    
        ✅ Quận/Huyện của Người Nhận    
        ✅ Hình Thức Gửi Hàng (:red[**Gửi Bưu Cục**] hoặc :red[**Lấy Tận Nơi**])     
        ✅ Khối Lượng tính cước (đơn vị: :red[**gram**])  
            
        :red[**Output**]  
        👉 Mã phân loại tuyến  
        👉 Giá cước giao hàng (đơn vị: :red[**đồng**])  
        👉 Trạng thái tuyến giao của nhà vận chuyển  
        👉 Thời gian giao dự kiến  
        👉 Tỉ lệ giao thành công  
        👉 Số sao trung bình tuyến theo đánh giá người nhận  
        👉 Điểm chất lượng giao hàng của nhà vận chuyển  
        👉 Ranking nhà vận chuyển theo các tiêu chí (tốt nhất cho khách hàng, đối tác, cước phí rẻ nhất, tốc độ nhanh nhất, chất lượng tốt nhất)
    """
    )
    # ----------------------------------------------------------------------------------------------

    # Form
    with st.container():
        # ----------------------------------------------------------------------------------------------
        sender_province_field, sender_district_field = st.columns(2)
        sender_province_field.selectbox(
            ":blue[**Tỉnh/Thành Phố của Người Gửi**]",
            options=(PROVINCE_MAPPING_DISTRICT_DF['province'].unique()),
            key='sender_province',
        )
        sender_district_field.selectbox(
            ":blue[**Quận/Huyện của Người Gửi**]",
            options=(
                PROVINCE_MAPPING_DISTRICT_DF.loc[
                    PROVINCE_MAPPING_DISTRICT_DF['province'] == st.session_state['sender_province']]
                ['district'].unique()),
            key='sender_district',
        )
        # ----------------------------------------------------------------------------------------------
        receiver_province_field, receiver_district_field = st.columns(2)
        receiver_province_field.selectbox(
            ":blue[**Tỉnh/Thành Phố của Người Nhận**]",
            options=(PROVINCE_MAPPING_DISTRICT_DF['province'].unique()),
            key='receiver_province',
        )
        receiver_district_field.selectbox(
            ":blue[**Quận/Huyện của Người Nhận**]",
            options=(
                PROVINCE_MAPPING_DISTRICT_DF.loc[
                    PROVINCE_MAPPING_DISTRICT_DF['province'] == st.session_state['receiver_province']]
                ['district'].unique()),
            key='receiver_district',
        )
        # ----------------------------------------------------------------------------------------------
        pickup_field, weight_field = st.columns(2)
        pickup_field.selectbox(
            ":blue[**Hình Thức Gửi Hàng**]",
            options=('Lấy Tận Nơi', 'Gửi Bưu Cục'),
            key='pickup'
        )
        weight_field.number_input(
            ':blue[**Khối lượng đơn (gram)**: ]',
            key='weight',
            placeholder='Vui lòng nhập khối lượng đơn <= 50,000g và lớn hơn 0g',
            format='%d',
            step=50
        )
        print("Weight after re-run scripts", st.session_state['weight'])

        # --------------------------------------------------------------------------------------------
        st.button(
            "Xem kết quả",
            type='primary',
            on_click=handle_submit_form,
        )
    # ------------------------------------------------------------------------------------------------

    # Logic
    if 'is_submitted_at_least_one_time' not in st.session_state:
        st.session_state['is_submitted_at_least_one_time'] = False
    if 'submit_result' not in st.session_state:
        st.session_state['submit_result'] = pd.DataFrame()

    if st.session_state['is_submitted_at_least_one_time']:
        result_df = st.session_state['submit_result']
        result_df['carrier'] = result_df['carrier_id'].map(MAPPING_ID_CARRIER)
        # print(result_df)
        # new_type = MAPPING_ID_ORDER_TYPE[int(result_df['new_type'].values[0])]

        # Table 1
        result_df1 = result_df[[
            'carrier',
            'description',
            'price',
            'time_data',
            'rate',
            'star',
            'score',
            # 'for_shop',
            # 'for_partner',
        ]]

        # Show dataframe of information
        if len(result_df) > 0:
            st.info(f"""{get_order_type_str(result_df)}""")
            st.dataframe(
                result_df1,
                column_config={
                    "carrier": "Nhà vận chuyển",
                    'description': "Trạng thái tuyến giao",
                    'price': "Tiền cước",
                    'time_data': "Thời gian giao dự kiến",
                    'rate': 'Tỉ lệ giao thành công',
                    "star": st.column_config.NumberColumn(
                        "Số sao đánh giá trung bình",
                        format="%.1f ⭐",
                    ),
                    "score": "Score chất lượng giao hàng",
                },
                hide_index=True,
            )

            # ranking_by_customer = ' > '.join(result_df.sort_values('for_shop', ascending=True)['carrier'].tolist())
            # ranking_by_partner = ' > '.join(result_df.sort_values('for_partner', ascending=True)['carrier'].tolist())

            st.info(
                f"""
                NVC tốt cho :red[**Khách hàng**]    
                :one: :blue[**{', '.join(result_df[result_df['for_shop'] == 1]['carrier'].tolist())}**]  
                :two: :blue[**{', '.join(result_df[result_df['for_shop'] == 2]['carrier'].tolist())}**]  
                :three: :blue[**{', '.join(result_df[result_df['for_shop'] == 3]['carrier'].tolist())}**]  
                :four: :blue[**{', '.join(result_df[result_df['for_shop'] == 4]['carrier'].tolist())}**]  
                :five: :blue[**{', '.join(result_df[result_df['for_shop'] == 5]['carrier'].tolist())}**]  
                :six: :blue[**{', '.join(result_df[result_df['for_shop'] == 6]['carrier'].tolist())}**]  
                """
            )

            st.info(
                f"""
                NVC tốt cho :red[**Đối tác**]    
                :one: :blue[**{', '.join(result_df[result_df['for_partner'] == 1]['carrier'].tolist())}**]  
                :two: :blue[**{', '.join(result_df[result_df['for_partner'] == 2]['carrier'].tolist())}**]  
                :three: :blue[**{', '.join(result_df[result_df['for_partner'] == 3]['carrier'].tolist())}**]  
                :four: :blue[**{', '.join(result_df[result_df['for_partner'] == 4]['carrier'].tolist())}**]  
                :five: :blue[**{', '.join(result_df[result_df['for_partner'] == 5]['carrier'].tolist())}**]  
                :six: :blue[**{', '.join(result_df[result_df['for_shop'] == 6]['carrier'].tolist())}**]  
                """
            )

        elif st.session_state['weight'] == 0:
            st.warning('Vui lòng nhập khối lượng đơn hàng > 0g')
        elif st.session_state['weight'] > 50000:
            st.warning('Vui lòng nhập khối lượng đơn hàng <= 50000g')
        else:
            st.error('Có lỗi xảy ra')
