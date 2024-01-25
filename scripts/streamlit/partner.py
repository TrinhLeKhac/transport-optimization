from scripts.streamlit.streamlit_helper import *
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def draw_fee_error(total_analyze_df):
    fee_err_div, fee_err_info = st.columns([3, 2])
    fee_err_info.info(
        """
        **Chart này mô tả tương quan giữa đường biểu diễn :red[chi phí] và :red[lỗi] khi thay đổi score**  
        👉 Đường :red[**chi phí**] tỉ lệ thuận với :red[**score**]  
        👉 Số :red[**lỗi phát sinh**] tỉ lệ nghịch với :red[**score**]    
        👉 :red[***Điểm tối ưu là giao nhau giữa 2 đường chi phí và lỗi***]   
        """
    )
    # ----------------------------------------------------------------------------------------------

    viz_df = total_analyze_df[['score', 'monetary', 'total_error']].drop_duplicates()

    # subfig = make_subplots(specs=[[{"secondary_y": True}]])

    fig = px.line(
        viz_df,
        x='score',
        y='monetary',
        title='',
    )
    fig.update_traces(line=dict(color='seagreen'), showlegend=True)

    fig2 = px.line(viz_df, x='score', y='total_error')
    # Change the axis for fig2
    fig2.update_traces(yaxis='y2', line=dict(color='indianred'), showlegend=True)

    # Add the figs to the subplot figure
    # subfig.add_traces(fig.data + fig2.data)

    fig.add_trace(fig2.data[0])
    fig.update_layout(
        xaxis=dict(title='Score'),
        yaxis=dict(title='Tổng tiền cước'),
        yaxis2=dict(title='Tổng lỗi', overlaying='y', side='right'),
    )
    fee_err_div.plotly_chart(fig)


def score_sidebar(total_analyze_df):
    slider_div, _, div_info = st.columns([2, 1, 2])
    div_info.info(
        """
        **Kéo thanh :red[slidebar] để chọn ngưỡng :red[score] mong muốn**  
        👉 Công thức: :red[*score = 2.5 + slidebar_value * 0.025*]  
    """
    )
    slider_num = slider_div.slider("", min_value=0, max_value=100, value=70)

    _th = 2.5 + slider_num * 0.025
    slider_div.info(f'**Score: :red[{str(_th)[:5]}]**')

    viz_df = total_analyze_df[total_analyze_df['score'] == _th]
    slider_div.info(
        f"""
        Tổng số đơn :red[**trên**] ngưỡng lọc: :red[**{str(viz_df['n_good_order'].values[0])}**]     
        Tổng số đơn :red[**dưới**] ngưỡng lọc: :red[**{str(viz_df['n_bad_order'].values[0])}**]     
        """
    )
    return _th


def error_by_score(total_analyze_df, threshold=0.75):
    viz_df = total_analyze_df[total_analyze_df['score'] == threshold]
    viz_df1 = viz_df.groupby('carrier')['n_errors'].sum().reset_index()

    carriers = viz_df1['carrier'].tolist()

    fig = go.Figure()
    bar_width = 0.5
    fig.add_trace(
        go.Bar(
            x=carriers,
            y=viz_df1['n_errors'],
            width=bar_width,
            text=viz_df1['n_errors'],
            marker_color=['#2596BE']*len(carriers),
            # marker_color=px.colors.sequential.YlOrRd_r[0:len(carriers)],
        )
    )

    fig.update_layout(
        xaxis=dict(title='Nhà vận chuyển', categoryorder='total descending'),
        yaxis=dict(title='Tổng số lỗi'),
        # legend=dict(
        #     orientation='h',
        #     y=1.12,
        #     x=0.15
        # ),
        # legend_title='',
        height=500,
        # width=800
    )
    return fig


def detail_error_by_carrier(total_analyze_df, opt_carrier, type_viz='error_type', x_legend_position=0.4,
                            threshold=0.75):
    viz_df = total_analyze_df[
        (total_analyze_df['score'] == threshold)
        & (total_analyze_df['carrier'] == opt_carrier)
        ].groupby(type_viz)['n_errors'].sum().reset_index()
    categories = viz_df[type_viz].tolist()

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=viz_df['n_errors'],
            y=categories,
            text=viz_df['n_errors'],
            orientation='h',
            marker_color=['#2596BE']*len(categories),
        )
    )

    fig.update_layout(
        xaxis=dict(title='Tổng số lỗi'),
        yaxis=dict(categoryorder='total descending'),
        height=500,
    )
    return fig


def analyze_by_carrier(total_analyze_df, type_viz='n_orders', threshold=0.75):

    viz_df = total_analyze_df[total_analyze_df['score'] == threshold]
    categories = sorted(viz_df['carrier'].unique())
    groups = ['good', 'bad']  # sorted(viz_df['quality'].unique())
    colors = {
        'good': '#2596BE',
        'bad': 'firebrick'
    }

    fig = go.Figure()
    bar_width = 0.3
    for i, group in enumerate(groups):
        group_data = viz_df[viz_df['quality'] == group]
        positions = [pos + i * bar_width for pos in range(len(categories))]
        fig.add_trace(
            go.Bar(
                x=positions,
                y=group_data[type_viz],
                name=group,
                width=bar_width,
                marker_color=colors[group]
            )
        )

    if type_viz == 'n_orders':
        y_title = 'Số đơn hàng'
    elif type_viz == 'monetary':
        y_title = 'Tổng tiền'
    else:
        y_title = ''

    fig.update_layout(
        xaxis=dict(tickvals=[pos + (len(groups) - 1) * bar_width / 2 for pos in range(len(categories))],
                   ticktext=categories, title='Nhà vận chuyển', categoryorder='total descending'),
        yaxis=dict(title=y_title),
        barmode='group',
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


def find_intersection(x1,y1, x2,y2, x3,y3, x4,y4):
    """
        the first line is defined by the line between point1(x1, y1) and point2(x2, y2)
        the first line is defined by the line between point3(x3, y3) and point4(x4, y4)
    """
    px= ((x1*y2-y1*x2)*(x3-x4)-(x1-x2)*(x3*y4-y3*x4)) / ((x1-x2)*(y3-y4)-(y1-y2)*(x3-x4))
    py= ((x1*y2-y1*x2)*(y3-y4)-(y1-y2)*(x3*y4-y3*x4)) / ((x1-x2)*(y3-y4)-(y1-y2)*(x3-x4))
    return px, py


def get_optimal_point(input_df, step=2):
    target_df = input_df[['score', 'monetary', 'total_error']].drop_duplicates().reset_index(drop=True)

    optimal_point = -1
    error_max = target_df['total_error'].max()
    monetary_max = target_df['monetary'].max()
    scale = monetary_max / error_max

    for idx in range(len(target_df) - step):
        # print(idx)
        point1 = (target_df.loc[idx, 'score'], target_df.loc[idx, 'monetary'] / scale)
        point2 = (target_df.loc[idx + step, 'score'], target_df.loc[idx + step, 'monetary'] / scale)
        point3 = (target_df.loc[idx, 'score'], target_df.loc[idx, 'total_error'])
        point4 = (target_df.loc[idx + step, 'score'], target_df.loc[idx + step, 'total_error'])

        R = find_intersection(*point1, *point2, *point3, *point4)

        print(point1, point2, point3, point4, idx, R)

        if (R[0] >= target_df.loc[idx, 'score']) and (R[0] <= target_df.loc[idx + step, 'score']):
            optimal_point = idx + step//2
            score = target_df.loc[optimal_point, 'score']
            break
    return score


def create_partner_tab():
    interactive = st.container()
    with interactive:
        # 1. Info
        st.info(
            """
            **Modules này hỗ trợ chọn :red[score tối ưu vận chuyển] một cách trực quan dựa vào thống kê :red[lỗi] và :red[chi phí]**
            * Thông tin:  
            👉 Chart tương quan chi phí - lỗi    
            👉 Chart hiển thị lỗi chi tiết của NVC    
            * Tiêu chí chọn đơn:  
            👉 Nếu tồn tại ít nhất 1 NVC có điểm >= ngưỡng, chọn NVC có cước phí nhỏ nhất  
            👉 Nếu tất cả các NVC có điểm < ngưỡng, chọn NVC có score cao nhất  
        """
        )
        st.divider()
        # ----------------------------------------------------------------------------------------------

        total_analyze_df1, total_analyze_df2 = st_get_data_viz()

        # 2. Tương quan chi phí - lỗi
        draw_fee_error(total_analyze_df1)

        score = get_optimal_point(total_analyze_df1)
        opt_point_div, _ = st.columns([1, 1])
        opt_point_div.info(
            f"""
            Optimal point: :red[**{score}**]
            """
        )

        st.divider()
        # ----------------------------------------------------------------------------------------------

        # 3.Điều chỉnh theo score
        # _, score_div, _ = st.columns([1, 4, 1])
        # with score_div:
        _th = score_sidebar(total_analyze_df1)
        st.divider()
        # ----------------------------------------------------------------------------------------------

        # 4. Thống kê lỗi Nhà vận chuyển

        # 4.1 Info
        select_div, _, info_err_div = st.columns([1, 1, 2])
        info_err_div.info(
            """
            **Thống kê lỗi của NVC theo :red[ngưỡng score]**
            * Thông tin:  
            👉 Chart bên trái: :red[**Tổng số lỗi**] của Nhà vận chuyển  
            👉 Chart bên phải: :red[**Chi tiết lỗi**] của Nhà vận chuyển theo :red[**loại vận chuyển**] hoặc :red[**category lỗi**]  
        """
        )
        with select_div:
            viz_df = total_analyze_df1[total_analyze_df1['score'] == _th]
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

        detail_error_by_carrier_div, _, error_by_score_div = st.columns([4, 1, 4])

        fig_error_by_score = error_by_score(total_analyze_df1, threshold=_th)

        if opt_type_viz == 'Category lỗi':
            fig_detail_error_by_score = detail_error_by_carrier(
                total_analyze_df1, opt_carrier,
                type_viz='error_type', x_legend_position=0.4, threshold=_th
            )
        elif opt_type_viz == 'Loại vận chuyển':
            fig_detail_error_by_score = detail_error_by_carrier(
                total_analyze_df1, opt_carrier,
                type_viz='order_type', x_legend_position=0.2, threshold=_th)

        fig_detail_error_by_score.update_layout(yaxis=dict(anchor='x'), barmode='stack')

        # 4.2 Thống kê tổng lỗi NVC theo score
        with error_by_score_div:
            st.plotly_chart(fig_error_by_score)

        # 4.3 Thống kê lỗi chi tiết của NVC theo score
        with detail_error_by_carrier_div:
            st.plotly_chart(fig_detail_error_by_score)

        st.divider()
        # ----------------------------------------------------------------------------------------------
        # 5. Thống kê trên/dưới ngưỡng score

        # 5.1 Info
        st.info(
            """
            **Thống kê chi tiết :red[số đơn hàng + số tiền] theo ngưỡng lọc score của từng NVC**
            * Thông tin:  
            👉 Chart bên trái: Phân bố :red[**đơn hàng**]  
            👉 Chart bên phải: Phân bố :red[**cước phí**]  
        """
        )
        analyze_by_order_div, _, analyze_by_money_div = st.columns([4, 1, 4])

        fig_order_by_carrier = analyze_by_carrier(total_analyze_df2, type_viz='n_orders', threshold=_th)
        fig_monatary_by_carrier = analyze_by_carrier(total_analyze_df2, type_viz='monetary', threshold=_th)
        fig_monatary_by_carrier.update_layout(yaxis=dict(anchor='x'), barmode='stack')

        # 5.2. Thống kê đơn theo nhà vận chuyển
        with analyze_by_order_div:
            st.plotly_chart(fig_order_by_carrier)

        # 5.3. Thống kê tiền theo nhà vận chuyển
        with analyze_by_money_div:
            st.plotly_chart(fig_monatary_by_carrier)
