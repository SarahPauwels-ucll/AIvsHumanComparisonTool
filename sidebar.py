import streamlit as st
from streamlit_cookies_controller import CookieController


def load_sidebar():
    controller = CookieController()
    st.sidebar.title("Dental Chart")
    # Profile number
    stored_profile_number = controller.get("ProfileNumber") or ""
    profile_number = st.sidebar.text_input("Profile number", value=stored_profile_number)
    if profile_number and profile_number != stored_profile_number:
        controller.set("ProfileNumber", profile_number)

    # Last name
    stored_last_name = controller.get("LastName") or ""
    last_name = st.sidebar.text_input("Last name", value=stored_last_name)
    if last_name and last_name != stored_last_name:
        controller.set("LastName", last_name)

    # First name
    stored_first_name = controller.get("FirstName") or ""
    first_name = st.sidebar.text_input("First name", value=stored_first_name)
    if first_name and first_name != stored_first_name:
        controller.set("FirstName", first_name)

    # Gender
    stored_gender = controller.get("Gender") or ""
    selected_index = None
    if stored_gender == "Male":
        selected_index = 0
    if stored_gender == "Female":
        selected_index = 1
    gender = st.sidebar.radio("Gender", ["Male", "Female"], index=selected_index)
    if gender and gender != stored_gender:
        controller.set("Gender", gender)

    # Age
    stored_age = controller.get("Age") or 30
    age = st.sidebar.number_input("Select age", step=1, value=stored_age)
    if age and age != stored_age:
        controller.set("Age", age)