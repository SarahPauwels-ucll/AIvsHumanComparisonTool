import streamlit as st
from PIL import Image
teeth = {
    11: None, 12: None, 13: None, 14: None, 15: None, 16: None, 17: None, 18: None,
    21: None, 22: None, 23: None, 24: None, 25: None, 26: None, 27: None, 28: None,
    31: None, 32: None, 33: None, 34: None, 35: None, 36: None, 37: None, 38: None,
    41: None, 42: None, 43: None, 44: None, 45: None, 46: None, 47: None, 48: None
}


def get_tooth_image(tooth_number, status,height=80):
    if status is None:
        img= Image.open(f"icons/Icon_normal_teeth/{tooth_number}.png")
    elif status == "implant":
        img= Image.open(f"icons/Icon_implant/{tooth_number}.png")
    elif status == "missing":
        img= Image.open(f"icons/Icon_missing_teeth/{tooth_number}.png")
    else:
        img= Image.open(f"icons/Icon_impacted/{tooth_number}.png")
    w, h = img.size
    new_w = int(w * (height / h))
    return img.resize((new_w, height))

def load_teeth(teeth):
    top_row = list(reversed(range(11, 19))) + list(range(21, 29)) 
    bottom_row = list(reversed(range(31, 39))) + list(range(41, 49)) 

    st.title("Dental Chart")
    cols = st.columns(16)
    for i, tooth_num in enumerate(top_row):
        with cols[i]:
            st.image(get_tooth_image(tooth_num, teeth[tooth_num]))

    cols = st.columns(16)
    for i, tooth_num in enumerate(bottom_row):
        with cols[i]:
            st.image(get_tooth_image(tooth_num, teeth[tooth_num]))