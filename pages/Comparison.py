import streamlit as st
from streamlit_cookies_controller import CookieController

from components.excel import excel_button
from components.pdf import pdf_button
from components.zipDownload import combined_download_button
from components.sidebar import load_sidebar
from components.teeth import load_teeth
from input.teethSet import teeth as manualteeth, childteeth as manualchildteeth
from AIOutput.teethSet import teeth as AIteeth, childteeth as AIchildteeth
from components.teeth import load_teeth, pil_to_data_url
from components.teeth_renderer import check_checkbox_disabled, check_checkbox_status, toggle_tooth_presence, \
    show_options, render_button_row
from input.teethSet import teeth as manualteeth
from AIOutput.teethSet import teeth as AIteeth
import os
from components.teeth import get_tooth_image
from components.pdf_profesionnal import pdf_button_professional

st.set_page_config(page_title="comparison", layout="wide")

st.markdown("""
    <style>
    .st-key-something_different {
        background-color: white;
        color: black;
        border-radius: 0.5rem;
    }
    .st-key-radio_modal_difference *{
        gap: 6rem;
    }
    </style>
    """, unsafe_allow_html=True)

def restart():
    controller = CookieController()
    print(controller.getAll())

    keys_to_clear = [
        "ProfileNumber", "LastName", "FirstName", "birthdate", "consultation date", "Gender","Teethkind"
    ]

    # Clear all session_state keys
    for key in list(st.session_state.keys()):
        del st.session_state[key]

    # Remove cookies
    for key in keys_to_clear:
        if key in controller.getAll():
            controller.remove(key)
        else:
            print(key + " not found")

    print(controller.getAll())
    st.cache_data.clear()

    # Set flag to trigger page switch on next rerun
    st.session_state.just_restarted = True

if "go_to_next_page" not in st.session_state:
   st.session_state.go_to_next_page = False

# Perform the page switch "outside" the callback
if st.session_state.go_to_next_page:
    st.session_state.go_to_next_page = False
    st.switch_page("pages/Upload_img.py")

if "go_to_upload_page" not in st.session_state:
    st.session_state.go_to_upload_page = False

if st.session_state.go_to_upload_page:
    st.session_state.go_to_upload_page = False
    st.switch_page("pages/Upload_img.py")


# Define a session flag to trigger the page switch


try:
    manual_teeth =st.session_state.manual_teeth
except:
    manual_teeth=manualteeth
    print("no manual teeth found")

try:
    AI_teeth =st.session_state.ai_teeth
except:
    AI_teeth=AIteeth

    print("no ai teeth found")

if st.session_state.get("customize_tooth", False):
    teeth = st.session_state.get("teeth_dict_manual")
    show_options(teeth)

def normalize(value):
    if value is None:
        return None
    return set(map(str.strip, value.split(",")))

def compair(manualteeth, AIteeth) -> dict[int, str | None]:
    differences = {}
    for tooth in AIteeth:
        user_val = manualteeth[tooth]
        ai_val = AIteeth[tooth]

        norm_user = normalize(user_val)
        norm_ai = normalize(ai_val)

        if norm_user != norm_ai:
            if not (norm_user==None and norm_ai=="normal") or not (norm_user=="normal" and norm_ai==None):
                differences[tooth]=ai_val
    return(differences)

load_sidebar("Comparison")

if st.session_state.Teethkind == "Child":
    child=True
else:
    child=False

if child:
    try:
        manual_teeth =st.session_state.manual_teeth_child
    except:
        manual_teeth=manualchildteeth
        print("no manual teeth found")

    try:
        AI_teeth =st.session_state.ai_teeth_child
    except:
        AI_teeth=AIchildteeth
    print("no ai teeth found")
else:
    try:
        manual_teeth =st.session_state.manual_teeth
    except:
        manual_teeth=manualteeth
        print("no manual teeth found")

    try:
        AI_teeth =st.session_state.ai_teeth
    except:
        AI_teeth=AIteeth
        print("no ai teeth found")

st.title("Comparison page!")

ai_image_bytes = st.session_state.get("AI_image_bytes")
manual_image_bytes = st.session_state.get("manual_image_bytes")


TARGET_IMAGE_HEIGHT = 90


# Simplified pick_correct_tooth - it no longer needs to manage complex last_click states
@st.dialog(title=" ")
def pick_correct_tooth(clicked_tooth_id):
    if "corrected_teeth" not in st.session_state:  # Use .get for safer access if not always present
        st.session_state.corrected_teeth = set()

    st.title(f"Tooth {clicked_tooth_id}")
    tooth_differences_value = differences.get(clicked_tooth_id, False)

    columns = st.columns(2)
    with columns[0]:
        radio_value = st.radio(" ", ("manual", "ai"), key=f"radio_modal_difference")

    with columns[1]:
        modal_tooth_pil_manual = get_tooth_image(clicked_tooth_id, manual_teeth[clicked_tooth_id])
        st.image(modal_tooth_pil_manual, width=40)

        if tooth_differences_value is not False:
            modal_tooth_pil_ai = get_tooth_image(clicked_tooth_id, tooth_differences_value)
            st.image(modal_tooth_pil_ai, width=40)
        else:
            st.write("AI data not available for this tooth.")  # Or handle appropriately

    modal_cols = st.columns(2)
    with modal_cols[0]:
        if st.button("Something different", key=f"something_different_modal_{clicked_tooth_id}",
                     use_container_width=True):
            st.session_state.selected_tooth = clicked_tooth_id
            st.session_state.show_tooth_config_dialog = True
            st.rerun()

    with modal_cols[1]:
        if st.button("Save", key=f"save_modal_{clicked_tooth_id}", use_container_width=True, type="primary"):
            if radio_value == "ai":
                manual_teeth[clicked_tooth_id] = AI_teeth[clicked_tooth_id]

            if clicked_tooth_id in differences:
                del differences[clicked_tooth_id]

            if "corrected_teeth" in st.session_state:  # Check if it exists
                st.session_state.corrected_teeth.add(clicked_tooth_id)

            st.session_state.modal_tooth_num = None
            st.rerun()

TOP_ROW_ADULT    = list(reversed(range(11, 19))) + list(range(21, 29))
BOTTOM_ROW_ADULT = list(reversed(range(41, 49))) + list(range(31, 39))

TOP_ROW_CHILD = list(reversed(range(51, 56))) + list(range(61, 66))
BOTTOM_ROW_CHILD= list(reversed(range(81, 86))) + list(range(71, 76))

if st.session_state.get("modal_tooth_num", False):
    if child and (st.session_state.modal_tooth_num not in TOP_ROW_CHILD and st.session_state.modal_tooth_num not in BOTTOM_ROW_CHILD):
        st.session_state.show_tooth_config_dialog = False
        st.session_state.modal_tooth_num = None
    elif not child and (st.session_state.modal_tooth_num not in TOP_ROW_ADULT and st.session_state.modal_tooth_num not in BOTTOM_ROW_ADULT):
        st.session_state.show_tooth_config_dialog = False
        st.session_state.modal_tooth_num = None

def load_diff_teeth_top(differences, teeth_list):
    cols = st.columns(len(teeth_list))
    for col, tooth in zip(cols, teeth_list):
        with col:
            if tooth in differences:
                st.image(get_tooth_image(tooth, differences[tooth]))
            else:
                st.empty()

def load_diff_teeth_bottom(differences, teeth_list):
    cols = st.columns(len(teeth_list))
    for col, tooth in zip(cols, teeth_list):
        with col:
            if tooth in differences:
                st.image(get_tooth_image(tooth, differences[tooth]))
            else:
                st.empty()

# Check if the image exists
if ai_image_bytes and manual_image_bytes:
    st.markdown("""
    <style>
    .st-key-photo-container {
        margin: 0 auto;
    }
    </style>
    """, unsafe_allow_html=True)
    with st.container(key="photo-container"):
        cols = st.columns(2)
        with cols[0]:
            st.image(manual_image_bytes, use_container_width=True)
        with cols[1]:
            st.image(ai_image_bytes, use_container_width=True)
    raw_differences = compair(manual_teeth, AI_teeth)
    corrected_teeth = st.session_state.get("corrected_teeth", set())
    differences = {}
    for key, value in raw_differences.items():
        if key not in corrected_teeth:
            differences[key] = value

    st.markdown("""
    <style>
    .st-key-container {
        max-width: 900px;
        margin: 0 auto;
    }
    .st-key-container div[data-testid="stElementToolbarButtonContainer"] {
            display: none;
    }
    </style>
    """, unsafe_allow_html=True)
    with st.container(key="container"):
        st.markdown("### Differences top teeth")
        if child:
            top_row = TOP_ROW_CHILD
            cols = st.columns(10)
        else:
            top_row = TOP_ROW_ADULT
            cols = st.columns(16)
        load_diff_teeth_top(differences, top_row)
        if st.session_state.get("Professional", False):
            render_button_row(cols, top_row, manual_teeth, disable_buttons=False, differences=differences, color_differences_instead_of_manual=True)

        st.markdown("### Your input")
        load_teeth(manual_teeth, outline_corrected_images=True, child=child)

        st.markdown("### Differences bottom teeth")
        if child:
            bottom_row = BOTTOM_ROW_CHILD
            cols = st.columns(10)
        else:
            bottom_row = BOTTOM_ROW_ADULT
            cols = st.columns(16)
        load_diff_teeth_top(differences, bottom_row)
        if st.session_state.get("Professional", False):
            render_button_row(cols, bottom_row, manual_teeth, disable_buttons=False, differences=differences, color_differences_instead_of_manual=True)

        if (
                st.session_state.get("modal_tooth_num") is not None
                and not st.session_state.get("show_tooth_config_dialog", True)
        ):
            selected_tooth = st.session_state.modal_tooth_num
            st.session_state.selected_tooth = selected_tooth
            if st.session_state.get("modal_tooth_show_diff_modal", False):
                pick_correct_tooth(selected_tooth)
            else:
                show_options(manual_teeth, False)

else:
    st.warning("No image has been uploaded yet.")

def go_to_upload_page():
    st.session_state.go_to_upload_page = True

if "manual_image_bytes" in st.session_state:
    st.markdown("""
        <style>
        .st-key-next-container {
            max-width: 900px;
            margin: 0 auto;
        }
        [data-testid="stButton"] button {
            display: flex;
            justify-content: center;
            margin-right: 0;
            margin-left: auto;
            width: fit-content; 
        }
        </style>
    """, unsafe_allow_html=True)

    with st.container(key="next-container"):
        st.markdown("""
        <style>
        .st-key-pdf-container {
            max-width: fit-content; 
            margin-right: 0;
            margin-left: auto;
            display: flex;
        }
        </style>
        """, unsafe_allow_html=True)
        with st.container(key="pdf-container"):
            if st.session_state.Professional:
                combined_download_button()
            else:
                pdf_button()
                # excel_button()


        st.button("Restart", on_click=restart)
else:
    st.button("Upload image", on_click=go_to_upload_page)

if st.session_state.get("just_restarted"):
    st.session_state.just_restarted = False
    st.session_state.go_to_next_page = True
if "AI_image_bytes" not in st.session_state and not st.session_state.get("just_restarted"):
    st.session_state.go_to_AI_page = True

# Trigger the actual page switch
# if st.session_state.get("go_to_AI_page"):
#     st.session_state.go_to_AI_page = False
#     st.switch_page("pages/AI.py")

if st.session_state.get("show_tooth_config_dialog", False):
    st.session_state.show_tooth_config_dialog = False
    st.session_state.modal_tooth_num = None
    show_options(manual_teeth, True)

