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
    11: "jfslkjflkds", 12: "implant", 13: None, 14: None, 15: "impacted", 16: None, 17: None, 18: None,
    21: None, 22: None, 23: None, 24: "missing", 25: "bridgde,rcf", 26: "crown,implant", 27: None, 28: "df,rcf",
    31: "bridge", 32: "normal", 33: None, 34: "crown,rcf", 35: None, 36: None, 37: None, 38: None,
    41: None, 42: None, 43: "crown", 44: None, 45: "brigde,pontic", 46: "brigde,implant", 47: "df", 48: None
}

load_teeth(teeth)