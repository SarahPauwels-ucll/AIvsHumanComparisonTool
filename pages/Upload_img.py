from st_pages import Page, add_page_title
import streamlit as st
from components.sidebar import load_sidebar
import os


st.set_page_config(page_title="Upload image",
                   layout="wide")

if "upload_errors" not in st.session_state:
    st.session_state["upload_errors"] = []

def upload_files():
    st.session_state["upload_errors"] = []
    file = st.session_state["uploaded_files"]

    if file == [] or file == None:
        st.session_state["upload_errors"]=["No files uploaded"]
    else:   
        print("processing file: ", file)
        filename = file.name
        name, ext = os.path.splitext(filename)
        ext = ext.replace('.', '')

        if ext == 'jpeg' or ext =='jpg':
            img_bytes = file.read()
            st.session_state["manual_image_bytes"] = img_bytes
            st.session_state["upload_errors"]=[f"File '{name}' is uploaded successfully"]
            st.session_state.submitted_manual_teeth = False
            image_path = os.path.join("AIOutput", "image.jpg")
            if os.path.exists(image_path):
                with open(image_path, "rb") as img_file:
                    st.session_state.AI_image_bytes = img_file.read()

        else:
            st.session_state["upload_errors"]=[f"Cannot use files with extension '{ext}' use 'jpeg' or 'jpg' instead"]

# layout
load_sidebar("Upload")

st.header("Upload Dental image")
st.markdown("""
    <style>
    .st-key-uploader-container {
        max-width: 900px;
        margin: 0 auto;
    }
    </style>
    """, unsafe_allow_html=True)
with st.container(key="uploader-container"):
    st.error("Please ensure the image is a 'jpeg' or 'jpg'")
    with st.container(border=True):
        file = st.file_uploader("Image uploader", accept_multiple_files=False, key="uploaded_files", type=["jpeg"], on_change=upload_files)
    for message in st.session_state.get("upload_errors", []):
        if "successfully" in message:
            st.success(message)
        else:
            st.error(message)
    st.markdown("""
        <style>
            [data-testid="stForm"] button {
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

    with st.form("next", border=False):
        nextpage = st.form_submit_button("Next page",use_container_width=True,type="tertiary")
    if nextpage:
        st.switch_page("pages/Manual.py") 
