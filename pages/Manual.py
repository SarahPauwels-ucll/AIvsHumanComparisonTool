import streamlit as st
from st_pages import Page, add_page_title

from pdf_profesionnal import pdf_button_professional
from teeth_renderer import render_teeth
from sidebar import load_sidebar
from teeth import load_teeth
import os

#switch page
# Define a session flag to trigger the page switch
if "go_to_next_page" not in st.session_state:
    st.session_state.go_to_next_page = False

# Perform the page switch "outside" the callback
if st.session_state.go_to_next_page:
    st.session_state.go_to_next_page = False
    st.switch_page("pages/AI.py")

st.set_page_config(page_title="AI vs. Human analysis: A smart comparison tool",
                   layout="wide")



load_sidebar()

st.title("Welcome to the manual page!")

image_path = os.path.join("image", "image.jpeg")

if os.path.exists(image_path):
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
    
    manual_teeth = render_teeth("manual")
    st.session_state.manual_teeth = manual_teeth
else:
    st.warning("No image has been uploaded yet.")

# Define the callback
def go_to_next():
    st.session_state.go_to_next_page = True


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
        st.button("Next Page", on_click=go_to_next)

pdf_button_professional()
