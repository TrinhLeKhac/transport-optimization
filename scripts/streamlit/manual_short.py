from scripts.output.out_data_api import out_data_api, assign_supership_carrier
from scripts.output.out_data_final import out_data_final, get_data_viz
from scripts.processing.total_processing import total_processing
from scripts.streamlit.streamlit_helper import *
import scripts.streamlit.redirect as rd


def create_manual_tab():

    st.info(
        """
        Page hỗ trợ update :red[**manual**] các files cần thiết cho quá trình tính toán  
        Dữ liệu sử dụng :red[**30 ngày**] gần nhất  
        Timeline khuyến nghị:   
        :one: Update data manual (:red[**17h30 chiều**])  
        :two: Update data API (:red[**24h tối**])  
        :three: Chạy job định kỳ (:red[**4h sáng, 11h trưa, 18h chiều**])  
        Khoảng thời gian :red[**downtime**] service: :red[**15p kể từ thời điểm chạy job định kỳ**]  
        
        **Import đầy đủ các files sau**  
        📂 Bảng cước phí (Nếu có update)  
        📂 :red[**Đánh giá chất lượng nội bộ nhà vận chuyển**]    
        📂 Thông tin bưu cục nhà vận chuyển (Nếu có update)    
        📂 :red[**Thông tin vùng ngưng giao nhận**]    
        📂 Phân vùng nhà vận chuyển (Nếu có update)    
        """
    )
    # ----------------------------------------------------------------------------------------------

    with st.expander("📂 :red[**Files cần upload**]"):
        ngung_giao_nhan_file = st.file_uploader(":four: Ngưng giao nhận", type=['xlsx'])
        if ngung_giao_nhan_file is not None:
            save_uploaded_file(ngung_giao_nhan_file, "input")