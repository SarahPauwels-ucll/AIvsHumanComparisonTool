import streamlit as st
from components.excel import excel_button
from components.teeth_renderer import render_teeth
from input.teethSet import teeth as manualteeth

from components.sidebar import load_sidebar
import os
from streamlit_cookies_controller import CookieController

if "go_to_upload_page" not in st.session_state:
    st.session_state.go_to_upload_page = False

controller = CookieController()

if st.session_state.go_to_upload_page:
    st.session_state.go_to_upload_page = False
    st.switch_page("pages/Upload_img.py")

st.set_page_config(page_title="AI vs. Human analysis: A smart comparison tool",
                   layout="wide")

try:
    manual_teeth =st.session_state.manual_teeth
except:
    st.session_state.manual_teeth=manualteeth
    print("no manual teeth found")

load_sidebar("AI")

st.title("Welcome to the AI page!")
if st.session_state.Professional:
    st.switch_page("pages/Comparison.py")

# Check if the image exists
if "manual_image_bytes" in st.session_state:
    st.markdown("""
    <style>
    .st-key-photo-container {
        max-width: 900px;
        margin: 0 auto;
    }
    </style>
    """, unsafe_allow_html=True)
    ai_image = st.session_state.AI_image_bytes
    with st.container(key="photo-container"):
        st.image(ai_image,  use_container_width=True)
    circleView=st.session_state.circleView if "circleView" in st.session_state and st.session_state.circleView is not None else False
    if st.session_state.Teethkind == "Child":
        child=True
    else:
        child=False
    ai_teeth = render_teeth("ai", circle=circleView, child=child)

    # ✅ Always update AI teeth in session state with the latest render
    if child:
        st.session_state["ai_teeth_child"] = ai_teeth
    else:
        st.session_state["ai_teeth"] = ai_teeth

else:
    st.warning("No image has been uploaded yet.")

#switch page
def go_to_upload_page():
    st.session_state.go_to_upload_page = True

def switch_view():
    if "circleView" not in  st.session_state or st.session_state.circleView is None or st.session_state.circleView==False:
        st.session_state.circleView = True  
    else: 
        st.session_state.circleView=False

if "manual_image_bytes" in st.session_state:
    st.markdown("""
    <style>
    .st-key-next-container {
        max-width: 900px;
        margin: 0 auto;
    }
    </style>
    """, unsafe_allow_html=True)
    with st.container(key="next-container"):
        st.markdown("""
            <style>
                .st-key-next-container [data-testid="stForm"] button {
                        border-style: solid;
                        border-width: 1px;
                        justify-content:center;
                        width: fit-content;       
                        padding: 0.5rem;
                        margin-right: 0;
                        margin-left: auto;
                        display: flex;
                        } 
            </style>
            """, unsafe_allow_html=True)            
        col1, col2 = st.columns([1, 1])  
        with col1:
            if st.session_state.Professional:
                st.button("Switch view", on_click=switch_view)
        with col2:
            with st.form("next", border=False):
                nextpage = st.form_submit_button("Next page",use_container_width=True,type="tertiary")
        if nextpage:
            st.switch_page("pages/Comparison.py") 

else:
    st.button("Upload image", on_click=go_to_upload_page)