import datetime
from scripts.streamlit.streamlit_helper import *
import streamlit as st
import plotly.express as px


def draw_n_zns_message(filter_zns_df):

    viz_df = filter_zns_df['carrier'].value_counts().reset_index()

    fig = px.pie(viz_df, values='count', names='carrier', height=300)
    fig.update_traces(textposition='inside', textinfo='label+value')
    fig.update_layout(showlegend=False)
    fig.update_layout(
        {
            "plot_bgcolor": "rgba(0, 0, 0, 0)",  # make the background transparent
            "margin": {"l": 0, "r": 0, "t": 0, "b": 0}
        }
    )
    return fig


def draw_n_zns_comment(filter_zns_df):

    viz_df = filter_zns_df['comment'].value_counts().reset_index()
    fig = px.pie(viz_df, values='count', names='comment', height=300)
    fig.update_traces(textposition='inside', textinfo='value')
    fig.update_layout(
        {
            "plot_bgcolor": "rgba(0, 0, 0, 0)",  # make the background transparent
            "margin": {"l": 0, "r": 0, "t": 15, "b": 0}
        }
    )
    return fig


def draw_order(filter_order_df):
    viz_df = filter_order_df['carrier'].value_counts().reset_index()

    fig = px.pie(viz_df, values='count', names='carrier')
    fig.update_traces(textposition='inside', textinfo='label+value')
    fig.update_layout(showlegend=False)
    return fig


def create_analytic_tab(run_date_str):
    interactive = st.container()
    with interactive:

        # 1. Thống kê tuyến ưu tiên

        # 1.1. Load data
        meta_priority_df = st_get_data_meta_priority_route()
        raw_priority_df, dup_priority_df = st_get_data_priority_route()
        raw_priority_details_df, dup_priority_details_df = st_get_data_priority_route_details()

        # 1.2. Thông tin tuyến ưu tiên
        st.info(
            f"""
                    **Thống kê dữ liệu :red[Tuyến ưu tiên]**   
                    * Thông tin:  
                    👉 Khoảng thời gian đánh giá: :red[**1 tháng**], :red[**2 tháng**], :red[**3 tháng**], :red[**6 tháng**], :red[**12 tháng**]  
                    👉 Chỉ xét đơn NVC lấy thành công :red[**trước 18:00**] ngày hôm trước (:red[**picked_at**])  
                    👉 Thời gian shipper lấy từ kho ở tỉnh đi giao :red[**trước 09:00**] ngày hôm sau (:red[**last_delivering_at**])  
                    👉 Tỉ lệ tính đang lấy ở mức top :red[**20%**]    
                """
        )

        # 1.3 Tỉ lệ tính
        meta_div, _, _ = st.columns(3)
        meta_div.selectbox(
            ":blue[**Chọn tỉ lệ tính**]",
            options=sorted(meta_priority_df['type'].unique().tolist(), key=vietnamese_sort_key),
            key='meta_priority_type',
        )

        filter_priority_meta_df = meta_priority_df.loc[
            (meta_priority_df['type'] == st.session_state['meta_priority_type'])
            ][[ 'order_type', 'rounded_delta_hour', 'idea_delta_hour']]

        st.dataframe(
            filter_priority_meta_df,
            column_config={
                'order_type': "Hình thức vận chuyển",
                'rounded_delta_hour': "Thời gian vận chuyển (last_delivering_at - picked_at)(h)",
                'idea_delta_hour': "Thòi gian vận chuyển (tính xét tuyến ưu tiên)",
            },
            hide_index=True,
        )
        st.divider()

        # 1.4 Thông tin thống kê
        # Checkbox filter tuyến ưu tiên có nhiều hơn 1 NVC
        find_duplicates = st.checkbox("Check tuyến ưu tiên có nhiều hơn 1 NVC")
        if find_duplicates:
            priority_df = dup_priority_df
            priority_details_df = dup_priority_details_df
        else:
            priority_df = raw_priority_df
            priority_details_df = raw_priority_details_df

        # 1.4.1 Select box chọn thông tin thống kê
        priority_div1, priority_div2, priority_div3 = st.columns(3)

        priority_div1.selectbox(
            ":blue[**Chọn Tỉnh/Thành Phố Gửi**]",
            options=sorted(priority_df['sender_province'].unique().tolist(), key=vietnamese_sort_key),
            key='priority_sender_province',
        )
        priority_div2.selectbox(
            ":blue[**Chọn Quận/Huyện Gửi**]",
            options=sorted(priority_df.loc[
                               (priority_df['sender_province'] == st.session_state[
                                   'priority_sender_province'])
                           ]['sender_district'].unique().tolist(), key=vietnamese_sort_key),
            key='priority_sender_district',
        )
        priority_div3.selectbox(
            ":blue[**Chọn Loại Vận Chuyển**]",
            options=sorted(priority_df.loc[
                               (priority_df['sender_province'] == st.session_state[
                                   'priority_sender_province'])
                               & (priority_df['sender_district'] == st.session_state[
                                   'priority_sender_district'])
                               ]['order_type'].unique().tolist(), key=vietnamese_sort_key),
            key='priority_order_type',
        )

        priority_div4, priority_div5, _ = st.columns(3)

        priority_div4.selectbox(
            ":blue[**Chọn Tỉnh/Thành Phố Nhận**]",
            options=sorted(priority_df.loc[
                               (priority_df['sender_province'] == st.session_state[
                                   'priority_sender_province'])
                               & (priority_df['sender_district'] == st.session_state[
                                   'priority_sender_district'])
                               & (priority_df['order_type'] == st.session_state[
                                   'priority_order_type'])
                               ]['receiver_province'].unique().tolist(), key=vietnamese_sort_key),
            key='priority_receiver_province',
        )
        priority_div5.selectbox(
            ":blue[**Chọn Quận/Huyện Nhận**]",
            options=sorted(priority_df.loc[
                               (priority_df['sender_province'] == st.session_state[
                                   'priority_sender_province'])
                               & (priority_df['sender_district'] == st.session_state[
                                   'priority_sender_district'])
                               & (priority_df['order_type'] == st.session_state[
                                   'priority_order_type'])
                               & (priority_df['receiver_province'] == st.session_state[
                                   'priority_receiver_province'])
                               ]['receiver_district'].unique().tolist(), key=vietnamese_sort_key),
            key='priority_receiver_district',
        )

        # 1.4.2 Thông tin thống kê
        filter_priority_df = priority_df.loc[
             (priority_df['sender_province'] == st.session_state['priority_sender_province'])
             & (priority_df['sender_district'] == st.session_state['priority_sender_district'])
             & (priority_df['order_type'] == st.session_state['priority_order_type'])
             & (priority_df['receiver_province'] == st.session_state['priority_receiver_province'])
             & (priority_df['receiver_district'] == st.session_state['priority_receiver_district'])
            ]

        filter_priority_df = filter_priority_df[[
            'carrier', 'preferred_carrier',
            'sender_province', 'sender_district', 'receiver_province', 'receiver_district',
            'order_type',
            'orders_in_1_month', 'ndays_in_1_month',
            'orders_in_2_month', 'ndays_in_2_month',
        ]]
        st_p1, _, _, _, _ = st.columns(5)

        # 1.4.3 Hiển thị thống kê
        st_p1.info(":red[**Thống kê**]")
        st.dataframe(
            filter_priority_df,
            column_config={
                "carrier": "Nhà vận chuyển",
                "preferred_carrier": "Ưu tiên",
                'sender_province': "Tỉnh thành gửi",
                'sender_district': "Quận huyện gửi",
                'receiver_province': "Tỉnh thành nhận",
                'receiver_district': "Quận huyện nhận",
                'order_type': "Hình thức vận chuyển",
                'orders_in_1_month': "Đơn (1 tháng)",
                'ndays_in_1_month': 'Ngày (1 tháng)',
                'orders_in_2_month': "Đơn (2 tháng)",
                'ndays_in_2_month': 'Ngày (2 tháng)',
            },
            hide_index=True,
        )

        filter_priority_details_df = priority_details_df.loc[
            (priority_details_df['sender_province'] == st.session_state['priority_sender_province'])
            & (priority_details_df['sender_district'] == st.session_state['priority_sender_district'])
            & (priority_details_df['order_type'] == st.session_state['priority_order_type'])
            & (priority_details_df['receiver_province'] == st.session_state['priority_receiver_province'])
            & (priority_details_df['receiver_district'] == st.session_state['priority_receiver_district'])
            ]

        filter_priority_details_df = filter_priority_details_df[[
            'order_code', 'carrier',
            'sender_province', 'sender_district',
            'receiver_province', 'receiver_district',
            'order_status',
            'picked_at', 'last_delivering_at',
        ]]

        # 1.5.3 Thông tin chi tiết để hiển thị
        st.dataframe(
            filter_priority_details_df,
            column_config={
                "order_code": "Mã đơn hàng",
                "carrier": "Nhà vận chuyển",
                'sender_province': "Tỉnh thành gửi",
                'sender_district': "Quận huyện gửi",
                'receiver_province': "Tỉnh thành nhận",
                'receiver_district': "Quận huyện nhận",
                'order_status': "Trạng thái đơn hàng",
                'picked_at': "Thời gian shipper NVC lấy hàng",
                'last_delivering_at': "Thời gian shipper giao lấy từ kho ở tỉnh đi giao"
            },
            hide_index=True,
        )
        st.divider()

        # 2. Thống kê ZNS
        # 2.1. Load data
        total_zns_df = st_get_data_zns()
        comment_zns_df = total_zns_df[['receiver_province', 'receiver_district', 'carrier', 'comment']].explode(
            column='comment')
        comment_zns_df = comment_zns_df.loc[comment_zns_df['comment'].notna()]

        # 2.2. Thống kê data ZNS
        st.info(
            f"""
            **Thống kê dữ liệu :red[đánh giá ZNS]**   
            * Thông tin:  
            👉 Khoảng thời gian đánh giá: Từ :red[**{total_zns_df['reviewed_at'].min().date()}**] đến :red[**{total_zns_df['reviewed_at'].max().date()}**]   
            👉 Số tin nhắn ZNS theo :red[**Khu vực**], :red[**Số sao đánh giá**] và :red[**Khoảng thời gian**] tùy chọn  
            👉 Comment của người nhận theo :red[**Khu vực**], :red[**Nhà vận chuyển**]  
        """
        )

        chart_zns_message, _, chart_zns_comment = st.columns([4, 1, 3])

        # 2.3 ZNS message div
        opt_zns_mess_province, opt_zns_mess_district = chart_zns_message.columns(2)
        opt_zns_mess_province.selectbox(  # multiselect
            ":blue[**Chọn Tỉnh/Thành Phố**]",
            options=sorted(total_zns_df['receiver_province'].unique().tolist(), key=vietnamese_sort_key),
            key='zns_province',
        )
        filter_zns_df1 = total_zns_df.loc[
            (total_zns_df['receiver_province'] == st.session_state['zns_province'])
        ]
        opt_zns_mess_district.selectbox(
            ":blue[**Chọn Quận/Huyện**]",
            options=sorted(filter_zns_df1['receiver_district'].unique().tolist(), key=vietnamese_sort_key),
            key='zns_district',
        )
        opt_zns_mess_star, opt_zns_mess_range_date = chart_zns_message.columns([2, 3])
        filter_zns_df2 = filter_zns_df1.loc[
            (filter_zns_df1['receiver_district'] == st.session_state['zns_district'])
        ]
        opt_zns_mess_star.selectbox(
            ":blue[**Chọn Số Sao Đánh Giá**]",
            options=sorted(filter_zns_df2['n_stars'].unique().tolist()),
            key='zns_star',
        )
        filter_zns_df3 = filter_zns_df2.loc[
            (filter_zns_df2['n_stars'] == st.session_state['zns_star'])
        ]
        opt_zns_mess_range_date.slider(
            label=":blue[**Chọn Khoảng Thời Gian**]",
            min_value=filter_zns_df3['reviewed_at'].min().date(),
            max_value=filter_zns_df3['reviewed_at'].max().date()+timedelta(days=1),
            step=timedelta(days=1),
            key='zns_range_date',
            value=(filter_zns_df3['reviewed_at'].min().date(), filter_zns_df3['reviewed_at'].max().date())
        )
        filter_zns_df4 = filter_zns_df3.loc[
            (filter_zns_df3['reviewed_at'].dt.date >= st.session_state['zns_range_date'][0])
            & (filter_zns_df3['reviewed_at'].dt.date <= st.session_state['zns_range_date'][1])
        ]
        fig_zns_mess_by_carrier = draw_n_zns_message(filter_zns_df4)

        chart_zns_message.plotly_chart(fig_zns_mess_by_carrier)
        chart_zns_message.info(f'Tổng số đánh giá: :red[**{len(filter_zns_df4)}**]')

        # ----------------------------------------------------------------------------------------------

        # 2.4 ZNS comment div
        opt_zns_com_province, opt_zns_com_district = chart_zns_comment.columns(2)

        opt_zns_com_province.selectbox(
            ":blue[**Chọn Tỉnh/Thành Phố**]",
            options=sorted(comment_zns_df['receiver_province'].unique().tolist(), key=vietnamese_sort_key),
            key='zns_province2',
        )
        filter_comment_zns_df1 = comment_zns_df.loc[
            (comment_zns_df['receiver_province'] == st.session_state['zns_province2'])
        ]
        opt_zns_com_district.selectbox(
            ":blue[**Chọn Quận/Huyện**]",
            options=sorted(filter_comment_zns_df1['receiver_district'].unique().tolist(), key=vietnamese_sort_key),
            key='zns_district2',
        )
        filter_comment_zns_df2 = filter_comment_zns_df1.loc[
            (filter_comment_zns_df1['receiver_district'] == st.session_state['zns_district2'])
        ]
        chart_zns_comment.selectbox(
            ":blue[**Chọn Nhà Vận Chuyển**]",
            options=sorted(filter_comment_zns_df2['carrier'].unique().tolist(), key=vietnamese_sort_key),
            key='zns_carrier',
        )
        filter_comment_zns_df3 = filter_comment_zns_df2.loc[
            (filter_comment_zns_df2['carrier'] == st.session_state['zns_carrier'])
        ]
        fig_zns_com_by_carrier = draw_n_zns_comment(filter_comment_zns_df3)

        chart_zns_comment.plotly_chart(fig_zns_com_by_carrier)
        chart_zns_comment.info(f'Tổng số comment: :red[**{len(filter_comment_zns_df3)}**]')

        st.divider()
        # ----------------------------------------------------------------------------------------------

        # 3. Thống kê đơn hàng
        # 3.1 Load data
        total_order_df = st_get_data_order()
        ti_le_giao_hang = st_get_ti_le_giao_hang()

        # 3.2 Thống kê data
        st.info(
            f"""
                **Thống kê dữ liệu :red[đơn hàng]**   
                * Thông tin:  
                👉 Khoảng thời gian đánh giá: Từ :red[**{total_order_df['created_at'].min().date()}**] đến :red[**{total_order_df['created_at'].max().date()}**]   
                👉 Số đơn hàng tính theo :red[**Khu vực**], :red[**Trạng thái giao hàng**], :red[**Khối lượng**] và :red[**Khoảng thời gian**] tùy chọn  
                👉 Thống kê khu vực :red[**đơn tồn đọng**] 
            """
        )

        chart_order, _, chart_stuck = st.columns([8, 1, 7])
        opt_order_sender_province, opt_order_sender_district = chart_order.columns(2)

        opt_order_sender_province.selectbox(
            ":blue[**Chọn Tỉnh/Thành Phố Giao**]",
            options=sorted(total_order_df['sender_province'].unique().tolist(), key=vietnamese_sort_key),
            key='order_sender_province',
        )
        filter_order_df1 = total_order_df.loc[
            total_order_df['sender_province'] == st.session_state['order_sender_province']
            ]
        opt_order_sender_district.selectbox(
            ":blue[**Chọn Quận/Huyện Giao**]",
            options=sorted(filter_order_df1['sender_district'].unique().tolist(), key=vietnamese_sort_key),
            key='order_sender_district',
        )

        opt_order_receiver_province, opt_order_receiver_district = chart_order.columns(2)
        filter_order_df2 = filter_order_df1.loc[
            filter_order_df1['sender_district'] == st.session_state['order_sender_district']
            ]
        opt_order_receiver_province.selectbox(
            ":blue[**Chọn Tỉnh/Thành Phố Nhận**]",
            options=sorted(filter_order_df2['receiver_province'].unique().tolist(), key=vietnamese_sort_key),
            key='order_receiver_province',
        )
        filter_order_df3 = filter_order_df2.loc[
            filter_order_df2['receiver_province'] == st.session_state['order_receiver_province']
            ]
        opt_order_receiver_district.selectbox(
            ":blue[**Chọn Quận/Huyện Nhận**]",
            options=sorted(filter_order_df3['receiver_district'].unique().tolist(), key=vietnamese_sort_key),
            key='order_receiver_district',
        )
        filter_order_df4 = filter_order_df3.loc[
            filter_order_df3['receiver_district'] == st.session_state['order_receiver_district']
            ]
        options_carrier_status = DF_STATUS_MAPPING.loc[
            DF_STATUS_MAPPING['carrier_status'].isin(filter_order_df4['carrier_status'].unique().tolist())
        ]['status'].unique().tolist()

        opt_carrier_status, opt_weight_range = chart_order.columns(2)
        opt_carrier_status.selectbox(
            ":blue[**Chọn Trạng Thái Đơn Hàng**]",
            options=sorted(options_carrier_status, key=vietnamese_sort_key),
            key='order_carrier_status',
        )
        filter_order_df5 = filter_order_df4.loc[
            filter_order_df4['carrier_status'].isin(
                DF_STATUS_MAPPING.loc[
                    DF_STATUS_MAPPING['status'] == st.session_state['order_carrier_status']
                    ]['carrier_status'])
        ]
        opt_weight_range.slider(
            label=":blue[**Chọn Khoảng Khối Lượng Đơn**]",
            min_value=int(filter_order_df5['weight'].min() // 100) * 100,
            max_value=int(filter_order_df5['weight'].max() // 100) * 100 + 100,
            step=100,
            key='order_weight_range',
            value=(filter_order_df5['weight'].min(), filter_order_df5['weight'].max())
        )
        filter_order_df6 = filter_order_df5.loc[
            (filter_order_df5['weight'] >= st.session_state['order_weight_range'][0])
            & (filter_order_df5['weight'] <= st.session_state['order_weight_range'][1])
            ]
        try:
            opt_created_at_range, opt_delivery_type = chart_order.columns(2)
            opt_created_at_range.slider(
                label=":blue[**Chọn Khoảng Thời Gian Tạo Đơn (created_at)**]",
                min_value=total_order_df['created_at'].min().date(),
                max_value=total_order_df['created_at'].max().date() + timedelta(days=1),
                step=timedelta(days=1),
                key='order_created_at_range',
                value=(filter_order_df6['created_at'].min().date(), filter_order_df6['created_at'].max().date())
            )
            filter_order_df7 = filter_order_df6.loc[
                (filter_order_df6['created_at'].dt.date >= st.session_state['order_created_at_range'][0])
                & (filter_order_df6['created_at'].dt.date <= st.session_state['order_created_at_range'][1])
                ]

            opt_delivery_type.selectbox(
                ":blue[**Chọn Hình Thức Gửi Hàng**]",
                options=sorted(filter_order_df7['delivery_type'].unique().tolist(), key=vietnamese_sort_key),
                key='order_delivery_type',
            )
            filter_order_df8 = filter_order_df7.loc[
                filter_order_df7['delivery_type'] == st.session_state['order_delivery_type']]
            fig_order_by_carrier = draw_order(filter_order_df8)

            chart_order.plotly_chart(fig_order_by_carrier)
            chart_order.info(f"""
                Tổng số đơn: :red[**{len(filter_order_df8)}**]  
                Loại vận chuyển: :red[**{filter_order_df8['order_type'].values[0]}**]  
            """)
        except:
            chart_order.error('Với điều kiện lọc trên, không có dữ liệu nào thỏa mãn')

        # ----------------------------------------------------------------------------------------------
        # 3.2 Thống kê đơn hàng tồn đọng
        chart_stuck.info(
            f"""
                **Nguyên tắc tính :red[đơn tồn đọng]**     
                👉 Nội/Ngoại Thành Tỉnh, Nội/Ngoại Thành Tp.HCM - HN, Nội Miền: :red[**60h**]  
                👉 Nội Miền Tp.HCM - HN: :red[**36h**]  
                👉 Cận Miền, Liên Miền Tp.HCM - HN, Liên Miền Đặc Biệt: :red[**84h**]  
                👉 Cách Miền: :red[**120h**]    
                👉 Fill :red[**last_delivering_at**] bằng giá trị :red[**lớn nhất**] trong tập dữ liệu  
                👉 **:red[Thời gian tồn đọng] = :red[last_delivering_at] - :red[picked_at]**
            """
        )

        ton_dong_df = st_get_don_ton_dong(run_date_str)
        opt_stuck_receiver_province, opt_stuck_receiver_district = chart_stuck.columns(2)

        opt_stuck_receiver_province.selectbox(
            ":blue[**Chọn Tỉnh/Thành Phố Nhận**]",
            options=sorted(ton_dong_df['receiver_province'].unique().tolist(), key=vietnamese_sort_key),
            key='stuck_receiver_province',
        )
        filter_ton_dong_df1 = ton_dong_df.loc[
            ton_dong_df['receiver_province'] == st.session_state['stuck_receiver_province']
            ]
        opt_stuck_receiver_district.selectbox(
            ":blue[**Chọn Quận/Huyện Nhận**]",
            options=sorted(filter_ton_dong_df1['receiver_district'].unique().tolist(), key=vietnamese_sort_key),
            key='stuck_receiver_district',
        )
        filter_ton_dong_df2 = filter_ton_dong_df1.loc[
            filter_ton_dong_df1['receiver_district'] == st.session_state['stuck_receiver_district']
            ]
        chart_stuck.selectbox(
            ":blue[**Chọn Hình Thức Vận Chuyển (order_type)**]",
            options=sorted(filter_ton_dong_df2['order_type'].unique().tolist(), key=vietnamese_sort_key),
            key='stuck_order_type',
        )
        filter_ton_dong_df3 = filter_ton_dong_df2.loc[
            filter_ton_dong_df2['order_type'] == st.session_state['stuck_order_type']
            ]

        fig_stuck_order = px.pie(filter_ton_dong_df3, values='n_order_late', names='carrier')
        fig_stuck_order.update_traces(textposition='inside', textinfo='label+value')
        fig_stuck_order.update_layout(showlegend=False)
        chart_stuck.plotly_chart(fig_stuck_order)
        chart_stuck.info(f"""
            Tổng số đơn tồn đọng: :red[**{filter_ton_dong_df3['n_order_late'].sum()}**]  
        """)

        # ----------------------------------------------------------------------------------------------
        div_5_6, div_1_6 = st.columns([5, 1])
        with div_5_6.expander(":blue[**Show chi tiết data theo điều kiện lọc**]"):
            st.dataframe(
                filter_order_df8[[
                    'created_at', 'order_code', 'carrier', 'weight', 'carrier_status',
                    'picked_at', 'last_delivering_at', 'carrier_delivered_at'
                ]],
                hide_index=True,
                use_container_width=True
            )
        with div_1_6:
            save_excel(filter_order_df8, key='filter_order')

        st.info(
            f"""
            **:red[Thời gian giao hàng estimate] :blue[ở API được tính dựa trên:]**     
            👉 Chỉ lấy :red[*đơn thành công*]  
            👉 Chỉ lấy đơn có :red[*created_at*] và :red[*carrier_delivered_at*] xác định    
            👉 Tính thống kê theo :red[*tỉnh/thành phố nhận, quận/huyện nhận, nhà vận chuyển*] và :red[*loại vận chuyển*]  
            👉 **time(:red[h]) = :red[carrier_delivered_at] - :red[created_at]**   
        """
        )
        st.info(
            f"""
            **:red[Tỉ lệ giao hàng thành công] :blue[ở API được tính dựa trên:]**  
            👉 Tính trên tập :red[*đơn thành công + đơn hoàn hàng*]  
            👉 Tính thống kê theo :red[*tỉnh/thành phố nhận, quận/huyện nhận, nhà vận chuyển*]  
            👉 :red[**success_rate = #đơn thành công/(#đơn thành công + #đơn hoàn hàng)**]   
        """
        )
        success_rate_div1, success_rate_div2, success_rate_div3 = st.columns(3)

        success_rate_div1.selectbox(
            ":blue[**Chọn Tỉnh/Thành Phố Nhận**]",
            options=sorted(total_order_df['receiver_province'].unique().tolist(), key=vietnamese_sort_key),
            key='success_rate_receiver_province',
        )
        success_rate_div2.selectbox(
            ":blue[**Chọn Quận/Huyện Nhận**]",
            options=sorted(total_order_df.loc[
                (total_order_df['receiver_province'] == st.session_state['success_rate_receiver_province'])
            ]['receiver_district'].unique().tolist(), key=vietnamese_sort_key),
            key='success_rate_receiver_district',
        )
        success_rate_div3.selectbox(
            ":blue[**Chọn Nhà Vận Chuyển**]",
            options=sorted(total_order_df.loc[
                (total_order_df['receiver_province'] == st.session_state['success_rate_receiver_province'])
                & (total_order_df['receiver_district'] == st.session_state['success_rate_receiver_district'])
                ]['carrier'].unique().tolist(), key=vietnamese_sort_key),
            key='success_rate_carrier',
        )
        filter_success_rate_total_order_df = total_order_df.loc[
            (total_order_df['receiver_province'] == st.session_state['success_rate_receiver_province'])
            & (total_order_df['receiver_district'] == st.session_state['success_rate_receiver_district'])
            & (total_order_df['carrier'] == st.session_state['success_rate_carrier'])
        ]

        success_df = filter_success_rate_total_order_df.loc[
            filter_success_rate_total_order_df['carrier_status'].isin(THANH_CONG_STATUS)
        ]

        failed_df = filter_success_rate_total_order_df.loc[
            filter_success_rate_total_order_df['carrier_status'].isin(HOAN_HANG_STATUS)
        ]

        delivery_success_rate = ti_le_giao_hang.loc[
            (ti_le_giao_hang['receiver_province'] == st.session_state['success_rate_receiver_province'])
            & (ti_le_giao_hang['receiver_district'] == st.session_state['success_rate_receiver_district'])
            & (ti_le_giao_hang['carrier'] == st.session_state['success_rate_carrier'])
        ]['delivery_success_rate'].tolist()[0]

        # ----------------------------------------------------------------------------------------------
        div_3, _, _ = st.columns(3)
        div_3.info(f"👉 Số đơn :red[**thành công**]: :red[**{len(success_df)}**]")
        div_5_6, div_1_6 = st.columns([5, 1])
        with div_5_6.expander(":blue[**Show chi tiết đơn hàng**] :red[**giao thành công**] :blue[**theo điều kiện lọc**]"):
            st.dataframe(
                success_df[[
                    'created_at', 'order_code', 'carrier', 'weight', 'carrier_status',
                    'picked_at', 'last_delivering_at', 'carrier_delivered_at'
                ]],
                hide_index=True,
                use_container_width=True
            )
        with div_1_6:
            save_excel(success_df, key='success')

        # ----------------------------------------------------------------------------------------------
        div_3, _, _ = st.columns(3)
        div_3.info(f"👉 Số đơn :red[**hoàn hàng**]: :red[**{len(failed_df)}**]")
        div_5_6, div_1_6 = st.columns([5, 1])
        with div_5_6.expander(":blue[**Show chi tiết đơn hàng**] :red[**hoàn hàng**] :blue[**theo điều kiện lọc**]"):
            st.dataframe(
                failed_df[[
                    'created_at', 'order_code', 'carrier', 'weight', 'carrier_status',
                    'picked_at', 'last_delivering_at', 'carrier_delivered_at'
                ]],
                hide_index=True,
                use_container_width=True
            )
        with div_1_6:
            save_excel(failed_df, key='failed')
        # ----------------------------------------------------------------------------------------------
        div_3, _, _ = st.columns(3)
        # try:
        #     div_3.info(f"👉 :red[**Tỉ lệ giao thành công**]: :red[**{round(len(success_df)/(len(success_df) + len(failed_df))*100, 2)}%**]")
        # except:
        #     div_3.warning(f"👉 :red[**Tổng số đơn giao**]: :red[**{len(success_df) + len(failed_df)}%**]")

        if (len(success_df) + len(failed_df)) == 0:
            div_3.warning(f"👉 :red[**Tổng số đơn giao**]: :red[**{len(success_df) + len(failed_df)}%**]")
        else:
            div_3.info(f"👉 :red[**Tỉ lệ giao thành công**]: :red[**{round(delivery_success_rate * 100, 2)}%**]")
