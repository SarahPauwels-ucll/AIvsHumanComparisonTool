import streamlit as st
import re
from streamlit_cookies_controller import CookieController
from datetime import date
import regex

def load_sidebar():
    if "go_to_login" not in st.session_state:
        st.session_state.go_to_login = False

    # Perform the page switch "outside" the callback
    if st.session_state.go_to_login:
        st.session_state.go_to_login = False
        st.switch_page("app.py")
    controller = CookieController()
    st.sidebar.title("Dental Chart")
    name_pattern = regex.compile(r"^[\p{L}'-]*$", regex.UNICODE)

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

    # -- birthdate --
    stored_birthdate_str = controller.get("birthdate")
    stored_birthdate = date.fromisoformat(stored_birthdate_str) if stored_birthdate_str else None
    if "birthdate" not in st.session_state or not st.session_state.birthdate:
        st.session_state.birthdate = stored_birthdate
        
    birthdate = st.sidebar.date_input("Select birthdate", value=st.session_state.birthdate, key="birthdate",
                                      min_value=date(1900, 1, 1), max_value='today')
    if birthdate != stored_birthdate:
        if birthdate:
            controller.set("birthdate", birthdate.isoformat())

    # -- Consultation date --
    stored_consultation_date_str = controller.get("consultation date")
    stored_consultation_date = date.fromisoformat(stored_consultation_date_str) if stored_consultation_date_str else None
    if "consultation date" not in st.session_state  or not st.session_state.consultation_date:
        st.session_state.consultation_date = stored_consultation_date

    consultation_date = st.sidebar.date_input("Select consultation date", value=st.session_state.consultation_date, key="consultation date",min_value=None, max_value='today')
    if consultation_date != stored_consultation_date:
        if consultation_date:
            controller.set("consultation date", consultation_date.isoformat()) 

    if consultation_date!=None and birthdate!=None:
        years = consultation_date.year - birthdate.year - ((consultation_date.month, consultation_date.day) < (birthdate.month, birthdate.day))
        st.sidebar.markdown(f"Age: {years}")

    def logout():
        controller = CookieController()
        keys_to_clear = [
            "ProfileNumber",
            "LastName",
            "FirstName",
            "birthdate",
            "consultation date",
            "Gender",
            "Proffesional"
        ]
        for key in st.session_state.keys():
            del st.session_state[key]
        for key in keys_to_clear:  
            controller.set(key, None)
        st.cache_data.clear()
        st.session_state.go_to_login = True

    stored_proffesional = controller.get("Proffesional") if controller.get("Proffesional") is not None else False
    if "Proffesional" not in st.session_state  or not st.session_state.Proffesional:
        st.session_state.Proffesional = stored_proffesional
    if st.session_state.Proffesional:
        st.sidebar.button("Log out",on_click=logout)
    else:
        st.sidebar.button("Log In",on_click=logout)

