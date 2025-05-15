import streamlit as st
from st_pages import Page, add_page_title
from sidebar import load_sidebar
from teeth import load_teeth
import os

st.set_page_config(page_title="AI vs. Human analysis: A smart comparison tool",
                   layout="wide")

load_sidebar()

st.title("Welcome to the AI page!")
st.write("Here we can see the AI results.")

image_path = os.path.join("AIOutput", "image.jpg")
# Check if the image exists
if os.path.exists(image_path):
    st.image(image_path, caption="Uploaded Dental Image",  use_container_width=True)
else:
    st.warning("No image has been uploaded yet.")

teeth = {
    11: None, 12: None, 13: None, 14: None, 15: None, 16: None, 17: None, 18: None,
    21: None, 22: None, 23: None, 24: None, 25: None, 26: None, 27: None, 28: None,
    31: None, 32: None, 33: None, 34: None, 35: None, 36: None, 37: None, 38: None,
    41: None, 42: None, 43: None, 44: None, 45: None, 46: None, 47: None, 48: None
}

load_teeth(teeth)