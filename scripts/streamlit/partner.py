from scripts.streamlit.streamlit_helper import *
import streamlit as st
import plotly.express as px


def draw_fee_error(total_analyze_df):
    viz_df = total_analyze_df[['score', 'monetary', 'total_error']].drop_duplicates()
    fig = px.line(
        viz_df,
        x='score',
        y='monetary',
        title='Tương quan Chi phí - Lỗi',
        labels={'monetary': 'Tổng tiền cước'})

    fig.add_trace(px.line(viz_df, x='score', y='total_error').update_traces(yaxis='y2').data[0])
    fig.update_layout(
        xaxis=dict(title='Score'),
        yaxis=dict(title='Tổng tiền cước'),
        yaxis2=dict(title='Tổng lỗi', overlaying='y', side='right'),
    )
    st.plotly_chart(fig)


def score_sidebar(total_analyze_df):
    slider_num = st.slider("Chọn ngưỡng score", min_value=1, max_value=100, value=100)

    _th = 0.5 + slider_num * 0.005
    st.text('Score: ' + str(_th)[:5])

    viz_df = total_analyze_df[total_analyze_df['score'] == _th]
    st.text('Tổng số đơn trên ngưỡng lọc: ' + str(viz_df['n_good_order'].values[0]))
    st.text('Tổng số đơn dưới ngưỡng lọc: ' + str(viz_df['n_bad_order'].values[0]))
    return _th


def error_by_score(total_analyze_df, threshold=0.75):
    viz_df = total_analyze_df[total_analyze_df['score'] == threshold]
    viz_df1 = viz_df.groupby('carrier')['n_errors'].sum().reset_index()
    fig = px.bar(viz_df1, x='carrier', y='n_errors', color='carrier', text='n_errors', template='seaborn')
    fig.update_layout(
        xaxis=dict(title='Nhà vận chuyển', categoryorder='total descending'),
        yaxis=dict(title='Tổng số lỗi'),
        legend=dict(
            orientation='h',
            y=1.12,
            x=0.15
        ),
        legend_title='',
        height=500,
        # width=800
    )
    return fig


def detail_error_by_carrier(total_analyze_df, opt_carrier, type_viz='error_type', threshold=0.75):

    viz_df = total_analyze_df[
        (total_analyze_df['score'] == threshold)
        & (total_analyze_df['carrier'] == opt_carrier)
    ].groupby(type_viz)['n_errors'].sum().reset_index()
    fig = px.bar(viz_df, x=type_viz, y='n_errors', color=type_viz, text='n_errors', template='seaborn')
    fig.update_layout(
        xaxis=dict(title='', tickvals=[], categoryorder='total descending'),
        yaxis=dict(title='Số lỗi theo category'),
        legend=dict(
            orientation='h',
            y=1.12,
            x=0.4
        ),
        legend_title='',
        height=500,
        # width=800,
    )
    return fig


def create_partner_tab():
    interactive = st.container()
    with interactive:
        # 1. Toggle thông tin
        toggle = st.toggle('Thông tin', key='toggle_partner_tab')
        if toggle:
            st.markdown(
                """
                **Modules này hỗ trợ chọn score tối ưu vận chuyển một cách trực quan dựa vào thống kê lỗi và chi phí**
                * Thông tin:
                    * Chart tương quan chi phí - lỗi.
                    * Chart hiển thị lỗi chi tiết của NVC.
                * Tiêu chí chọn đơn:
                    * Nếu tồn tại ít nhất 1 NVC có điểm >= ngưỡng, chọn NVC có cước phí nhỏ nhất.
                    * Nếu tất cả các NVC có điểm < ngưỡng, chọn NVC có score cao nhất.
            """
            )

        total_analyze_df = st_get_data_viz()

        # 2. Tương quan chi phí - lỗi
        _, fee_err_div, _ = st.columns([1, 2, 1])
        with fee_err_div:
            draw_fee_error(total_analyze_df)
        st.markdown("---")

        # 3.Điều chỉnh theo score
        _, score_div, _ = st.columns([1, 4, 1])
        with score_div:
            _th = score_sidebar(total_analyze_df)
        st.markdown("---")

        # 4. Chọn NVC
        _, select_div = st.columns([3, 1])
        with select_div:
            viz_df = total_analyze_df[total_analyze_df['score'] == _th]
            opt_carrier = st.selectbox(
                "Chọn nhà vận chuyển",
                options=list(viz_df['carrier'].unique()),
                key='carrier',
            )
            opt_type_viz = st.selectbox(
                "Thống kê theo",
                options=['Category lỗi', 'Loại vận chuyển'],
                key='type_viz',
            )

        error_by_score_div, _, detail_error_by_carrier_div = st.columns([4, 1, 5])

        fig_error_by_score = error_by_score(total_analyze_df, threshold=_th)

        if opt_type_viz == 'Category lỗi':
            fig_detail_error_by_score = detail_error_by_carrier(total_analyze_df, opt_carrier, type_viz='error_type', threshold=_th)
        elif opt_type_viz == 'Loại vận chuyển':
            fig_detail_error_by_score = detail_error_by_carrier(total_analyze_df, opt_carrier, type_viz='order_type', threshold=_th)

        fig_detail_error_by_score.update_layout(yaxis=dict(anchor='x'), barmode='stack')
        # 5. Thống kê tổng lỗi NVC theo score
        with error_by_score_div:
            st.plotly_chart(fig_error_by_score)

        # 6. Thống kê lỗi chi tiết của NVC theo score
        with detail_error_by_carrier_div:
            st.plotly_chart(fig_detail_error_by_score)

        st.markdown("---")
