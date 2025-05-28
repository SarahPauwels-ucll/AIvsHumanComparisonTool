import streamlit as st
from st_pages import Page, add_page_title
import AIOutput.teethSet
from components.pdf_profesionnal import pdf_button_professional
from components.teeth_renderer import render_teeth
from components.sidebar import load_sidebar
from components.teeth import load_teeth
import os

#switch page
# Define a session flag to trigger the page switch
if "go_to_next_page" not in st.session_state:
    st.session_state.go_to_next_page = False

# Perform the page switch "outside" the callback
if st.session_state.go_to_next_page:
    st.session_state.go_to_next_page = False
    st.switch_page("pages/AI.py")

if "go_to_upload_page" not in st.session_state:
    st.session_state.go_to_upload_page = False

if st.session_state.go_to_upload_page:
    st.session_state.go_to_upload_page = False
    st.switch_page("pages/Upload_img.py")

st.set_page_config(page_title="AI vs. Human analysis: A smart comparison tool",
                   layout="wide")



load_sidebar("Manual")

st.title("Welcome to the manual page!")

image_path = os.path.join("image", "image.jpeg")

if "manual_image_bytes" in st.session_state:
    st.markdown("""
    <style>
    .st-key-photo-container {
        max-width: 900px;
        margin: 0 auto;
    }
    </style>
    """, unsafe_allow_html=True)
    with st.container(key="photo-container"):
        st.image(st.session_state["manual_image_bytes"],  use_container_width=True)

    if "submitted_manual_teeth" not in st.session_state:
        st.session_state.submitted_manual_teeth = False

    if st.session_state.submitted_manual_teeth and not st.session_state.Professional:
        st.warning("You already submitted your findings!")
        disable_teeth_buttons = True
    else:
        disable_teeth_buttons = False
    circleView=st.session_state.circleView if "circleView" in st.session_state and st.session_state.circleView is not None else False
    if st.session_state.Teethkind == "Child":
        child=True
    else:
        child=False
    manual_teeth = render_teeth("manual", disable_teeth_buttons,circle=circleView, child=child)
    if child:
        st.session_state.manual_teeth_child = manual_teeth
    else:
        st.session_state.manual_teeth = manual_teeth
else:
    st.warning("No image has been uploaded yet.")

# Define the callback
def go_to_next():
    st.session_state.go_to_next_page = True

def go_to_comparison():
    image_path = os.path.join("AIOutput", "image.jpg")
    if os.path.exists(image_path):
        # Full import path to clearly show this comes from another file!!
        st.session_state.ai_teeth = AIOutput.teethSet.teeth
        with open(image_path, "rb") as img_file:
            st.session_state.AI_image_bytes = img_file.read()
    st.session_state.go_to_comparison_page = True

def go_to_upload_page():
    st.session_state.go_to_upload_page = True

def switch_view():
    if "circleView" not in  st.session_state or st.session_state.circleView is None or st.session_state.circleView==False:
        st.session_state.circleView = True  
    else: 
        st.session_state.circleView=False


if st.session_state.Professional:
    st.button("switch view", on_click=switch_view)
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
        st.markdown("""
            <style>
                [data-testid="stForm"] button {
                        border-style: solid;
                        border-width: 1px;
                        justify-content:center;
                        width: fit-content;       
                        padding: 0.5rem;
                        margin-right: 0;
                        margin-left: auto;
                        display: flex;
                        } 
            </style>
            """, unsafe_allow_html=True)

        with st.form("next", border=False):

            nextpage = st.form_submit_button("Next page",use_container_width=True,type="tertiary")
        if nextpage:
            st.switch_page("pages/AI.py")

else:
    st.button("Upload image", on_click=go_to_upload_page)
