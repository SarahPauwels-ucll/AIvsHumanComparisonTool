import streamlit as st
from st_pages import Page, add_page_title
from sidebar import load_sidebar
import os

st.set_page_config(page_title="AI vs. Human analysis: A smart comparison tool",
                   layout="wide")

load_sidebar()

st.title("Welcome to the manual page!")
st.write("Here we can manualy alter the chart.")


image_path = os.path.join("image", "image.jpg")
# Check if the image exists
if os.path.exists(image_path):
    st.image(image_path, caption="Uploaded Dental Image",  use_container_width=True)
else:
    st.warning("No image has been uploaded yet.")