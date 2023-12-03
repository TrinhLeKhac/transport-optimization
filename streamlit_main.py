import sys
from pathlib import Path
ROOT_PATH = str(Path(__file__).parent.parent.parent)
sys.path.append(ROOT_PATH)
from scripts.streamlit.manual import create_manual_tab
from scripts.streamlit.customer import create_customer_tab
from scripts.output.out_data_final import *


st.title("Tối ưu vận chuyển (SuperShipAI)")

tab1, tab2, tab3 = st.tabs(["Manual", "Customer", "Partner"])
with tab1:
    create_manual_tab()
with tab2:
    create_customer_tab()