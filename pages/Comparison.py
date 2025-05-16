import streamlit as st
from sidebar import load_sidebar
from teeth import load_teeth
from input.teethSet import teeth as manualteeth
from AIOutput.teethSet import teeth as AIteeth
import os
from teeth import get_tooth_image
   
st.set_page_config(page_title="comparison",
                   layout="wide")

def normalize(value):
    if value is None:
        return None
    return set(map(str.strip, value.split(",")))

def compair(manualteeth, AIteeth):
    differences = {}
    for tooth in AIteeth:
        user_val = manualteeth[tooth]
        ai_val = AIteeth[tooth]

        norm_user = normalize(user_val)
        norm_ai = normalize(ai_val)

        if norm_user != norm_ai:
           differences[tooth]=ai_val
    return(differences)

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

differences=compair(manualteeth, AIteeth)

st.markdown("""
<style>
.st-key-container {
    max-width: 900px;
    margin: 0 auto;
}
</style>
""", unsafe_allow_html=True)
with st.container(key="container"):
    
    top_row = list(reversed(range(11, 19))) + list(range(21, 29)) 
    cols = st.columns(16)
    for i, tooth_num in enumerate(top_row):
        if tooth_num in differences:
            with cols[i]:
                st.image(get_tooth_image(tooth_num, differences[tooth_num]))
                
    load_teeth(manualteeth)

    bottom_row = list(reversed(range(31, 39))) + list(range(41, 49)) 
    cols2 = st.columns(16)
    for i, tooth_num in enumerate(bottom_row):
        if tooth_num in differences:
            with cols2[i]:
                st.image(get_tooth_image(tooth_num, differences[tooth_num]))