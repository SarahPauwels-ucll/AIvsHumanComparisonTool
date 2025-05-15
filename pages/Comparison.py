from st_pages import Page, add_page_title
import streamlit as st
from sidebar import load_sidebar
from teeth import load_teeth
from input.teethSet import teeth
import os
   
st.set_page_config(page_title="comparison",
                   layout="wide")


load_sidebar()

st.title("Comparison page!")
ai_image_path = os.path.join("AIOutput", "image.jpg")
image_path=os.path.join("image", "image.jpeg")
# Check if the image exists
if os.path.exists(ai_image_path) and os.path.exists(image_path) :
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
            st.image(image_path,  use_container_width=True)
        with cols[1]:
            st.image(ai_image_path,  use_container_width=True)
else:
    st.warning("No image has been uploaded yet.")

load_teeth(teeth)