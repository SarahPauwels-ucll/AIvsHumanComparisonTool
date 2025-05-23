import base64
from io import BytesIO
from pathlib import Path

import streamlit as st
from PIL.ImageFile import ImageFile
from st_clickable_images import clickable_images
from streamlit_cookies_controller import CookieController

from components.excel import excel_button
from components.pdf import pdf_button
from components.sidebar import load_sidebar
from components.teeth import load_teeth
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

def normalize(value):
    if value is None:
        return None
    return set(map(str.strip, value.split(",")))

def compair(manualteeth, AIteeth):
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

def pil_image_to_base64(pil_image):
    buffered = BytesIO()
    pil_image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return img_str

def img_to_html(pil_image):
    encoded_img = pil_image_to_base64(pil_image)
    mime_type = f"image/png"
    img_html = f"<img src='data:{mime_type};base64,{encoded_img}' class='img-fluid' alt='Tooth Image'>"
    return img_html

def pil_to_data_url(pil_image):
    buffered = BytesIO()
    pil_image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"

def _select_manual(tooth):
    st.session_state[f"correction_choice_{tooth}"] = "manual"

def _select_ai(tooth):
    st.session_state[f"correction_choice_{tooth}"] = "ai"


@st.dialog(title=" ")
def pick_correct_tooth(clicked_tooth):
    if not st.session_state.get("corrected_teeth", None):
        st.session_state.corrected_teeth = set()

    st.title(f"Tooth {clicked_tooth}")
    tooth_differences = differences.get(clicked_tooth, False)
    # st.write(f"This tooth has tooth_differences: **{tooth_differences}**")

    choice = st.session_state.get(f"correction_choice_{clicked_tooth}", None)

    columns = st.columns(2)
    with columns[0]:
        st.radio(" ", ("manual", "ai"))

    with columns[1]:
        modal_tooth_pil_manual = get_tooth_image(clicked_tooth, manual_teeth[clicked_tooth])
        st.image(modal_tooth_pil_manual, width=40)

        modal_tooth_pil_ai = get_tooth_image(clicked_tooth, tooth_differences)
        st.image(modal_tooth_pil_ai, width=40)

    # Add more details or interactive elements for the modal here

    if st.button("Something different", key=f"something_different", use_container_width=True, type="tertiary"):
        st.session_state.selected_tooth = clicked_tooth
        st.session_state.show_tooth_config_dialog = True

    columns = st.columns(2)
    with columns[0]:
        if st.button("Return", key=f"close_modal_{clicked_tooth}", use_container_width=True):
            # Reset processed click
            st.session_state.modal_tooth_num = None
            st.session_state.last_clicked_bottom_idx_processed = -1
            st.rerun()

    with columns[1]:
        if st.button("Save", key=f"save_modal_{clicked_tooth}", use_container_width=True, type="primary"):
            # TODO: change manual teeth to new tooth
            st.session_state.manual_teeth[clicked_tooth] = tooth_differences # check
            st.session_state.modal_tooth_num = None
            st.session_state.last_clicked_bottom_idx_processed = -1
            st.rerun()

# Check if the image exists
if ai_image_bytes and manual_image_bytes :
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
            st.image(manual_image_bytes,  use_container_width=True)
        with cols[1]:
            st.image(ai_image_bytes,  use_container_width=True)
    differences = compair(manual_teeth, AI_teeth)

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

        load_teeth(manual_teeth)

        st.markdown("Differences bottom Teeth")
        bottom_row = list(reversed(range(41, 49))) + list(range(31, 39))

        bottom_teeth_images_data_urls = []
        bottom_teeth_titles = []
        bottom_teeth_display_order = []

        for tooth_num in bottom_row:
            if tooth_num in differences.keys():
                tooth_pil = get_tooth_image(tooth_num, differences[tooth_num])
                data_url = pil_to_data_url(tooth_pil)
                bottom_teeth_images_data_urls.append(data_url)
                bottom_teeth_titles.append(f"Tooth {tooth_num}\n (Difference(s): {differences[tooth_num]})")
                bottom_teeth_display_order.append(tooth_num)

        if not bottom_teeth_images_data_urls:
            st.write("No tooth data to display for the bottom row.")
        else:
            # Use st_clickable_images
            # The component returns the index of the clicked image, or -1
            clicked_bottom_idx = clickable_images(
                paths=bottom_teeth_images_data_urls,
                titles=bottom_teeth_titles,
                div_style={"display": "flex", "justify-content": "center", "flex-wrap": "wrap", "gap": "5px"},
                img_style={"margin": "2px", "cursor": "pointer"},
                key="bottom_teeth_gallery"
            )

            if clicked_bottom_idx != -1 and clicked_bottom_idx != st.session_state.get('last_clicked_bottom_idx_processed', -1):
                selected_tooth_num = bottom_teeth_display_order[clicked_bottom_idx]
                st.session_state.modal_tooth_num = selected_tooth_num
                st.session_state.last_clicked_bottom_idx_processed = clicked_bottom_idx
                st.rerun()

            # If nothing is clicked after a previous click, clickable_images might return -1.
            # If you want the modal to disappear if the user clicks "away" (not on an image),
            # you might need more complex state management, or rely on a "Close" button in the modal.
            # The current setup keeps the modal open until explicitly closed or another image is clicked.

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