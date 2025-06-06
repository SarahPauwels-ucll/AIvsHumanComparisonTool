import streamlit as st
import subprocess
import json

st.set_page_config(page_title="Belgian eID Login")
st.title("Login with Belgian eID")

if st.button("Read eID Card"):
    try:
        # Run eidreader with subprocess
        result = subprocess.run(["eidreader"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("test")
            output = result.stdout.strip()
            print(output)
            try:
                data = json.loads(output)
                if data.get("success"):
                    full_name = f"{data.get('firstnames', '')} {data.get('surname', '')}"
                    national_number = data.get("national_number", "N/A")
                    st.success("eID read successfully!")
                    st.markdown(f"**Name:** {full_name}")
                    st.markdown(f"**National Number:** {national_number}")
                    st.session_state["eid_data"] = data
                else:
                    st.error(" eID read failed: " + data.get("message", "Unknown error"))
            except json.JSONDecodeError:
                st.error("Could not parse eIDreader output as JSON.")
                st.text(output)
        else:
            st.error("eidreader returned an error.")
            st.text(result.stderr)
    
    except FileNotFoundError:
        st.error("'eidreader' command not found. Make sure it is installed and in PATH.")
    except subprocess.TimeoutExpired:
        st.error("eidreader timed out. Is a card inserted?")
