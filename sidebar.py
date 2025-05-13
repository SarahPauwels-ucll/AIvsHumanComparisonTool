import streamlit as st
from st_pages import Page, add_page_title


def load_sidebar():

    if "user_input" not in st.session_state:
       st.session_state["user_input"] = "kjlj"
    
    st.sidebar.title("Dental Chart")
    ProfileNumber = st.sidebar.text_input("Profile number", key="user_input")
    LastName = st.sidebar.text_input("Last name")
    FirstName = st.sidebar.text_input("First name")
    gender = st.sidebar.radio("Gender", ["Male", "Female"])
    age = st.sidebar.text_input("Select your age")