import io
from typing import Dict, List, Set

import openpyxl
import pandas as pd
import streamlit as st
from openpyxl.utils import get_column_letter


def excel_button():

    manual_teeth: Dict[int, str] = st.session_state.get("manual_teeth", {})
    ai_teeth: Dict[int, str] = st.session_state.get("ai_teeth", {})
    final_teeth: Dict[int, str] = st.session_state.get("final_teeth", {})

    print(manual_teeth)

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

    buffer = io.BytesIO()

    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Overview", index=False)

        worksheet: openpyxl.worksheet.worksheet.Worksheet = writer.book["Overview"]

        for column in worksheet.columns:
            max_length = 0
            for cell in column:
                cell_value = "" if cell.value is None else str(cell.value)
                max_length = max(max_length, len(cell_value))

            # Remove some width to not have too much white space
            #adjusted_width = max_length - 25
            adjusted_width = max_length + 5

            column_letter = get_column_letter(column[0].column)
            worksheet.column_dimensions[column_letter].width = adjusted_width

    # rewind so Streamlit can read the buffer from start
    buffer.seek(0)
    st.dataframe(df)
    st.download_button(
        label="Download Excel file",
        data=buffer,
        file_name="dicts_summary.xlsx",
        mime=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
    )
