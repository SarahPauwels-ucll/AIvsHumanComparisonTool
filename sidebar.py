import streamlit as st

def load_sidebar(): 
    st.sidebar.title("Dental Chart")
    ProfileNumber = st.sidebar.text_input("Profile number", key="number")
    LastName = st.sidebar.text_input("Last name")
    FirstName = st.sidebar.text_input("First name")
    gender = st.sidebar.radio("Gender", ["Male", "Female"])
    age = st.sidebar.number_input("Select age", step=1, value=30)