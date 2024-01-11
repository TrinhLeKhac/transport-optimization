import optparse
import sys
from datetime import datetime
from pathlib import Path

import streamlit as st

ROOT_PATH = str(Path(__file__).parent.parent.parent)
sys.path.append(ROOT_PATH)
from scripts.streamlit.manual import create_manual_tab
from scripts.streamlit.customer import create_customer_tab
from scripts.streamlit.partner import create_partner_tab
from scripts.streamlit.analytic import create_analytic_tab
from scripts.streamlit.authenticator import Authenticator


def main(run_date_str, is_auth=True):
    st.set_page_config(
        layout="wide",
        initial_sidebar_state="expanded"
    )
    streamlit_style = """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@100&display=swap');
        html, body, [class*="css"]  {
        font-family: 'Roboto', sans-serif;
        }
        </style>
    """
    st.markdown(streamlit_style, unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; color: #2596BE;'>Tối ưu vận chuyển (SuperShipAI)</h1>",
                unsafe_allow_html=True)
    st.markdown("""
        <style>
            .stTabs [data-baseweb="tab-list"] {
                gap: 10px;
            }
            .stTabs [data-baseweb="tab"] {
                height: 30px;
                background-color: #C6EAEC;
                border-radius: 5px 5px 0px 0px;
                padding: 5px 30px 5px 30px;
            }
            .stTabs [aria-selected="true"] {
                background-color: #2596BE;
            }
        </style>""", unsafe_allow_html=True)

    if is_auth:
        authenticator = Authenticator()
        st.sidebar.header("Login")
        authenticator.login(location='sidebar')
        if st.session_state["authentication_status"]:
            tab1, tab2, tab3, tab4 = st.tabs(["Manual", "Customer", "Analytic", "Partner"])
            with tab1:
                create_manual_tab()
            with tab2:
                create_customer_tab()
            with tab3:
                create_analytic_tab(run_date_str)
            with tab4:
                create_partner_tab()
        elif st.session_state["authentication_status"] is False:
            st.sidebar.error('Username/password is incorrect')
        elif st.session_state["authentication_status"] is None:
            st.sidebar.warning('Please enter your username and password')

        st.sidebar.header("Register")
        authenticator.register_user(location='sidebar')
    else:
        tab1, tab2, tab3, tab4 = st.tabs(["Manual", "Customer", "Analytic", "Partner"])
        with tab1:
            create_manual_tab()
        with tab2:
            create_customer_tab()
        with tab3:
            create_analytic_tab(run_date_str)
        with tab4:
            create_partner_tab()


if __name__ == '__main__':

    parser = optparse.OptionParser(description="Running mode")
    parser.add_option(
        '-r', '--run_date',
        action="store", dest="run_date",
        help="run_date string", default=f"{datetime.now().strftime('%Y-%m-%d')}"
    )
    options, args = parser.parse_args()
    main(options.run_date, is_auth=True)
