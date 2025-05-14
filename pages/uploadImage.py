from st_pages import Page, add_page_title
import streamlit as st
import os


st.set_page_config(page_title="Upload image",
                   page_icon=":books:",
                   layout="wide")


 
def upload_files():
    files = st.session_state["uploaded_files"]

    for file in files:
        print("processing file: ", file)
        filename = file.name
        name, ext = os.path.splitext(filename)
        ext = ext.replace('.', '')
        if ext == 'jpg':
            file_size = file.size
            if file_size / 1e6 < 25:

                os.makedirs("image", exist_ok=True)
                with open(os.path.join("image",file.name),"wb") as f:
                    f.write(file.getbuffer())
                
            else: # should show warning
                print(f"Cannot use files with extension '{ext}' with size bigger than 25MB.")
        else:
             print(f"Cannot use files with extension '{ext}'")
        
            

st.markdown(" # Upload Data")

# upload files 
st.header("Upload Dental image")
st.error("Please ensure the image is an bla bla bla bla bla")
with st.container(border=True):
    files = st.file_uploader("Image uploader", accept_multiple_files=True, key="uploaded_files")

    st.button("Upload image", on_click=upload_files)