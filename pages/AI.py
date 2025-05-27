import streamlit as st
from components.excel import excel_button
from components.teeth_renderer import render_teeth
from input.teethSet import teeth as manualteeth

from components.sidebar import load_sidebar
import os

st.session_state.submitted_manual_teeth = True
# Define a session flag to trigger the page switch
if "go_to_next_page" not in st.session_state:
    st.session_state.go_to_next_page = False

# Perform the page switch "outside" the callback
if st.session_state.go_to_next_page:
    st.session_state.go_to_next_page = False
    st.switch_page("pages/Comparison.py")

if "go_to_upload_page" not in st.session_state:
    st.session_state.go_to_upload_page = False

if st.session_state.go_to_upload_page:
    st.session_state.go_to_upload_page = False
    st.switch_page("pages/Upload_img.py")

st.set_page_config(page_title="AI vs. Human analysis: A smart comparison tool",
                   layout="wide")

try:
    manual_teeth =st.session_state.manual_teeth
except:
    st.session_state.manual_teeth=manualteeth
    print("no manual teeth found")

load_sidebar("AI")

st.title("Welcome to the AI page!")

image_path = os.path.join("AIOutput", "image.jpg")
# Check if the image exists
if os.path.exists(image_path) and "manual_image_bytes" in st.session_state:
    st.markdown("""
    <style>
    .st-key-photo-container {
        max-width: 900px;
        margin: 0 auto;
    }
    </style>
    """, unsafe_allow_html=True)
    with st.container(key="photo-container"):
        st.image(image_path,  use_container_width=True)
    circleView=st.session_state.circleView if "circleView" in st.session_state and st.session_state.circleView is not None else False
    if st.session_state.Teethkind == "Child":
        child=True
    else:
        child=False
    ai_teeth = render_teeth("ai",circle=circleView,child=child)
    if child:
         st.session_state.ai_teeth_child = ai_teeth
    else:
        st.session_state.ai_teeth = ai_teeth

    with open(image_path, "rb") as img_file:
        st.session_state.AI_image_bytes = img_file.read()

else:
    st.warning("No image has been uploaded yet.")

#switch page
# Define the callback
def go_to_next():
    st.session_state.go_to_next_page = True

def go_to_upload_page():
    st.session_state.go_to_upload_page = True

def switch_view():
    if "circleView" not in  st.session_state or st.session_state.circleView is None or st.session_state.circleView==False:
        st.session_state.circleView = True  
    else: 
        st.session_state.circleView=False

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
        with col1:
            if st.session_state.Professional:
                st.button("switch view", on_click=switch_view)
        with col2:
        # Show the button
            st.button("Next Page", on_click=go_to_next)

else:
    st.button("Upload image", on_click=go_to_upload_page)