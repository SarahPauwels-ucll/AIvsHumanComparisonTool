import os.path
import math
import streamlit as st
from PIL import Image
import base64
from io import BytesIO

def pil_image_to_base64(pil_image):
    buffered = BytesIO()
    pil_image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return img_str

def img_to_html(pil_image):
    encoded_img = pil_image_to_base64(pil_image)
    mime_type = f"image/png"
    img_html = f"<img src='data:{mime_type};base64,{encoded_img}' class='img-fluid' alt='Tooth Image'>"
    return img_html

def pil_to_data_url(pil_image):
    buffered = BytesIO()
    pil_image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"

#example input
teeth = {
    11: None, 12: "missing,implant", 13: None, 14: None, 15: "impacted", 16: None, 17: None, 18: None,
    21: None, 22: None, 23: None, 24: "missing", 25: "bridgde,rcf", 26: "missing,crown,implant", 27: None, 28: "df,rcf",
    31: "bridge", 32: "normal", 33: None, 34: "crown,rcf", 35: None, 36: None, 37: None, 38: None,
    41: None, 42: None, 43: "crown", 44: None, 45: "missing,brigde", 46: "missing,brigde,implant", 47: "df", 48: None
}


def get_tooth_image(tooth_number, status, height=80, icon_variant="white", as_base64=False):
    #remove this if you we add children tooth icons
    if tooth_number>50:
        if status is not None and status != "normal":       
            if tooth_number%10<4:
                tooth_number-=40
            else:
                tooth_number-=38
    #----------------------------------------------

    if icon_variant == "black":
        path_prefix = "icons"
    elif icon_variant == "white":
        path_prefix = "icons_white_scaled"
    else:
        raise ValueError("icon variant should be black or white")

    # Determine correct icon path
    if status is None or status == "normal":
        icon_path = f"Icon_normal_teeth/{tooth_number}.png"
    elif status == "missing":
        icon_path = f"Icon_missing_teeth/{tooth_number}.png"
    elif "impacted" in status:
        icon_path = f"Icon_impacted/{tooth_number}.png"
    elif status == "missing,implant":
        icon_path = f"Icon_implant/{tooth_number}.png"
    elif "df" in status and "rcf" in status:
        icon_path = f"Icon_df_rcf/{tooth_number}.png"
    elif "df" in status:
        icon_path = f"Icon_df/{tooth_number}.png"
    elif "rcf" in status and "crown" in status:
        icon_path = f"Icon_crown_rcf/{tooth_number}.png"
    elif "implant" in status and "crown" in status:
        icon_path = f"Icon_crown_implant/{tooth_number}.png"
    elif "crown" in status:
        icon_path = f"Icon_crown/{tooth_number}.png"
    elif "rcf" in status and "bridge" in status:
        icon_path = f"Icon_bridge_tooth_rcf/{tooth_number}.png"
    elif "bridge" in status and "implant" in status:
        icon_path = f"Icon_bridge_implant/{tooth_number}.png"
    elif status == "missing,bridge":
        icon_path = f"Icon_bridge_pontic/{tooth_number}.png"
    elif "bridge" in status and "normal" in status:
        icon_path = f"Icon_bridge_tooth/{tooth_number}.png"
    else:
        icon_path = f"Icon_normal_teeth/{tooth_number}.png"
        print(f"tooth number: {tooth_number} has an unrecognized status")

    full_path = os.path.join(path_prefix, icon_path)
    img = Image.open(full_path)

    # Resize the image
    w, h = img.size
    new_w = int(w * (height / h))
    img_resized = img.resize((new_w, height))
    resized_width, resized_height = img_resized.size
    if as_base64:
        # Convert to base64 string
        buffer = BytesIO()
        img_resized.save(buffer, format="PNG")
        img_str = base64.b64encode(buffer.getvalue()).decode()
        return f"data:image/png;base64,{img_str}", (resized_width, resized_height)
    else:
        # Return PIL image for st.image
        return img_resized


def load_teeth(teeth,child, outline_corrected_images: bool = False):
    if child:
        top_row = list(reversed(range(51, 56))) + list(range(61, 66))
        bottom_row = list(reversed(range(81, 86))) + list(range(71, 76))
        cols = st.columns(10)
        cols2 = st.columns(10)
    else:
        top_row = list(reversed(range(11, 19))) + list(range(21, 29))
        bottom_row = list(reversed(range(41, 49))) + list(range(31, 39))
        cols = st.columns(16)
        cols2 = st.columns(16)

    corrected_teeth = st.session_state.get("corrected_teeth", set())


    for i, tooth_num in enumerate(top_row):
        with cols[i]:
            img = get_tooth_image(tooth_num, teeth[tooth_num])
            if outline_corrected_images and tooth_num in corrected_teeth:
                data_url = pil_to_data_url(img)
                st.markdown(
                    f"""
                    <img src="{data_url}"
                         style="
                             outline:2px solid red;
                             outline-offset:-2px;
                             border-radius: 5px;
                             height:auto; width:auto;
                         ">
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.image(img)


    for i, tooth_num in enumerate(bottom_row):
        with cols2[i]:
            img = get_tooth_image(tooth_num, teeth[tooth_num])
            if outline_corrected_images and tooth_num in corrected_teeth:
                data_url = pil_to_data_url(img)
                st.markdown(
                    f"""
                    <img src="{data_url}"
                         style="
                             outline:2px solid red;
                             outline-offset:-2px;
                             border-radius: 5px;
                             height:auto; width:auto;
                         ">
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.image(img)

def load_teeth_circle(teeth, child):
    if child:
        top_row = list(reversed(range(51, 56))) + list(range(61, 66))
        bottom_row = list(reversed(range(71, 76))) + list(range(81, 86))
    else:
        top_row = list(reversed(range(11, 19))) + list(range(21, 29))
        bottom_row = list(reversed(range(31, 39))) + list(range(41, 49))

    all_teeth =bottom_row+top_row

    num_items = len(all_teeth)
    container_size = 600
    radius = (container_size-100) / 3
    center = container_size / 2

    html = f"""
    <style>
    .circle-container {{
    position: relative;
    width: {container_size}px;
    height: {container_size}px;
    margin: 50px auto;
    }}
    .item {{
    position: absolute;
    object-fit: contain;
    transform: translate(-50%, -50%);
    }}
    </style>
    <div class="circle-container">
    """

    for i, tooth_num in enumerate(all_teeth):
        img_src, (width, height)= get_tooth_image(tooth_num, teeth[tooth_num], as_base64=True)
        angle_deg = (i * (360 / num_items))+(360 / num_items)/2
        if child:
            row=10
        else:
            row=16
        if i < row:
            rotation=angle_deg + 90
        else:
            rotation=angle_deg-90
        angle_rad = math.radians(angle_deg)
        x = center + radius * math.cos(angle_rad)
        y = center-50 + 1.7*(radius * math.sin(angle_rad))
        if y>center-50:
            y+=50
        html += (
            f'<img class="item" src="{img_src}" '
            f'style="left: {x}px; top: {y}px; transform: rotate({rotation}deg);" '
            f'title="Tooth {tooth_num}" alt="Tooth {tooth_num}">'
        )
    html += "</div>"

    st.markdown(html, unsafe_allow_html=True)
