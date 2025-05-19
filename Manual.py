import streamlit as st
from st_pages import Page, add_page_title

from teeth_renderer import render_teeth
from sidebar import load_sidebar
from teeth import load_teeth
import os

st.set_page_config(page_title="AI vs. Human analysis: A smart comparison tool",
                   layout="wide")

load_sidebar()

st.title("Welcome to the manual page!")
st.write("Here we can manualy alter the chart.")


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