import streamlit as st
from st_pages import Page, add_page_title

st.set_page_config(page_title="AI vs. Human analysis: A smart comparison tool",
                   layout="wide")


st.markdown(
    """
    <style>
    .sidebar .sidebar-content {
        display: flex;
        flex-direction: column;
        justify-content: flex-end;
        align-items: center;
    }
    </style>
    """,
    unsafe_allow_html=True
)



st.title("Hello Streamlit!")
st.write("Welcome to your first Streamlit app.")

