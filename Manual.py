import streamlit as st
from st_pages import Page, add_page_title
from sidebar import load_sidebar

st.set_page_config(page_title="AI vs. Human analysis: A smart comparison tool",
                   layout="wide")

load_sidebar()

st.title("Welcome to the manualy page!")
st.write("Here we can manual alter the chart.")

