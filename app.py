from st_pages import Page, add_page_title
import streamlit as st
from sidebar import load_sidebar
import os
   
st.set_page_config(page_title="Upload image",
                   layout="wide")

if "upload_errors" not in st.session_state:
    st.session_state["upload_errors"] = []

def upload_files():
    st.session_state["upload_errors"] = []
    files = st.session_state["uploaded_files"]

    if files==[]or files==None:
        st.session_state["upload_errors"].append("No files uploaded")
    for file in files:
        print("processing file: ", file)
        filename = file.name
        name, ext = os.path.splitext(filename)
        ext = ext.replace('.', '')

        if ext == 'jpeg':
                os.makedirs("image", exist_ok=True)
                with open(os.path.join("image","image.jpeg"),"wb") as f:
                    f.write(file.getbuffer())
                st.session_state["upload_errors"].append(f"File '{name}' is uploaded successfully")

        else:
             st.session_state["upload_errors"].append(f"Cannot use files with extension '{ext}' use 'jpeg' instead")

# layout
load_sidebar()

st.header("Upload Dental image")
st.error("Please ensure the image is an 'jpeg'")
with st.container(border=True):
    files = st.file_uploader("Image uploader", accept_multiple_files=True, key="uploaded_files")

    st.button("Upload image", on_click=upload_files)

for message in st.session_state.get("upload_errors", []):
    if "successfully" in message:
        st.success(message)
    else:
        st.error(message)



#switch page
# Define a session flag to trigger the page switch
if "go_to_next_page" not in st.session_state:
    st.session_state.go_to_next_page = False

# Define the callback
def go_to_next():
    st.session_state.go_to_next_page = True

# Show the button
st.button("Next Page", on_click=go_to_next)

# Perform the page switch "outside" the callback
if st.session_state.go_to_next_page:
    st.session_state.go_to_next_page = False
    st.switch_page("pages/Manual.py")
   