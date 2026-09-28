import streamlit as st

from modules.api_client import ApiError, login, signup
from modules.theme import INK_NAVY, PAPER


def _render_hero():
    st.markdown(
        f"""
        <div style="background:{INK_NAVY};padding:2.5rem 2rem;border-radius:8px;margin-bottom:2rem;">
            <div style="font-family:'Fraunces',serif;font-size:2rem;font-weight:600;color:{PAPER};">Meridian Shield</div>
            <div style="color:{PAPER}bb;font-size:1rem;margin-top:0.35rem;">
                Claims processing workspace -- coverage, history, and fraud-risk review, assisted by an AI agent whose recommendation is always reviewed by a person before it's final.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _login_form():
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Log in")

    if submitted:
        if not username.strip() or not password:
            st.error("Please enter your username and password.")
            return

        try:
            token_response = login(username, password)
        except ApiError as exc:
            st.error(exc.detail)
        else:
            st.session_state["access_token"] = token_response["access_token"]
            st.session_state["username"] = username
            st.rerun()


def _signup_form():
    with st.form("signup_form"):
        customer_id = st.text_input("Customer ID", help="The customer ID from your policy documents, e.g. CUST-005")
        username = st.text_input("Choose a username")
        password = st.text_input("Choose a password", type="password", help="At least 8 characters, with a mix of letters and numbers")
        confirm_password = st.text_input("Confirm password", type="password")
        submitted = st.form_submit_button("Create account")

    if submitted:
        if not customer_id.strip() or not username.strip() or not password:
            st.error("Please fill in all fields.")
            return

        if password != confirm_password:
            st.error("Passwords don't match.")
            return

        try:
            signup(customer_id, username, password)
        except ApiError as exc:
            st.error(exc.detail)
        else:
            st.success("Account created. Switch to the Log In tab to sign in.")


def render_auth_view():
    _render_hero()

    center = st.columns([1, 2, 1])[1]
    with center:
        login_tab, signup_tab = st.tabs(["Log In", "Sign Up"])
        with login_tab:
            _login_form()
        with signup_tab:
            _signup_form()

