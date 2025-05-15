import streamlit as st
from st_pages import Page, add_page_title
from sidebar import load_sidebar
from teeth import load_teeth
from AIOutput.teethSet import teeth
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

load_teeth(teeth)
