import sys
from pathlib import Path
import streamlit as st

ROOT_PATH = str(Path(__file__).parent.parent.parent)
sys.path.append(ROOT_PATH)
from scripts.streamlit.manual import create_manual_tab
from scripts.streamlit.customer import create_customer_tab
from scripts.streamlit.partner import create_partner_tab
from scripts.streamlit.authenticator import Authenticator

st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded"
)
st.title("Tối ưu vận chuyển (SuperShipAI)")

authenticator = Authenticator()
st.sidebar.header("Login")
authenticator.login(location='sidebar')
if st.session_state["authentication_status"]:
    tab1, tab2, tab3 = st.tabs(["Manual", "Customer", "Partner"])
    with tab1:
        create_manual_tab()
    with tab2:
        create_customer_tab()
    with tab3:
        create_partner_tab()
elif st.session_state["authentication_status"] is False:
    st.sidebar.error('Username/password is incorrect')
elif st.session_state["authentication_status"] is None:
    st.sidebar.warning('Please enter your username and password')

st.sidebar.header("Register")
authenticator.register_user(location='sidebar')
