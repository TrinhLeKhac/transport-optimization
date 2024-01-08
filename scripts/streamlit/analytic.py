import datetime

from scripts.streamlit.streamlit_helper import *
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go


def draw_zns(total_zns_df, province, district, n_stars, r_date):
    filter_zns_df = total_zns_df.loc[
        total_zns_df['receiver_province'].isin(province)
        & total_zns_df['receiver_district'].isin(district)
        & total_zns_df['n_stars'].isin(n_stars)
        & (total_zns_df['reviewed_at'].dt.date >= r_date[0])
        & (total_zns_df['reviewed_at'].dt.date <= r_date[1])
    ]
    viz_df = filter_zns_df['carrier'].value_counts().reset_index()

    fig = px.pie(viz_df, values='count', names='carrier')
    fig.update_traces(textposition='inside', textinfo='value+value')
    return fig, len(filter_zns_df)


def draw_order(total_order_df, sender_province, sender_district, receiver_province, receiver_district, carrier_status, w_range):
    filter_order_df = total_order_df.loc[
        total_order_df['sender_province'].isin(sender_province)
        & total_order_df['sender_district'].isin(sender_district)
        & total_order_df['receiver_province'].isin(receiver_province)
        & total_order_df['receiver_district'].isin(receiver_district)
        & total_order_df['carrier_status'].isin(carrier_status)
        & (total_order_df['weight'] >= w_range[0])
        & (total_order_df['weight'] <= w_range[1])
    ]
    viz_df = filter_order_df['carrier'].value_counts().reset_index()

    fig = px.pie(viz_df, values='count', names='carrier')
    fig.update_traces(textposition='inside', textinfo='value+value')
    return fig, len(filter_order_df)


def create_analytic_tab():
    interactive = st.container()
    with interactive:
        # 1. Info
        st.info(
            """
            **Modules này hỗ trợ :red[thống kê dữ liệu đầu vào]**
            * Thông tin:  
            👉 Chart thống kê đánh giá ZNS   
            👉 Chart thống kê thông tin đơn hàng   
        """
        )
        st.divider()
        # ----------------------------------------------------------------------------------------------

        total_zns_df = st_get_data_zns()
        total_order_df = st_get_data_order()

        # 2. Thống kê ZNS
        opt_zns_province, opt_zns_district = st.columns(2)

        opt_zns_province.multiselect(
            ":blue[**Chọn Tỉnh/Thành Phố**]",
            options=total_zns_df['receiver_province'].unique().tolist(),
            default=['Thành phố Hà Nội'],
            key='zns_province',
        )
        opt_zns_district.multiselect(
            ":blue[**Chọn Quận/Huyệni**]",
            options=total_zns_df.loc[
                total_zns_df['receiver_province'].isin(st.session_state['zns_province'])
            ]['receiver_district'].unique().tolist(),
            key='zns_district',
            default=['Quận Đống Đa'],
        )
        # ----------------------------------------------------------------------------------------------
        opt_zns_star, opt_range_date = st.columns(2)
        opt_zns_star.multiselect(
            ":blue[**Chọn số sao đánh giá**]",
            options=total_zns_df.loc[
                (total_zns_df['receiver_province'].isin(st.session_state['zns_province']))
                & (total_zns_df['receiver_district'].isin(st.session_state['zns_district']))
            ]['n_stars'].unique().tolist(),
            key='zns_star',
            default=[1, 5],
        )
        filter_zns_df = total_zns_df.loc[
            (total_zns_df['receiver_province'].isin(st.session_state['zns_province']))
            & (total_zns_df['receiver_district'].isin(st.session_state['zns_district']))
            & (total_zns_df['n_stars'].isin(st.session_state['zns_star']))
        ]
        opt_range_date.slider(
            label=":blue[**Chọn khoảng thời gian**]",
            min_value=filter_zns_df['reviewed_at'].min().date(),
            max_value=filter_zns_df['reviewed_at'].max().date(),
            step=timedelta(days=1),
            key='zns_range_date',
            value=(filter_zns_df['reviewed_at'].min().date(), filter_zns_df['reviewed_at'].max().date())
        )
        # ----------------------------------------------------------------------------------------------
        fig_zns_by_carrier, _len = draw_zns(
            total_zns_df,
            province=st.session_state['zns_province'],
            district=st.session_state['zns_district'],
            n_stars=st.session_state['zns_star'],
            r_date=st.session_state['zns_range_date']
        )

        st.plotly_chart(fig_zns_by_carrier)
        # st.info(f"Tổng số đánh giá: :red[**{_len}**]")
        st.divider()
        # ----------------------------------------------------------------------------------------------

        # 3. Thống kê đơn hàng
        opt_order_sender_province, opt_order_sender_district = st.columns(2)

        opt_order_sender_province.multiselect(
            ":blue[**Chọn Tỉnh/Thành Phố Giao**]",
            options=total_order_df['sender_province'].unique().tolist(),
            default=['Thành phố Hà Nội'],
            key='order_sender_province',
        )
        opt_order_sender_district.multiselect(
            ":blue[**Chọn Quận/Huyện Giao**]",
            options=total_order_df.loc[
                total_order_df['sender_province'].isin(st.session_state['order_sender_province'])
            ]['sender_district'].unique().tolist(),
            key='order_sender_district',
            default=['Quận Đống Đa'],
        )

        opt_order_receiver_province, opt_order_receiver_district = st.columns(2)

        opt_order_receiver_province.multiselect(
            ":blue[**Chọn Tỉnh/Thành Phố Nhận**]",
            options=total_order_df.loc[
                total_order_df['sender_province'].isin(st.session_state['order_sender_province'])
                & total_order_df['sender_district'].isin(st.session_state['order_sender_district'])
            ]['receiver_province'].unique().tolist(),
            default=['Thành phố Hồ Chí Minh'],
            key='order_receiver_province',
        )
        opt_order_receiver_district.multiselect(
            ":blue[**Chọn Quận/Huyện Nhận**]",
            options=total_order_df.loc[
                total_order_df['sender_province'].isin(st.session_state['order_sender_province'])
                & total_order_df['sender_district'].isin(st.session_state['order_sender_district'])
                & total_order_df['receiver_province'].isin(st.session_state['order_receiver_province'])
            ]['receiver_district'].unique().tolist(),
            key='order_receiver_district',
            default=['Quận 1'],
        )
        # ----------------------------------------------------------------------------------------------
        opt_carrier_status, opt_weight_range = st.columns(2)
        opt_carrier_status.multiselect(
            ":blue[**Chọn trạng thái đơn hàng**]",
            options=('Chưa giao hàng', 'Đang giao', 'Hoàn hàng', 'Thành công', 'Thất lạc', 'Không xét'),
            key='order_carrier_status',
            default=['Thành công'],
        )
        total_status = []
        for stt in st.session_state['order_carrier_status']:
            total_status.extend(STATUS_MAPPING[stt])

        # filter_order_df = total_order_df.loc[
        #     total_order_df['sender_province'].isin(st.session_state['order_sender_province'])
        #     & total_order_df['sender_district'].isin(st.session_state['order_sender_district'])
        #     & total_order_df['receiver_province'].isin(st.session_state['order_receiver_province'])
        #     & (total_order_df['receiver_district'].isin(st.session_state['order_receiver_district']))
        #     & (total_order_df['carrier_status'].isin(total_status))
        #     ]
        opt_weight_range.slider(
            label=":blue[**Chọn khoảng khối lượng đơn**]",
            min_value=50,
            max_value=50000,
            step=50,
            key='order_weight_range',
            value=(500, 2000)
        )
        # ----------------------------------------------------------------------------------------------
        fig_order_by_carrier, _len_order = draw_order(
            total_order_df,
            sender_province=st.session_state['order_sender_province'],
            sender_district=st.session_state['order_sender_district'],
            receiver_province=st.session_state['order_receiver_province'],
            receiver_district=st.session_state['order_receiver_district'],
            carrier_status=st.session_state['order_carrier_status'],
            w_range=st.session_state['order_weight_range']
        )

        st.plotly_chart(fig_order_by_carrier)
        st.info(f"Tổng số đơn: :red[**{_len_order}**]")
        st.divider()
        # ----------------------------------------------------------------------------------------------
