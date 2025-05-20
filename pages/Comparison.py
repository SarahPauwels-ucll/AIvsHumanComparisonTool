import streamlit as st
from streamlit_cookies_controller import CookieController
from pdf import pdf_button
from sidebar import load_sidebar
from teeth import load_teeth
from input.teethSet import teeth as manualteeth
from AIOutput.teethSet import teeth as AIteeth
import os
from teeth import get_tooth_image
   
st.set_page_config(page_title="comparison", layout="wide")

# Define a session flag to trigger the page switch
if "go_to_next_page" not in st.session_state:
    st.session_state.go_to_next_page = False

# Perform the page switch "outside" the callback
if st.session_state.go_to_next_page:
    st.session_state.go_to_next_page = False
    st.switch_page("app.py")

try:
    manual_teeth =st.session_state.manual_teeth
except:
    manual_teeth=manualteeth
    print("no manual teeth found")

try:
    AI_teeth =st.session_state.ai_teeth
except:
    AI_teeth=AIteeth
    print("no ai teeth found")

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

differences=compair(manual_teeth, AI_teeth)

st.markdown("""
<style>
.st-key-container {
    max-width: 900px;
    margin: 0 auto;
}
.st-key-container div[data-testid="stElementToolbarButtonContainer"] {
        display: none;
}
</style>
""", unsafe_allow_html=True)
with st.container(key="container"):
    st.markdown("Differences Top Teeth")
    top_row = list(reversed(range(11, 19))) + list(range(21, 29)) 
    cols = st.columns(16)
    for i, tooth_num in enumerate(top_row):
        if tooth_num in differences:
            with cols[i]:
                st.image(get_tooth_image(tooth_num, differences[tooth_num]))
    
    st.markdown("Your input") 

    load_teeth(manual_teeth)

    st.markdown("Differences bottom Teeth")
    bottom_row = list(reversed(range(41, 49))) + list(range(31,39))
    cols2 = st.columns(16)
    for i, tooth_num in enumerate(bottom_row):
        if tooth_num in differences:
            with cols2[i]:
                st.image(get_tooth_image(tooth_num, differences[tooth_num]))
st.markdown("""
    <style>
    .st-key-pdf-container {
        max-width: 900px;
        margin: 0 auto;
    }
    </style>
    """, unsafe_allow_html=True)
with st.container(key="pdf-container"):
    col1, col2 = st.columns([16, 5])

    with col2:
        pdf_button()

#switch page
# Define the callback
def restart():
    controller = CookieController()
    keys_to_clear = [
        "ProfileNumber",
        "LastName",
        "FirstName",
        "birthdate",
        "consultation date",
        "Gender"
        "teeth_dict_ai",
        "teeth_dict_manual"
    ]
    for key in st.session_state.keys():
        del st.session_state[key]
    for key in keys_to_clear:  
        controller.set(key, None)
    st.cache_data.clear()
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
        st.button("restart", on_click=restart)


