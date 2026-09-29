import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from modules.auth_view import render_auth_view  
from modules.dashboard_view import render_dashboard_view  
from modules.theme import GLOBAL_CSS 

st.set_page_config(page_title="Claims Processing Agent", page_icon="", layout="wide")
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


def main():
    if st.session_state.get("access_token"):
        render_dashboard_view()
    else:
        render_auth_view()


if __name__ == "__main__":
    main()


