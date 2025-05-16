import streamlit as st
from st_pages import Page, add_page_title

from pages.teeth_renderer import render_teeth
from sidebar import load_sidebar
from teeth import load_teeth
import os

st.set_page_config(page_title="AI vs. Human analysis: A smart comparison tool",
                   layout="wide")

load_sidebar()

st.title("Welcome to the manual page!")
st.write("Here we can manualy alter the chart.")


image_path = os.path.join("image", "image.jpeg")

# Check if the image exists
if os.path.exists(image_path):
    st.image(image_path, caption="Uploaded Dental Image",  use_container_width=True)
    render_teeth()
else:
    st.warning("No image has been uploaded yet.")

