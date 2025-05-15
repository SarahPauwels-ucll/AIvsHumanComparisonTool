import streamlit as st
from st_pages import Page, add_page_title
from sidebar import load_sidebar
from teeth import load_teeth
import os

st.set_page_config(page_title="AI vs. Human analysis: A smart comparison tool",
                   layout="wide")

load_sidebar()

st.title("Welcome to the manual page!")
st.write("Here we can manualy alter the chart.")


image_path = os.path.join("image", "image.jpeg")
has_image_been_uploaded = False
# Check if the image exists
if os.path.exists(image_path):
    st.image(image_path, caption="Uploaded Dental Image",  use_container_width=True)
    has_image_been_uploaded = True
else:
    st.warning("No image has been uploaded yet.")

@st.cache_data()
def get_teeth_data() -> dict[int, str | None]:
    teeth_dict = {
        11: None, 12: None, 13: None, 14: None, 15: None, 16: None, 17: None, 18: None,
        21: None, 22: None, 23: None, 24: None, 25: None, 26: None, 27: None, 28: None,
        31: None, 32: None, 33: None, 34: None, 35: None, 36: None, 37: None, 38: None,
        41: None, 42: None, 43: None, 44: None, 45: None, 46: None, 47: None, 48: None
    }
    return teeth_dict

if has_image_been_uploaded:
    if st.session_state.get("teeth_dict"):
        teeth = st.session_state.teeth_dict
    else:
        teeth = get_teeth_data()
        st.session_state.teeth_dict = teeth
    if "show_tooth_config_dialog" not in st.session_state:
        st.session_state.show_tooth_config_dialog = False

    def toggle_tooth_presence(presence: str, tooth_number: int):
        if teeth[tooth_number] == presence or teeth[tooth_number] is None:
            if presence == "missing":
                if "missing" in str(teeth[tooth_number]):
                    teeth[tooth_number] = None
                else:
                    teeth[tooth_number] = "missing"
            if presence == "normal":
                if "normal" in str(teeth[tooth_number]):
                    teeth[tooth_number] = None
                else:
                    teeth[tooth_number] = "normal"

        elif presence in str(teeth[tooth_number]):
            if presence == "missing" or presence == "normal":
                teeth[tooth_number] = None

            else:
                teeth[tooth_number] = str(teeth[tooth_number]).replace(f",{presence}", "")
        else:
            teeth[tooth_number] = str(teeth[tooth_number]) + f",{presence}"

    @st.dialog( " ", width="large")
    def show_options():
        tooth_number = st.session_state.selected_tooth
        missing_properties = ["Implant", "Implant bridge", "Implant crown", "Bridge"]
        present_properties = ["Dental filling", "Root canal filling", "Crown", "Bridge", "Impacted"]
        # order: missing/present, implant, bridge/crown, dental filling, root canal filling
        # crown(+root canal fill), bridge(+root canal fill), dental fill, dental fill+root canal fill, impacted

        st.title(f"Tooth {tooth_number}")
        col1, col2 = st.columns(2)

        with col1:
            if "missing" in str(teeth[tooth_number]):
                present_checkbox = st.checkbox("Present", key=f"present_{tooth_number}", disabled=True)
            else:
                present_checkbox = st.checkbox("Present", key=f"present_{tooth_number}", on_change=toggle_tooth_presence, args=("normal", tooth_number))

        with col2:
            if "normal" in str(teeth[tooth_number]):
                missing_checkbox = st.checkbox("Missing", key=f"missing_{tooth_number}", disabled=True)
            else:
                missing_checkbox = st.checkbox("Missing", key=f"missing_{tooth_number}", on_change=toggle_tooth_presence, args=("missing", tooth_number))

        with col1:
            if present_checkbox:
                dental_filling_checkbox = st.checkbox("Dental filling")
                root_canal_filling_checkbox = st.checkbox("Root canal filling")
                crown_checkbox = st.checkbox("Crown")
                bridge_checkbox = st.checkbox("Bridge")
                impacted_checkbox = st.checkbox("Impacted")

            if missing_checkbox:
                if "crown" in str(teeth[tooth_number]):
                    implant_checkbox = st.checkbox("Implant", disabled=True)
                else:
                    implant_checkbox = st.checkbox("Implant", on_change=toggle_tooth_presence, args=("implant",tooth_number))
                if implant_checkbox and not "bridge" in str(teeth[tooth_number]):
                    crown_checkbox = st.checkbox("Crown", on_change=toggle_tooth_presence, args=("crown",tooth_number))
                else:
                    crown_checkbox = st.checkbox("Crown", disabled=True)
                if not "crown" in str(teeth[tooth_number]):
                    bridge_checkbox = st.checkbox("Bridge", on_change=toggle_tooth_presence, args=("bridge",tooth_number))
                else:
                    crown_checkbox = st.checkbox("Bridge", disabled=True)
                    #bridge_checkbox = st.checkbox("Bridge", on_change=toggle_tooth_presence, args=("bridge",tooth_number))


        col1, col2 = st.columns(2)
        with col1:
            if st.button("Clear all"):
                teeth[tooth_number] = None
                st.session_state.show_tooth_config_dialog = False
                st.rerun()

        with col2:
            if st.button("Submit"):
                    missing_or_present = None
                    if missing_checkbox:
                        missing_or_present = "Missing"
                    if present_checkbox:
                        missing_or_present = "Present"
                    st.session_state.show_tooth_config_dialog = False
                    st.rerun()
        print(teeth)

    top_left_nums = [18,17,16,15,14,13,12,11]
    top_right_nums = [21,22,23,24,25,26,27,28]
    bottom_left_nums = [48,47,46,45,44,43,42,41]
    bottom_right_nums = [31,32,33,34,35,36,37,38]

    teeth_base_folder = os.path.join("image", "teeth")

    def show_tooth_modal(tooth_number):
        st.session_state.selected_tooth = tooth_number
        st.session_state.show_tooth_config_dialog = True

    top_cols = st.columns(len(top_left_nums + top_right_nums))
    top_nums = top_left_nums + top_right_nums
    for column, n in zip(top_cols, top_nums):
        with column:
            button_key = f"btn_{n}_b"
            custom_css = f"""
            <style>
                .st-key-{button_key} button {{
                    white-space: nowrap !important;
                }}
            </style>
            """
            st.markdown(custom_css, unsafe_allow_html=True)
            if st.button(str(n), key=button_key):
                show_tooth_modal(n)

    load_teeth(teeth)

    bottom_cols = st.columns(len(bottom_left_nums + bottom_right_nums))
    bottom_nums = bottom_left_nums + bottom_right_nums
    for column, n in zip(bottom_cols, bottom_nums):
        with column:
            button_key = f"btn_{n}_b"
            custom_css = f"""
            <style>
                .st-key-{button_key} button {{
                    white-space: nowrap !important;
                }}
            </style>
            """
            st.markdown(custom_css, unsafe_allow_html=True)
            if st.button(str(n), key=button_key):
                show_tooth_modal(n)

    if st.session_state.show_tooth_config_dialog:
        show_options()