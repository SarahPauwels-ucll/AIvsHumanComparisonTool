import streamlit as st
from streamlit_cookies_controller import CookieController
from components.pdf import pdf_button
from components.sidebar import load_sidebar
from components.teeth import load_teeth
from input.teethSet import teeth as manualteeth
from AIOutput.teethSet import teeth as AIteeth
import os
from components.teeth import get_tooth_image
from components.pdf_profesionnal import pdf_button_professional

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

st.set_page_config(page_title="comparison", layout="wide")

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

def restart():
    controller = CookieController()
    print(controller.getAll())
    keys_to_clear = [
        "ProfileNumber",
        "LastName",
        "FirstName",
        "birthdate",
        "consultation date",
        "Gender"
    ]
    for key in st.session_state.keys():
        del st.session_state[key]
    for key in keys_to_clear:  
        if key in controller.getAll():
            controller.remove(key)
        else: print(key+ " not found")
    print(controller.getAll())
    st.cache_data.clear()
    st.session_state.go_to_next_page = True

load_sidebar("Comparison")

st.title("Comparison page!")
ai_image_bytes = st.session_state.get("AI_image_bytes")
manual_image_bytes = st.session_state.get("manual_image_bytes")
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
        cols2 = st.columns(16)
        for i, tooth_num in enumerate(bottom_row):
            if tooth_num in differences:
                with cols2[i]:
                    st.image(get_tooth_image(tooth_num, differences[tooth_num]))
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
            else:
                pdf_button()

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

