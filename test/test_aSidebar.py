from streamlit.testing.v1 import AppTest
import pytest


import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from components.sidebar import load_sidebar

def test_sidebar_loads_correctly():
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
    assert logout_button.label in ["Log out", "Log in as professional"]
