import streamlit as st
from st_pages import Page, add_page_title

from pages.teeth_renderer import render_teeth
from sidebar import load_sidebar
from teeth import load_teeth
from AIOutput.teethSet import teeth
import os

st.set_page_config(page_title="AI vs. Human analysis: A smart comparison tool",
                   layout="wide")

load_sidebar()

st.title("Welcome to the AI page!")

image_path = os.path.join("AIOutput", "image.jpg")
# Check if the image exists
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
else:
    st.warning("No image has been uploaded yet.")

render_teeth()
