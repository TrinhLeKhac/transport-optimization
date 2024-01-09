import datetime

from plotly.subplots import make_subplots

from scripts.streamlit.streamlit_helper import *
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go


def draw_n_zns_message(zns_df, province, district, n_stars, r_date):
    filter_zns_df = zns_df.loc[
        (zns_df['receiver_province'] == province)
        & (zns_df['receiver_district'] == district)
        & (zns_df['n_stars'] == n_stars)
        & (zns_df['reviewed_at'].dt.date >= r_date[0])
        & (zns_df['reviewed_at'].dt.date <= r_date[1])
        ]
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
    return fig, len(filter_zns_df)


def draw_n_zns_comment(zns_df, province, district, carrier):
    filter_zns_df = zns_df.loc[
        (zns_df['receiver_province'] == province)
        & (zns_df['receiver_district'] == district)
        & (zns_df['carrier'] == carrier)
        ]
    viz_df = filter_zns_df['comment'].value_counts().reset_index()

    fig = px.pie(viz_df, values='count', names='comment', height=300)
    # fig.update_xaxes(tickwidth=1, range=(1, 8.2))
    fig.update_traces(textposition='inside', textinfo='value')
    fig.update_layout(
        {
            "plot_bgcolor": "rgba(0, 0, 0, 0)",  # make the background transparent
            "margin": {"l": 0, "r": 0, "t": 15, "b": 0}
        }
    )
    return fig, len(filter_zns_df)


def draw_order(total_order_df, sender_province, sender_district, receiver_province, receiver_district, carrier_status,
               w_range):

    filter_order_df = total_order_df.loc[
        (total_order_df['sender_province'] == sender_province)
        & (total_order_df['sender_district'] == sender_district)
        & (total_order_df['receiver_province'] == receiver_province)
        & (total_order_df['receiver_district'] == receiver_district)
        & (total_order_df['carrier_status'].isin(STATUS_MAPPING[carrier_status]))
        & (total_order_df['weight'] >= w_range[0])
        & (total_order_df['weight'] <= w_range[1])
        ]
    viz_df = filter_order_df['carrier'].value_counts().reset_index()

    fig = px.pie(viz_df, values='count', names='carrier')
    fig.update_traces(textposition='inside', textinfo='label+value')
    return fig, len(filter_order_df)


def create_analytic_tab():
    interactive = st.container()
    with interactive:
        # 1. Load data
        total_zns_df = st_get_data_zns()
        comment_zns_df = total_zns_df[['receiver_province', 'receiver_district', 'carrier', 'comment']].explode(
            column='comment')
        comment_zns_df = comment_zns_df.loc[comment_zns_df['comment'].notna()]

        # 2. Thống kê data ZNS
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

        # 2.1 ZNS message div
        opt_zns_mess_province, opt_zns_mess_district = chart_zns_message.columns(2)
        opt_zns_mess_province.selectbox(  # multiselect
            ":blue[**Chọn Tỉnh/Thành Phố**]",
            options=total_zns_df['receiver_province'].unique().tolist(),
            # default=['Thành phố Hà Nội'],
            key='zns_province',
        )
        opt_zns_mess_district.selectbox(
            ":blue[**Chọn Quận/Huyệni**]",
            options=total_zns_df.loc[
                (total_zns_df['receiver_province'] == st.session_state['zns_province'])
            ]['receiver_district'].unique().tolist(),
            # default=['Quận Đống Đa'],
            key='zns_district',
        )
        opt_zns_mess_star, opt_zns_mess_range_date = chart_zns_message.columns([2, 3])
        opt_zns_mess_star.selectbox(
            ":blue[**Chọn số sao đánh giá**]",
            options=total_zns_df.loc[
                (total_zns_df['receiver_province'] == st.session_state['zns_province'])
                & (total_zns_df['receiver_district'] == st.session_state['zns_district'])
                ]['n_stars'].unique().tolist(),
            # default=[1, 5],
            key='zns_star',
        )
        filter_zns_df = total_zns_df.loc[
            (total_zns_df['receiver_province'] == st.session_state['zns_province'])
            & (total_zns_df['receiver_district'] == st.session_state['zns_district'])
            & (total_zns_df['n_stars'] == st.session_state['zns_star'])
            ]
        opt_zns_mess_range_date.slider(
            label=":blue[**Chọn khoảng thời gian**]",
            min_value=filter_zns_df['reviewed_at'].min().date(),
            max_value=filter_zns_df['reviewed_at'].max().date(),
            step=timedelta(days=1),
            key='zns_range_date',
            value=(filter_zns_df['reviewed_at'].min().date(), filter_zns_df['reviewed_at'].max().date())
        )
        fig_zns_mess_by_carrier, len_zns_mess = draw_n_zns_message(
            total_zns_df,
            province=st.session_state['zns_province'],
            district=st.session_state['zns_district'],
            n_stars=st.session_state['zns_star'],
            r_date=st.session_state['zns_range_date']
        )

        chart_zns_message.plotly_chart(fig_zns_mess_by_carrier)
        chart_zns_message.info(f'Tổng số đánh giá: :red[**{len_zns_mess}**]')

        # ----------------------------------------------------------------------------------------------

        # 2.2 ZNS comment div
        opt_zns_com_province, opt_zns_com_district = chart_zns_comment.columns(2)

        opt_zns_com_province.selectbox(
            ":blue[**Chọn Tỉnh/Thành Phố**]",
            options=comment_zns_df['receiver_province'].unique().tolist(),
            # default=['Thành phố Hà Nội'],
            key='zns_province2',
        )
        opt_zns_com_district.selectbox(
            ":blue[**Chọn Quận/Huyệni**]",
            options=comment_zns_df.loc[
                (comment_zns_df['receiver_province'] == st.session_state['zns_province2'])
            ]['receiver_district'].unique().tolist(),
            # default=['Quận Đống Đa'],
            key='zns_district2',
        )
        chart_zns_comment.selectbox(
            ":blue[**Chọn nhà vận chuyển**]",
            options=comment_zns_df.loc[
                (comment_zns_df['receiver_province'] == st.session_state['zns_province2'])
                & (comment_zns_df['receiver_district'] == st.session_state['zns_district2'])
                ]['carrier'].unique().tolist(),
            # default=['BEST Express'],
            key='zns_carrier',
        )
        fig_zns_com_by_carrier, len_zns_com = draw_n_zns_comment(
            comment_zns_df,
            province=st.session_state['zns_province2'],
            district=st.session_state['zns_district2'],
            carrier=st.session_state['zns_carrier'],
        )

        chart_zns_comment.plotly_chart(fig_zns_com_by_carrier)
        chart_zns_comment.info(f'Tổng số comment: :red[**{len_zns_com}**]')

        st.divider()
        # ----------------------------------------------------------------------------------------------

        # 3. Thống kê đơn hàng
        # 3.1 Load data
        total_order_df = st_get_data_order()
        # 3.2 Thống kê data
        st.info(
            f"""
                **Thống kê dữ liệu :red[đơn hàng]**   
                * Thông tin:  
                👉 Khoảng thời gian đánh giá: Từ :red[**{total_order_df['created_at'].min().date()}**] đến :red[**{total_order_df['created_at'].max().date()}**]   
                👉 Số đơn hàng theo :red[**Khu vực**], :red[**Trạng thái giao hàng**] :red[**Khối lượng**] và :red[**Khoảng thời gian**] tùy chọn  
                👉 Thống kê khu vực :red[**nghẽn**] 
            """
        )

        chart_order, _, chart_stuck = st.columns([4, 1, 3])
        opt_order_sender_province, opt_order_sender_district = chart_order.columns(2)

        opt_order_sender_province.selectbox(
            ":blue[**Chọn Tỉnh/Thành Phố Giao**]",
            options=total_order_df['sender_province'].unique().tolist(),
            # default=['Thành phố Hà Nội'],
            key='order_sender_province',
        )
        opt_order_sender_district.selectbox(
            ":blue[**Chọn Quận/Huyện Giao**]",
            options=total_order_df.loc[
                (total_order_df['sender_province'] == st.session_state['order_sender_province'])
            ]['sender_district'].unique().tolist(),
            # default=['Quận Đống Đa'],
            key='order_sender_district',
        )

        opt_order_receiver_province, opt_order_receiver_district = chart_order.columns(2)

        opt_order_receiver_province.selectbox(
            ":blue[**Chọn Tỉnh/Thành Phố Nhận**]",
            options=total_order_df.loc[
                (total_order_df['sender_province'] == st.session_state['order_sender_province'])
                & (total_order_df['sender_district'] == st.session_state['order_sender_district'])
                ]['receiver_province'].unique().tolist(),
            # default=['Thành phố Hồ Chí Minh'],
            key='order_receiver_province',
        )
        opt_order_receiver_district.selectbox(
            ":blue[**Chọn Quận/Huyện Nhận**]",
            options=total_order_df.loc[
                (total_order_df['sender_province'] == st.session_state['order_sender_province'])
                & (total_order_df['sender_district'] == st.session_state['order_sender_district'])
                & (total_order_df['receiver_province'] == st.session_state['order_receiver_province'])
                ]['receiver_district'].unique().tolist(),
            # default=['Quận 1'],
            key='order_receiver_district',
        )

        opt_carrier_status, opt_weight_range = chart_order.columns(2)
        opt_carrier_status.selectbox(
            ":blue[**Chọn trạng thái đơn hàng**]",
            options=('Chưa giao hàng', 'Đang giao', 'Hoàn hàng', 'Thành công', 'Thất lạc', 'Không xét'),
            # default=['Thành công'],
            key='order_carrier_status',
        )

        opt_weight_range.slider(
            label=":blue[**Chọn khoảng khối lượng đơn**]",
            min_value=50,
            max_value=50000,
            step=50,
            key='order_weight_range',
            value=(500, 2000)
        )

        fig_order_by_carrier, len_order_by_carrier = draw_order(
            total_order_df,
            sender_province=st.session_state['order_sender_province'],
            sender_district=st.session_state['order_sender_district'],
            receiver_province=st.session_state['order_receiver_province'],
            receiver_district=st.session_state['order_receiver_district'],
            carrier_status=st.session_state['order_carrier_status'],
            w_range=st.session_state['order_weight_range']
        )

        chart_order.plotly_chart(fig_order_by_carrier)
        chart_order.info(f"Tổng số đơn: :red[**{len_order_by_carrier}**]")
        st.divider()
        # ----------------------------------------------------------------------------------------------
