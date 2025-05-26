import base64
from io import BytesIO
from pathlib import Path
from st_click_detector import click_detector
import streamlit as st
from PIL import Image
from PIL.ImageFile import ImageFile
from st_clickable_images import clickable_images
from streamlit_cookies_controller import CookieController

from components.excel import excel_button
from components.pdf import pdf_button
from components.sidebar import load_sidebar
from components.teeth import load_teeth, pil_to_data_url
from components.teeth_renderer import check_checkbox_disabled, check_checkbox_status, toggle_tooth_presence, \
    show_options
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
    [role=radiogroup]{
        gap: 6rem;
    }
    </style>
    """, unsafe_allow_html=True)

def restart():
    controller = CookieController()
    print(controller.getAll())

    keys_to_clear = [
        "ProfileNumber", "LastName", "FirstName", "birthdate", "consultation date", "Gender"
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

st.title("Comparison page!")

ai_image_bytes = st.session_state.get("AI_image_bytes")
manual_image_bytes = st.session_state.get("manual_image_bytes")


TARGET_IMAGE_HEIGHT = 120


# Simplified pick_correct_tooth - it no longer needs to manage complex last_click states
@st.dialog(title=" ")
def pick_correct_tooth(clicked_tooth_id):
    if "corrected_teeth" not in st.session_state:  # Use .get for safer access if not always present
        st.session_state.corrected_teeth = set()

    st.title(f"Tooth {clicked_tooth_id}")
    tooth_differences_value = differences.get(clicked_tooth_id, False)

    columns = st.columns(2)
    with columns[0]:
        radio_value = st.radio(" ", ("manual", "ai"), key=f"radio_modal_{clicked_tooth_id}")

    with columns[1]:
        modal_tooth_pil_manual = get_tooth_image(clicked_tooth_id, manual_teeth[clicked_tooth_id])
        st.image(modal_tooth_pil_manual, width=40)

        if tooth_differences_value is not False:
            modal_tooth_pil_ai = get_tooth_image(clicked_tooth_id, tooth_differences_value)
            st.image(modal_tooth_pil_ai, width=40)
        else:
            st.write("AI data not available for this tooth.")  # Or handle appropriately

    if st.button("Something different", key=f"something_different_modal_{clicked_tooth_id}", use_container_width=True):
        st.session_state.selected_tooth = clicked_tooth_id
        st.session_state.show_tooth_config_dialog = True
        st.rerun()  # Rerun to handle the new dialog state

    modal_cols = st.columns(2)
    with modal_cols[0]:
        if st.button("Return", key=f"close_modal_{clicked_tooth_id}", use_container_width=True):
            st.session_state.modal_tooth_num = None
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
        st.markdown("Differences Top Teeth")
        top_row = list(reversed(range(11, 19))) + list(range(21, 29))
        cols = st.columns(16)
        for i, tooth_num in enumerate(top_row):
            if tooth_num in differences:
                with cols[i]:
                    st.image(get_tooth_image(tooth_num, differences[tooth_num]))

        st.markdown("Your input")

        load_teeth(manual_teeth, outline_corrected_images=True)

        st.markdown("Differences bottom Teeth")
        bottom_row_ordered_tooth_ids = list(reversed(range(41, 49))) + list(range(31, 39))

        # We still need to know which differences apply to the bottom row
        actual_differences_in_bottom_row = {
            tn: diff_value
            for tn, diff_value in differences.items()
            if tn in bottom_row_ordered_tooth_ids
        }

        # Check if there are any differences to display at all for the bottom row
        no_differences_to_show = not any(tooth_id in differences for tooth_id in bottom_row_ordered_tooth_ids)

        if no_differences_to_show:
            st.write("No tooth differences to display for the bottom row.")
        else:
            cols = st.columns(len(bottom_row_ordered_tooth_ids))
            clicked_image_id = None  # Variable to store the ID from click_detector

            for i, tooth_id_in_sequence in enumerate(bottom_row_ordered_tooth_ids):
                with cols[i]:
                    if tooth_id_in_sequence in actual_differences_in_bottom_row:
                        diff_value = actual_differences_in_bottom_row[tooth_id_in_sequence]
                        tooth_pil = get_tooth_image(tooth_id_in_sequence, diff_value)
                        image_data_url = pil_to_data_url(tooth_pil)

                        # The <a> tag needs the id attribute for click_detector to return it
                        anchor_html_id = f"diff_tooth_{tooth_id_in_sequence}"
                        html_content = f"""
                            <div style="display: flex; justify-content: center; align-items: center; height: 100%; cursor: pointer;">
                                <a href='#' id="{anchor_html_id}" >
                                <img src="{image_data_url}" 
                                     alt="Tooth {tooth_id_in_sequence} difference" 
                                     style="max-width: 100%; max-height: {TARGET_IMAGE_HEIGHT}px; object-fit: contain;">
                                </a>
                            </div>
                        """
                        detected_click = click_detector(html_content, key=f"detector_{tooth_id_in_sequence}")

                        if detected_click:
                            if detected_click == anchor_html_id:
                                clicked_image_id = detected_click
                    else:
                        st.markdown(
                            f"""<div style='height: {TARGET_IMAGE_HEIGHT}px;
                                        display: flex; align-items: center;
                                        justify-content: center; width: 100%;'>
                                 </div>""",
                            unsafe_allow_html=True
                        )

            # Process the click AFTER iterating through all detectors in the current script run
            if clicked_image_id:
                # Extract the tooth_id from the clicked_image_id (e.g., "diff_tooth_31" -> 31)
                try:
                    # Make sure the prefix matches what you used for image_html_id
                    actual_tooth_id_str = clicked_image_id.replace("diff_tooth_", "")
                    actual_tooth_id = int(actual_tooth_id_str)
                    st.session_state.modal_tooth_num = actual_tooth_id
                except ValueError:
                    st.error(f"Could not parse tooth ID from clicked element ID: {clicked_image_id}")

        # This part remains the same for showing the modal
        if st.session_state.get('modal_tooth_num', None):
            selected_tooth = st.session_state.modal_tooth_num
            pick_correct_tooth(selected_tooth)

else:
    st.warning("No image has been uploaded yet.")


if "manual_image_bytes" in st.session_state:
    st.markdown("""
        <style>
        .st-key-pdf-container {
            max-width: 900px;
            margin: 0 auto;
        }
        </style>
        """, unsafe_allow_html=True)
    with st.container(key="pdf-container"):
        col1, col2 = st.columns([16, 5])

        with col2:
            if st.session_state.Professional:
                pdf_button_professional()
                excel_button()

            else:
                pdf_button()
                excel_button()

#switch page
# Define the callback


def go_to_upload_page():
    st.session_state.go_to_upload_page = True

if "manual_image_bytes" in st.session_state:
    st.markdown("""
        <style>
        .st-key-next-container {
            max-width: 900px;
            margin: 0 auto;
        }
        </style>
        """, unsafe_allow_html=True)
    with st.container(key="next-container"):
        col1, col2 = st.columns([8, 1])

        with col2:
        # Show the button
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