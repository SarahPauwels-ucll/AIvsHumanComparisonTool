import os
import streamlit as st
from components.teeth import load_teeth, load_teeth_circle
from input.teethSet import teeth as teethInput, childteeth as childteethInput
from AIOutput.teethSet import teeth as teethAI, childteeth as childteethAI
import copy

def render_teeth(page: str, disable_buttons: bool = False,circle=False,child=False):
    if not page:
        raise Exception("page can't be empty")
    @st.cache_data()
    def get_teeth_data(teeth) -> dict[int, str | None]:
        teeth_dict = copy.deepcopy(teeth)
        return teeth_dict

    def check_checkbox_status(checkbox_name: str, tooth_number: int) -> bool:
        return True if checkbox_name in str(teeth[tooth_number]) else False

    def check_checkbox_disabled(false_when_enabled: list[str], tooth_number: int) -> bool:
        return len([x for x in false_when_enabled if x in str(teeth[tooth_number])]) > 0

    if not st.session_state.get(f"childteeth_dict_{page}"):
        if page=="ai":
                teeth = get_teeth_data(childteethAI)
        else:
                teeth = get_teeth_data(childteethInput)
        st.session_state[f"childteeth_dict_{page}"] = teeth

    if not st.session_state.get(f"teeth_dict_{page}"):
        if page=="ai":
            teeth = get_teeth_data(teethAI)
        else:
            teeth = get_teeth_data(teethInput)
        st.session_state[f"teeth_dict_{page}"] = teeth

    if child:
        teeth = st.session_state[f"childteeth_dict_{page}"]
    else:

        teeth = st.session_state[f"teeth_dict_{page}"]

    if "show_tooth_config_dialog" not in st.session_state:
        st.session_state.show_tooth_config_dialog = False

    def toggle_tooth_presence(presence: str, tooth_number: int):
        if teeth[tooth_number] == presence or teeth[tooth_number] is None:
            if presence == "missing":
                if "missing" in str(teeth[tooth_number]):
                    teeth[tooth_number] = None
                else:
                    teeth[tooth_number] = "missing"
            if presence == "normal":
                if "normal" in str(teeth[tooth_number]):
                    teeth[tooth_number] = None
                else:
                    teeth[tooth_number] = "normal"

        elif presence in str(teeth[tooth_number]):
            if presence == "missing" or presence == "normal":
                teeth[tooth_number] = None

            else:
                teeth[tooth_number] = str(teeth[tooth_number]).replace(f",{presence}", "")
        else:
            teeth[tooth_number] = str(teeth[tooth_number]) + f",{presence}"

    @st.dialog( " ", width="large")
    def show_options(teeth: dict[int, str | None], add_to_corrected_set: bool = False):
        tooth_number = st.session_state.selected_tooth
        missing_properties = ["Implant", "Implant bridge", "Implant crown", "Bridge"]
        present_properties = ["Dental filling", "Impacted", "Crown", "Bridge", "Root canal filling"]

        st.title(f"Tooth {tooth_number}")
        col1, col2 = st.columns(2)

        with col1:
            if "missing" in str(teeth[tooth_number]):
                present_checkbox = st.checkbox("Present", key=f"present_{tooth_number}", disabled=True)
            else:
                present_checkbox = st.checkbox("Present", key=f"present_{tooth_number}", on_change=toggle_tooth_presence, args=("normal", tooth_number), value=check_checkbox_status("normal", tooth_number))

        with col2:
            if "normal" in str(teeth[tooth_number]):
                missing_checkbox = st.checkbox("Missing", key=f"missing_{tooth_number}", disabled=True)
            else:
                missing_checkbox = st.checkbox("Missing", key=f"missing_{tooth_number}", on_change=toggle_tooth_presence, args=("missing", tooth_number), value=check_checkbox_status("missing", tooth_number))

        with col1:
            if present_checkbox:
                impacted_checkbox = st.checkbox("Impacted", disabled=check_checkbox_disabled(["bridge","crown","rcf","df"], tooth_number), on_change=toggle_tooth_presence, args=("impacted",tooth_number), value=check_checkbox_status("impacted", tooth_number))
                dental_filling_checkbox = st.checkbox("Dental filling", disabled=check_checkbox_disabled(["crown","bridge","rcf","impacted"],tooth_number), on_change=toggle_tooth_presence, args=("df",tooth_number), value=check_checkbox_status("df", tooth_number))
                bridge_checkbox = st.checkbox("Bridge", disabled=check_checkbox_disabled(["df","crown","rcf","impacted"],tooth_number), on_change=toggle_tooth_presence, args=("bridge",tooth_number), value=check_checkbox_status("bridge", tooth_number))
                crown_checkbox = st.checkbox("Crown", disabled=check_checkbox_disabled(["df","bridge","rcf","impacted"],tooth_number), on_change=toggle_tooth_presence, args=("crown",tooth_number), value=check_checkbox_status("crown", tooth_number))
                root_canal_filling_checkbox = st.checkbox("Root canal filling", disabled= not check_checkbox_disabled(["crown","bridge","df"],tooth_number), on_change=toggle_tooth_presence, args=("rcf",tooth_number), value=check_checkbox_status("rcf", tooth_number))

            if missing_checkbox:
                implant_checkbox = st.checkbox("Implant", disabled=check_checkbox_disabled(["crown"],tooth_number), on_change=toggle_tooth_presence, args=("implant",tooth_number), value=check_checkbox_status("implant", tooth_number))
                if not "crown" in str(teeth[tooth_number]):
                    bridge_checkbox = st.checkbox("Bridge", on_change=toggle_tooth_presence, args=("bridge",tooth_number), value=check_checkbox_status("bridge", tooth_number))
                elif "implant" not in str(teeth[tooth_number]):
                    bridge_checkbox = st.checkbox("Bridge", disabled=True, value=check_checkbox_status("bridge,pontic", tooth_number))
                else:
                    bridge_checkbox = st.checkbox("Bridge", disabled=True, value=check_checkbox_status("bridge", tooth_number))
                if implant_checkbox and not "bridge" in str(teeth[tooth_number]):
                    crown_checkbox = st.checkbox("Crown", on_change=toggle_tooth_presence, args=("crown",tooth_number), value=check_checkbox_status("crown", tooth_number))
                else:
                    crown_checkbox = st.checkbox("Crown", disabled=True, value=check_checkbox_status("crown", tooth_number))

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Clear all"):
                teeth[tooth_number] = None
                st.rerun()

        with col2:
            if st.button("Submit"):
                st.session_state.show_tooth_config_dialog = False
                if add_to_corrected_set:
                    if not st.session_state.get("corrected_teeth", False):
                        st.session_state.corrected_teeth = set()
                    st.session_state.corrected_teeth.add(tooth_number)
                st.rerun()
    if child:
        top_left_nums = [55,54,53,52,51]
        top_right_nums = [61,62,63,64,65]
        bottom_left_nums = [85,84,83,82,81]
        bottom_right_nums = [71,72,73,74,75]
    else:
        top_left_nums = [18,17,16,15,14,13,12,11]
        top_right_nums = [21,22,23,24,25,26,27,28]
        bottom_left_nums = [48,47,46,45,44,43,42,41]
        bottom_right_nums = [31,32,33,34,35,36,37,38]



    def show_tooth_modal(tooth_number):
        st.session_state.selected_tooth = tooth_number
        st.session_state.show_tooth_config_dialog = True


    def render_button_row(columns, numbers, teeth, disable_buttons, differences=None,
                          color_differences_instead_of_manual=False):
        if differences is None:
            differences = {}
        for column, n in zip(columns, numbers):
            with column:
                button_key = f"btn_{n}_b"
                button_color = None
                if teeth[n] is not None and not color_differences_instead_of_manual:
                    button_color = "background-color: rgb(255, 51, 0)"
                if n in differences.keys() and color_differences_instead_of_manual:
                    button_color = "background-color: rgb(255, 51, 0)"

                custom_css = f"""
                    <style>
                        .st-key-{button_key} button {{
                            white-space: nowrap !important;
                            color: white !important;
                            {button_color if button_color else ""}
                        }}
                    </style>
                    """
                st.markdown(custom_css, unsafe_allow_html=True)
                button = st.button(str(n), key=button_key, disabled=disable_buttons)
                if button:
                    if differences and n in differences:
                        st.session_state.modal_tooth_num = n
                        st.session_state.modal_tooth_show_diff_modal = True
                    else:
                        show_tooth_modal(n)
    st.markdown("""
    <style>
    .st-key-tooth-container {
        max-width: 900px;
        margin: 0 auto;
    }
    .st-key-tooth-container div[data-testid="stElementToolbarButtonContainer"] {
        display: none;
    }
    </style>
    """, unsafe_allow_html=True)
    with st.container(key="tooth-container"):

        top_cols = st.columns(len(top_left_nums + top_right_nums))
        top_nums = top_left_nums + top_right_nums
        render_button_row(top_cols,top_nums, teeth, disable_buttons)
        
        if circle:
            load_teeth_circle(teeth)
        else:
            load_teeth(teeth)

        bottom_cols = st.columns(len(bottom_left_nums + bottom_right_nums))
        bottom_nums = bottom_left_nums + bottom_right_nums
        render_button_row(bottom_cols,bottom_nums, teeth, disable_buttons)

        if st.session_state.show_tooth_config_dialog:
            show_options(teeth)
    return teeth