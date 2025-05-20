import streamlit as st

# Define a session flag to trigger the page switch
if "go_to_next_page" not in st.session_state:
    st.session_state.go_to_next_page = False

# Perform the page switch "outside" the callback
if st.session_state.go_to_next_page:
    st.session_state.go_to_next_page = False
    st.switch_page("pages/Upload_img.py")

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

    if login_button:
        if login(username, password):
            st.session_state["Proffesional"]=True
            st.session_state.go_to_next_page = True
            st.switch_page("pages/Upload_img.py")
        else:
            st.error("Invalid username or password.")

if st.session_state.get('logged_in'):
    st.info(f"You are logged in as {st.session_state['username']}.")