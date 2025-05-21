import io
import pandas as pd
import streamlit as st


def excel_button():
    manual_data = st.session_state.get("manual_teeth", {})
    ai_data = st.session_state.get("ai_teeth", {})
    # TODO: implement this, as final teeth currently doesn't exist.
    final_data = st.session_state.get("final_teeth", {})

    df_manual = pd.DataFrame(manual_data)
    df_ai = pd.DataFrame(ai_data)

    dicts = [manual_data, ai_data]

    # Find all unique values (automatically handle any number of columns)
    all_values = set()
    for d in dicts:
        for v in d.values():
            all_values.update(val.strip() for val in v.split(','))

    # Assign every key (tooth number) to the values it contains
    result = {}
    for val in all_values:
        keys_with_val = []
        for d in dicts:
            keys_with_val += [k for k, v in d.items() if val in [x.strip() for x in v.split(',')]]
        keys_with_val = sorted(set(keys_with_val))
        result[val] = ', '.join(map(str, keys_with_val))

    df_combined = pd.DataFrame([result])

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df_combined.to_excel(writer, sheet_name='Combined', index=False)
    buffer.seek(0)

    st.download_button(
        label="Download Excel file",
        data=buffer,
        file_name="data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )