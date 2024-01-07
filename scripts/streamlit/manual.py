from scripts.output.out_data_api import out_data_api, assign_supership_carrier
from scripts.output.out_data_final import out_data_final, get_data_viz
from scripts.processing.total_processing import total_processing
from scripts.streamlit.streamlit_helper import *
import scripts.streamlit.redirect as rd


def create_manual_tab():

    st.info(
        """
        Page tính toán :red[**manual**] các thông số tối ưu vận chuyển   
        Dữ liệu sử dụng :red[**30 ngày**] gần nhất  
        
        **Import đầy đủ các files sau**  
        📂 Bảng cước phí (Nếu có update)  
        📂 :red[Đánh giá chất lượng nội bộ nhà vận chuyển]    
        📂 Thông tin bưu cục nhà vận chuyển (Nếu có update)    
        📂 :red[Thông tin vùng ngưng giao nhận]    
        📂 Phân vùng nhà vận chuyển (Nếu có update)    
        """
    )
    # ----------------------------------------------------------------------------------------------

    with st.expander("📂 :red[**Files cần upload**]"):
        cuoc_phi_file = st.file_uploader(":one: Bảng Cước Phí", type=['xlsx'])
        if cuoc_phi_file is not None:
            save_uploaded_file(cuoc_phi_file, "input")

        chat_luong_noi_bo_files = st.file_uploader(":two: Chất Lượng Nội Bộ", type=['xlsx'], accept_multiple_files=True)
        if chat_luong_noi_bo_files is not None:
            for file in chat_luong_noi_bo_files:
                save_uploaded_file(file, "input")

        kho_giao_nhan_files = st.file_uploader(":three: Bưu Cục", type=['xlsx'], accept_multiple_files=True)
        if kho_giao_nhan_files is not None:
            for file in kho_giao_nhan_files:
                save_uploaded_file(file, "input")

        ngung_giao_nhan_file = st.file_uploader(":four: Ngưng giao nhận", type=['xlsx'])
        if ngung_giao_nhan_file is not None:
            save_uploaded_file(ngung_giao_nhan_file, "input")

        phan_vung_nvc_file = st.file_uploader(":five: Phân Vùng Nhà Vận Chuyển", type=['xlsx'])
        if phan_vung_nvc_file is not None:
            save_uploaded_file(phan_vung_nvc_file, "input")
    # ----------------------------------------------------------------------------------------------

    # 1. Processing dữ liệu
    if 'data_state' not in st.session_state:
        st.session_state['data_state'] = False

    data_button = st.button('Xử lý dữ liệu', type="primary")

    if data_button and st.session_state['data_state']:
        st.info('Đã xử lý xong dữ liệu')

    if data_button and not st.session_state['data_state']:
        try:
            start_processing = time()
            with st.spinner('Đang xử lý...'):
                with rd.stdout(format="code"):
                    total_processing(from_api=True)
            stop_processing = time()
            st.info('Thời gian xử lý: ' + convert_time_m_s(stop_processing, start_processing))
            st.session_state['data_state'] = True
        except Exception as e:
            st.error("Có lỗi xảy ra")
    # ----------------------------------------------------------------------------------------------

    # 2. Xuất data API
    if 'api_state' not in st.session_state:
        st.session_state['api_state'] = False

    out_data_api_button = st.button('Xuất data API', type="primary")

    if out_data_api_button and st.session_state['api_state']:
        st.info('Đã có kết quả API')

    if out_data_api_button and not st.session_state['api_state']:
        try:
            start = time()
            with st.spinner('Đang xử lý...'):
                with rd.stdout(format='code'):
                    df_api = out_data_api()
                    assign_supership_carrier(df_api)
            stop = time()
            st.session_state['api_state'] = True
            st.info('Thời gian xử lý: ' + convert_time_m_s(stop, start))
        except Exception as e:
            st.error("Có lỗi xảy ra")
    # ----------------------------------------------------------------------------------------------

    # 3. Xuất data API
    if 'viz_state' not in st.session_state:
        st.session_state['viz_state'] = False

    out_data_viz_button = st.button('Xuất data Viz', type="primary")

    if out_data_viz_button and st.session_state['viz_state']:
        st.info('Đã có kết quả Visualization')

    if out_data_viz_button and not st.session_state['viz_state']:
        try:
            start = time()
            with st.spinner('Đang xử lý...'):
                with rd.stdout(format='code'):
                    target_df = out_data_final()
                    get_data_viz(target_df)
            stop = time()
            st.session_state['viz_state'] = True
            st.info('Thời gian xử lý: ' + convert_time_m_s(stop, start))
        except Exception as e:
            st.error("Có lỗi xảy ra")
