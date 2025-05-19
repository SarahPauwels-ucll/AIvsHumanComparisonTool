import streamlit as st
from teeth_renderer import render_teeth

from sidebar import load_sidebar
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
    ai_teeth = render_teeth("ai")
    st.session_state.ai_teeth = ai_teeth
else:
    st.warning("No image has been uploaded yet.")

#switch page
# Define a session flag to trigger the page switch
if "go_to_next_page" not in st.session_state:
    st.session_state.go_to_next_page = False

print(st.session_state.manual_teeth)
print(st.session_state.ai_teeth)
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

# Perform the page switch "outside" the callback
if st.session_state.go_to_next_page:
    st.session_state.go_to_next_page = False
    st.switch_page("pages/Comparison.py")