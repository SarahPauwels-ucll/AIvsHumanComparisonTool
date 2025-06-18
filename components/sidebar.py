def load_sidebar(page="login"):
    import streamlit as st
    import re
    from streamlit_cookies_controller import CookieController
    from datetime import date
    import regex
    def logout():
        controller = CookieController()
        keys_to_clear = [
            "ProfileNumber",
            "LastName",
            "FirstName",
            "birthdate",
            "consultation date",
            "Gender",
            "Professional",
            "Teethkind",
            "studentName",
            "rnumber"
        ]
        for key in st.session_state.keys():
            del st.session_state[key]
        for key in keys_to_clear:
            if key in controller.getAll():
                controller.remove(key)
            else:
                print(key + " not found")
        st.cache_data.clear()
        st.session_state.just_logedin = True

    if "go_to_login" not in st.session_state:
        st.session_state.go_to_login = False

    # Perform the page switch "outside" the callback
    if st.session_state.go_to_login:
        st.session_state.go_to_login = False
        st.switch_page("app.py")
    controller = CookieController()
    
    try:
        stored_professional = controller.get("Professional") if controller.get("Professional") is not None else False
        if "Professional" not in st.session_state  or not st.session_state.Professional:
            st.session_state.Professional = stored_professional
    except:
        st.session_state.Professional =False

    st.markdown("""
    <style>
        [data-testid="stSidebarContent"] [data-testid="stButton"] button{
                margin-left:0;
                margin-right:auto
                }
                
        [data-testid="stSidebarContent"] [data-testid="stForm"] button {
                justify-content:left;
                margin-left: 1rem;
                border-style:none;
                } 
        
        [data-testid="stSidebarContent"] [data-testid="stForm"] [data-testid="stVerticalBlock"]{ 
                gap:0rem;
                }
    </style>
    """, unsafe_allow_html=True) 
    name_pattern = regex.compile(r"^[\p{L}' -]*$", regex.UNICODE)
    rnumber_pattern= regex.compile(r"^[a-z]\d{7}$", regex.UNICODE)

    st.sidebar.image("omfs_logo.png")           
    if st.session_state.Professional:
        with st.sidebar.form("menu", border=False):
            st.title("Menu")
            Upload = st.form_submit_button("Upload",use_container_width=True,type="tertiary", disabled=(page=="Upload") )
            Manual = st.form_submit_button("Manual input",use_container_width=True,type="tertiary", disabled=(page=="Manual"))
            AI = st.form_submit_button("AI result",use_container_width=True,type="tertiary", disabled=(page=="AI"))
            Compair = st.form_submit_button("Compare",use_container_width=True,type="tertiary", disabled=(page=="Comparison"))

        if Upload:
            st.switch_page("pages/Upload_img.py")
        elif Manual:
            st.switch_page("pages/Manual.py")
        elif AI:
            st.switch_page("pages/AI.py")
        elif Compair:
            st.switch_page("pages/Comparison.py")
    else:
        stored_student_name = controller.get("studentName") or ""
        if "studentName" not in st.session_state or not st.session_state.studentName:
            st.session_state.studentName = stored_student_name

        student_name = st.sidebar.text_input("Your name", value=st.session_state.studentName, key="studentName")

        if name_pattern.fullmatch(student_name):
            if student_name != stored_student_name:
                controller.set("studentName", student_name)
        elif student_name:
            st.sidebar.error("Your name can only contain letters, apostrophes ('), and hyphens (-).")
        
        stored_rnumber = controller.get("rnumber") or ""
        if "rnumber" not in st.session_state or not st.session_state.rnumber:
            st.session_state.rnumber = stored_rnumber

        rnumber = st.sidebar.text_input("Your r-nummer", value=st.session_state.rnumber, key="rnumber")

        if rnumber_pattern.fullmatch(rnumber):
            if rnumber != stored_rnumber:
                controller.set("rnumber", rnumber)
        elif rnumber:
            st.sidebar.error("Your r-number needs to look like r0123456")



    st.sidebar.title("Dental Chart")
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

        stored_Teethkind = controller.get("Teethkind")
        if not stored_Teethkind:
            if years>18:
                controller.set("Teethkind", "Adult")
                st.session_state.Teethkind = "Adult"
            if years>6 and years<=18:
                controller.set("Teethkind", "Mixed")
                st.session_state.Teethkind = "Mixed"
            else:
                controller.set("Teethkind", "Child")
                st.session_state.Teethkind = "Child"
        
    # --- teeth ---
    stored_Teethkind = controller.get("Teethkind")
    if "Teethkind" not in st.session_state or not st.session_state.Teethkind:
        st.session_state.Teethkind = stored_Teethkind

    if "Teethkindpicker" not in st.session_state or not st.session_state.Teethkindpicker:
        st.session_state.Teethkindpicker = stored_Teethkind

    Teethkindpicker = st.sidebar.radio("Teeth", ["Adult","Mixed", "Child"],
                              index=0 if st.session_state.Teethkindpicker == "Adult" else 1,
                              key="Teethkindpicker")
                              
    if "teethkindManualySet" in st.session_state:
        print(st.session_state.teethkindManualySet)

    if Teethkindpicker != stored_Teethkind:
        st.session_state.Teethkind=Teethkindpicker
        controller.set("Teethkind", Teethkindpicker)

    if st.session_state.Professional:
        st.sidebar.button("Log out",on_click=logout)
    else:
        st.sidebar.button("Log in as professional",on_click=logout)
    
    if st.session_state.get("just_logedin"):
        st.session_state.just_logedin = False
        st.session_state.go_to_login = True