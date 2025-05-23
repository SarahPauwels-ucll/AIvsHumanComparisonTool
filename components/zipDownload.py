from components.pdf import create_pdf
import streamlit as st
import io
import zipfile
import openpyxl
import pandas as pd
from openpyxl.utils import get_column_letter
from typing import Dict, List, Set

from components.pdf_profesionnal import create_pdf_professional


def combined_download_button():


    # --- Generate Excel ---
    excel_buffer = io.BytesIO()
    manual_teeth: Dict[int, str] = st.session_state.get("manual_teeth", {})
    ai_teeth: Dict[int, str] = st.session_state.get("ai_teeth", {})
    final_teeth: Dict[int, str] = st.session_state.get("final_teeth", {})

    data_sources: List[Dict[int, str]] = [manual_teeth, ai_teeth, final_teeth]
    source_names: List[str] = ["Manual", "AI", "Corrected"]

    def parse_tags(raw_value: str) -> List[str]:
        if raw_value is None:
            return []
        pieces = [part.strip() for part in raw_value.split(",")]
        return [p for p in pieces if p]

    all_tags: Set[str] = {"normal"}
    for src_dict in data_sources:
        for value in src_dict.values():
            for tag in parse_tags(value):
                all_tags.add(tag)

    rows: List[Dict[str, str]] = []

    for src_name, src_dict in zip(source_names, data_sources):
        row: Dict[str, str] = {"source": src_name}

        # First, check for normal tag as a special case, since both None and normal count as normal
        normal_keys: List[int] = []
        for key, value in src_dict.items():
            parsed = parse_tags(value)

            if not parsed or "normal" in parsed:
                normal_keys.append(key)

        row["present"] = ", ".join(str(key) for key in normal_keys)

        # Next, check for all other tags
        for tag in sorted(all_tags):
            if tag == "normal":
                continue  # already handled

            keys_with_this_tag: List[int] = []
            for key, value in src_dict.items():
                if tag in parse_tags(value):
                    keys_with_this_tag.append(key)

            row[tag] = ", ".join(str(k) for k in sorted(keys_with_this_tag))

        rows.append(row)

    df = pd.DataFrame(rows)

    priority_cols = ["source", "missing"]
    used_columns = [column for column in priority_cols] + ["normal", "present"]
    remaining_cols = [tag for tag in all_tags if tag not in used_columns]

    final_columns = [col for col in priority_cols if col in df.columns] + remaining_cols
    df = df.reindex(columns=final_columns)

    df = df.rename(columns={"df": "dental filling", "rcf": "root canal filling"})

    df.columns = [col.capitalize() for col in df.columns]

    with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Overview", index=False)

        worksheet: openpyxl.worksheet.worksheet.Worksheet = writer.book["Overview"]

        for column in worksheet.columns:
            max_length = 0
            for cell in column:
                cell_value = "" if cell.value is None else str(cell.value)
                max_length = max(max_length, len(cell_value))

            # Remove some width to not have too much white space
            # adjusted_width = max_length - 25
            adjusted_width = max_length + 5

            column_letter = get_column_letter(column[0].column)
            worksheet.column_dimensions[column_letter].width = adjusted_width

    # rewind so Streamlit can read the buffer from start
    excel_buffer.seek(0)
    # Copy the logic from your `excel_button()` here but write to excel_buffer instead of triggering download
    # NOTE: Extract only the inner logic that produces `buffer`, skip `st.download_button`
    # For brevity, here we assume excel_buffer is already filled

    # --- Generate PDF ---
    manual_teeth = getattr(st.session_state, 'manual_teeth', {})

    top_row = list(reversed(range(11, 19))) + list(range(21, 29))
    bottom_row = list(reversed(range(41, 49))) + list(range(31, 39))

    # ID
    stored_id = st.session_state.get("profile_number")
    patient_id = stored_id if stored_id else "Unknown"

    # Name
    stored_first_name = st.session_state.get("first_name")
    stored_last_name = st.session_state.get("last_name")
    if stored_first_name and stored_last_name:
        patient_name = f"{stored_first_name} {stored_last_name}"
    else:
        patient_name = "Unknown"

    # Consultation date
    stored_scandate = st.session_state.get("consultation_date")
    if stored_scandate:
        scandate_str = stored_scandate.strftime("%Y-%m-%d") if stored_scandate else ""
    else:
        scandate_str = "Unknown"

    # Age
    stored_birthdate = st.session_state.get("birthdate")
    if stored_birthdate:
        birthdate = stored_birthdate
    else:
        birthdate = "Unknown"

    if stored_birthdate and stored_scandate:
        age = stored_scandate.year - birthdate.year
        if (stored_scandate.month, stored_scandate.day) < (birthdate.month, birthdate.day):
            age -= 1
        age = str(age)
    else:
        age = "Unknown"

    # Gender
    stored_gender = st.session_state.get("gender")
    gender = stored_gender if stored_gender else "Unknown"

    manual_image_bytes = st.session_state["manual_image_bytes"]

    pdf_bytes = create_pdf_professional(
        patient_id=patient_id,
        patient_name=patient_name,
        scan_date=scandate_str,
        birth_date=birthdate,
        age=age,
        gender=gender,
        pano_bytes=manual_image_bytes,
        manual_teeth=manual_teeth,
        top_row=top_row,
        bottom_row=bottom_row,
    )

    # --- Create ZIP ---
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zf:
        zf.writestr("DentalExcel.xlsx", excel_buffer.getvalue())
        zf.writestr("Radiology_Report.pdf", pdf_bytes)

    zip_buffer.seek(0)
    latest_id = st.session_state.get("profile_number")
    st.download_button(
        label="📦 Download Report & Excel (ZIP)",
        data=zip_buffer,
        file_name=f"patient_{latest_id}.zip",
        mime="application/zip",
    )