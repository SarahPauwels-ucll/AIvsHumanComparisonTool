import streamlit as st
import re
from streamlit_cookies_controller import CookieController

def load_sidebar():
    controller = CookieController()
    st.sidebar.title("Dental Chart")
    name_pattern = re.compile(r"^[a-zA-Z'-]*$")

    # --- Profile Number ---
    stored_profile_number = controller.get("ProfileNumber")
    stored_profile_number = str(stored_profile_number) if stored_profile_number is not None else ""

    if "profile_number" not in st.session_state or not st.session_state.profile_number:
        st.session_state.profile_number = stored_profile_number

    profile_number_input = st.sidebar.text_input(
        "Profile number",
        value=st.session_state.profile_number,
        key="profile_number"
    )

    if profile_number_input.isdigit():
        if profile_number_input != stored_profile_number:
            controller.set("ProfileNumber", profile_number_input)
    elif profile_number_input:
        st.sidebar.error("Profile number must be a number.")

    # --- Last Name ---
    stored_last_name = controller.get("LastName") or ""
    if "last_name" not in st.session_state or not st.session_state.last_name:
        st.session_state.last_name = stored_last_name

    last_name = st.sidebar.text_input("Last name", value=st.session_state.last_name, key="last_name")

    if name_pattern.fullmatch(last_name):
        if last_name != stored_last_name:
            controller.set("LastName", last_name)
    elif last_name:
        st.sidebar.error("Last name can only contain letters, apostrophes ('), and hyphens (-).")

    # --- First Name ---
    stored_first_name = controller.get("FirstName") or ""
    if "first_name" not in st.session_state or not st.session_state.first_name:
        st.session_state.first_name = stored_first_name

    first_name = st.sidebar.text_input("First name", value=st.session_state.first_name, key="first_name")

    if name_pattern.fullmatch(first_name):
        if first_name != stored_first_name:
            controller.set("FirstName", first_name)
    elif first_name:
        st.sidebar.error("First name can only contain letters, apostrophes ('), and hyphens (-).")

    # --- Gender ---
    stored_gender = controller.get("Gender")
    if "gender" not in st.session_state or not st.session_state.gender:
        st.session_state.gender = stored_gender

    gender = st.sidebar.radio("Gender", ["Male", "Female"],
                              index=0 if st.session_state.gender == "Male" else 1,
                              key="gender")

    if gender != stored_gender:
        controller.set("Gender", gender)

    # --- Age ---
    stored_age = controller.get("Age")
    try:
        stored_age = int(stored_age)
        if stored_age < 0:
            stored_age = 0
    except (ValueError, TypeError):
        stored_age = 30

    if "age" not in st.session_state or not isinstance(st.session_state.age, int):
        st.session_state.age = stored_age

    age = st.sidebar.number_input("Select age", step=1, min_value=0,
                                  value=st.session_state.age, key="age")

    if age != stored_age:
        controller.set("Age", age)
