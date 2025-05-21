import os.path

import streamlit as st
from PIL import Image

#example input
teeth = {
    11: None, 12: "missing,implant", 13: None, 14: None, 15: "impacted", 16: None, 17: None, 18: None,
    21: None, 22: None, 23: None, 24: "missing", 25: "bridgde,rcf", 26: "missing,crown,implant", 27: None, 28: "df,rcf",
    31: "bridge", 32: "normal", 33: None, 34: "crown,rcf", 35: None, 36: None, 37: None, 38: None,
    41: None, 42: None, 43: "crown", 44: None, 45: "missing,brigde", 46: "missing,brigde,implant", 47: "df", 48: None
}

def get_tooth_image(tooth_number, status,height=80, icon_variant = "black"):
    if icon_variant == "black":
       path_prefix = "icons"
    elif icon_variant == "white":
       path_prefix = "icons_white_scaled"
    else:
       raise ValueError("icon variant should be black or white")
    
    if status is None or status=="normal":
        icon_path= f"Icon_normal_teeth/{tooth_number}.png"
    
    elif status == "missing":
        icon_path= f"Icon_missing_teeth/{tooth_number}.png"
    elif "impacted" in status:
        icon_path= f"Icon_impacted/{tooth_number}.png"
    elif status == "missing,implant":
        icon_path = f"Icon_implant/{tooth_number}.png"
    
    elif "df" in status and "rcf" in status:
        icon_path = f"Icon_df_rcf/{tooth_number}.png"
    elif "df" in status:
        icon_path= f"Icon_df/{tooth_number}.png"
    
    elif "rcf" in status and "crown" in status:
        icon_path= f"Icon_crown_rcf/{tooth_number}.png"
    elif "implant" in status and "crown" in status:
        icon_path= f"Icon_crown_implant/{tooth_number}.png"
    elif "crown" in status:
        icon_path= f"Icon_crown/{tooth_number}.png"
    
    elif "rcf" in status and "bridge" in status:
        icon_path= f"Icon_bridge_tooth_rcf/{tooth_number}.png"
    elif "bridge" in status and "implant" in status:
        icon_path= f"Icon_bridge_implant/{tooth_number}.png"
    elif status=="missing,bridge":
        icon_path= f"Icon_bridge_pontic/{tooth_number}.png"
    elif "bridge" in status and "normal" in status:
        icon_path= f"Icon_bridge_tooth/{tooth_number}.png"
    else:
        icon_path= f"Icon_normal_teeth/{tooth_number}.png"
        print("tooth number: "+tooth_number+ " has an invalid tooth condition")
    
    full_path = os.path.join(path_prefix, icon_path)
    img = Image.open(full_path)
    
    w, h = img.size
    new_w = int(w * (height / h))
    return img.resize((new_w, height))

def load_teeth(teeth):

    top_row = list(reversed(range(11, 19))) + list(range(21, 29))
    bottom_row = list(reversed(range(41, 49))) + list(range(31, 39))


    cols = st.columns(16)
    for i, tooth_num in enumerate(top_row):
        with cols[i]:
            st.image(get_tooth_image(tooth_num, teeth[tooth_num]))

    cols2 = st.columns(16)
    for i, tooth_num in enumerate(bottom_row):
        with cols2[i]:
            st.image(get_tooth_image(tooth_num, teeth[tooth_num]))