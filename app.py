import streamlit as st
from streamlit_cookies_controller import CookieController

USER_CREDENTIALS = {
    "admin": "1234",
    "sarah": "password"
}

def login(username, password):
    if username in USER_CREDENTIALS:
        return USER_CREDENTIALS[username] == password
    return False

st.title("Login Page")

st.markdown("""
    <style>
    .st-key-login-container {
        max-width: 900px;
        margin: 0 auto;
    }
    </style>
    """, unsafe_allow_html=True)
with st.container(key="login-container"):
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login_button = st.form_submit_button("Login")
        student_button =st.form_submit_button("Continue as Student")

    if login_button:
        if login(username, password):
            st.session_state["Professional"]=True
            controller = CookieController()
            controller.set("Professional", True)
            st.switch_page("pages/Upload_img.py")
        else:
            st.error("Invalid username or password.")
    if student_button:
        st.session_state["Professional"]=False
        controller = CookieController()
        controller.set("Professional", False)
        st.switch_page("pages/Upload_img.py")
st.image("omfs_logo.png")