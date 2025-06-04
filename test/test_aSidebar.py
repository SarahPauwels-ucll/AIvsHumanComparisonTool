from streamlit.testing.v1 import AppTest
import pytest


import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from components.sidebar import load_sidebar

def test_sidebar_loads_correctly_not_logged_in():
    at = AppTest.from_function(load_sidebar).run()

    # Check that the sidebar title is rendered
    assert at.sidebar.title[0].value == "Dental Chart"

    # Check that the sidebar radio buttons exist for gender and teeth
    gender_radio = at.sidebar.radio[0]
    teeth_radio = at.sidebar.radio[1]

    assert gender_radio.label == "Gender"
    assert teeth_radio.label == "Teeth"

    # Interact with the profile number input
    profile_input = at.sidebar.text_input[0]
    assert profile_input.label== "Profile number"

    # Test birthdate selection
    birthdate_input = at.sidebar.date_input[0]
    consultation_date_input = at.sidebar.date_input[1]
    assert birthdate_input.label == "Select birthdate"
    assert consultation_date_input.label == "Select consultation date"

    # Log out button
    logout_button = at.sidebar.button[-1]
    assert logout_button.label in ["Log in as professional"]

def test_sidebar_loads_correctly_logged_in():
    at = AppTest.from_function(load_sidebar).run()
    at.session_state["Professional"]="True"
    at.run()

    assert at.sidebar.title[0].value == "Menu"
    # Check that the sidebar title is rendered
    assert at.sidebar.title[1].value == "Dental Chart"

    # Check that the sidebar radio buttons exist for gender and teeth
    gender_radio = at.sidebar.radio[0]
    teeth_radio = at.sidebar.radio[1]

    assert gender_radio.label == "Gender"
    assert teeth_radio.label == "Teeth"

    # Interact with the profile number input
    profile_input = at.sidebar.text_input[0]
    assert profile_input.label== "Profile number"

    # Test birthdate selection
    birthdate_input = at.sidebar.date_input[0]
    consultation_date_input = at.sidebar.date_input[1]
    assert birthdate_input.label == "Select birthdate"
    assert consultation_date_input.label == "Select consultation date"

    # Log out button
    logout_button = at.sidebar.button[-1]
    assert logout_button.label in ["Log out"]

def test_sidebar_full_interaction():
    at = AppTest.from_function(load_sidebar).run()

    # Simulate user interaction
    at.radio[0].set_value("Female")  # Gender
    at.radio[1].set_value("Child")   # Teeth
    at.sidebar.text_input[0].set_value("12345")  # Profile number
    at.sidebar.date_input[0].set_value("1990-01-01")  # Birthdate
    at.sidebar.date_input[1].set_value("2025-06-01")  # Consultation date

    # Run the app after interactions
    at.run()

    # Assertions to confirm saved inputs
    assert at.sidebar.radio[0].value == "Female"
    assert at.sidebar.radio[1].value == "Child"
    assert at.sidebar.text_input[0].value == "12345"
    assert str(at.sidebar.date_input[0].value) == "1990-01-01"
    assert str(at.sidebar.date_input[1].value) == "2025-06-01"
    #age calculate correctly
    assert at.sidebar.markdown[0].value == "Age: 35"

