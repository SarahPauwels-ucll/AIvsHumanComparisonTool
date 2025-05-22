import os.path
import math
import streamlit as st
from PIL import Image
import base64
from io import BytesIO
#example input
teeth = {
    11: None, 12: "missing,implant", 13: None, 14: None, 15: "impacted", 16: None, 17: None, 18: None,
    21: None, 22: None, 23: None, 24: "missing", 25: "bridgde,rcf", 26: "missing,crown,implant", 27: None, 28: "df,rcf",
    31: "bridge", 32: "normal", 33: None, 34: "crown,rcf", 35: None, 36: None, 37: None, 38: None,
    41: None, 42: None, 43: "crown", 44: None, 45: "missing,brigde", 46: "missing,brigde,implant", 47: "df", 48: None
}


def get_tooth_image(tooth_number, status, height=80, icon_variant="white", as_base64=False):
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

def load_teeth_circle(teeth):
    st.title("32 Divs in een Cirkel (CSS only, werkt in Streamlit)")

    # Parameters
    num_items = 32
    container_size = 500
    item_size = 60
    radius = (container_size - item_size) / 2
    center = container_size / 2

    # Begin van HTML + CSS
    html = f"""
    <style>
    .circle-container {{
    position: relative;
    width: {container_size}px;
    height: {container_size}px;
    margin: 50px auto;
    border: 1px dashed lightgray;
    border-radius: 50%;
    }}
    .item {{
    position: absolute;
    width: {item_size}px;
    height: {item_size}px;
    background-color: teal;
    color: white;
    text-align: center;
    line-height: {item_size}px;
    border-radius: 50%;
    font-size: 16px;
    transform: translate(-50%, -50%);
    }}
    </style>
    <div class="circle-container">
    """

    # Voeg de 32 items toe op de juiste posities
    for i in range(num_items+1):
        angle_deg = i * (360 / num_items)
        angle_rad = math.radians(angle_deg)
        x = center + radius * math.cos(angle_rad)
        y = center + radius * math.sin(angle_rad)
        html += f'<div class="item" style="left: {x}px; top: {y}px;">{i}</div>\n'

    html += "</div>"

    # Inject in Streamlit
    st.markdown(html, unsafe_allow_html=True)

    # st.markdown("""
    #     <style>
    #     .teeth-container {
    #         position: relative;
    #         width: 600px;
    #         height: 600px;
    #         margin: 0 auto;
    #     }
    #     .tooth {
    #         position: absolute;
    #         height: 60px;
    #         width: auto;
    #         transform-origin: center center;
    #     }
    #     </style>
    # """, unsafe_allow_html=True)

    # st.markdown('<div class="teeth-container">', unsafe_allow_html=True)

    # # All teeth numbers in order around the circle
    # all_teeth = (
    #     list(reversed(range(11, 19))) + list(range(21, 29)) +
    #     list(reversed(range(41, 49))) + list(range(31, 39))
    # )

    # center_x = 200
    # center_y = 200
    # radius = 100

    # for i, tooth_num in enumerate(all_teeth):
    #     angle_deg = 360 * i / len(all_teeth)
    #     angle_rad = math.radians(angle_deg)
        

    #     x = center_x + radius * math.cos(angle_rad)
    #     y = center_y + radius * math.sin(angle_rad)

    #     img_src, (img_w, img_h) = get_tooth_image(tooth_num, teeth.get(tooth_num), as_base64=True)

    #     rotation = angle_deg -90

    #     print(str(tooth_num)+ " : "+ str(rotation)+ ' x='+str(x)," y="+str(y))
    #     # st.markdown(f'''
                    
    #     #     <img class="tooth" src="{img_src} alt={tooth_num}"
    #     #          style="left: {x - img_w / 2}px; top: {y - img_h / 2}px; transform: rotate({rotation}deg);"/>
    #     # ''', unsafe_allow_html=True)
    #     st.markdown(f'''
    #     <div style="position:absolute; width:10px; height:10px; 
    #             background:red; border-radius:50%; 
    #             transform: rotate(${angle_deg}deg) translate(${radius}px)"></div>
    #         ''', unsafe_allow_html=True)


    # st.markdown('</div>', unsafe_allow_html=True)


