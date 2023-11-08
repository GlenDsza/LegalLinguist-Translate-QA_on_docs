import streamlit as st
import time
from src.database import get_db, register_user, login_user

st.set_page_config(initial_sidebar_state='collapsed')


db = get_db()


def page_init():
    st.markdown(
        """
        <style>
            [data-testid="stSidebarNav"]::before {
                content: "Legal Linguist";
                margin-left: 20px;
                margin-top: 20px;
                font-size: 30px;
                position: relative;
                top: 80px;
                font-weight: bold;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    if 'authpage' not in st.session_state:
        st.session_state['authpage'] = 'login'

    if st.session_state['authpage'] and 'verif_email' not in st.session_state:
        if st.session_state['authpage'] == 'login':
            login_page()

            st.write("Don't have an account ? ")
            btn = st.button('Register')
            if btn:
                st.session_state['authpage'] = 'register'
                st.rerun()
            st.stop()
        elif st.session_state['authpage'] == 'register':
            register_page()
            st.write("Already have an account ? ")
            btn = st.button('Login')
            if btn:
                st.session_state['authpage'] = 'login'
                st.rerun()
            st.stop()


def register_action():
    name = st.session_state['name']
    email = st.session_state['email']
    password = st.session_state['password']

    if register_user(db, name, email, password):
        st.success("Registered successfully. Redirecting to login page...")
        time.sleep(2)
        st.session_state['authpage'] = 'login'
    else:
        st.error("User already exists.")
        time.sleep(1)


def login_action():
    email = st.session_state['email']
    password = st.session_state['password']

    print(email, password)

    if login_user(db, email, password):
        st.success("Logged in successfully. Redirecting to home page...")
        time.sleep(1)
        st.session_state['authpage'] = None
        st.session_state['verif_email'] = email
    else:
        st.error("Invalid credentials.")
        time.sleep(1)


def login_page():
    st.write("# Login")
    with st.form("login"):
        st.text_input("Email", key="email")
        st.text_input("Password", type="password", key="password")
        btn = st.form_submit_button("Login", on_click=login_action)
        if btn:
            st.rerun()


def register_page():
    st.write("# Register")
    with st.form("register"):
        st.text_input("Name", key="name")
        st.text_input("Email", key="email")
        st.text_input("Password", type="password", key="password")
        btn = st.form_submit_button("Register", on_click=register_action)
        if btn:
            st.rerun()
