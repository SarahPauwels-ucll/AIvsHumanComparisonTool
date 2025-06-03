from streamlit.testing.v1 import AppTest
import streamlit as st


def test_loginpage():
    at = AppTest.from_file("app.py").run()
    assert at.title[0].value == "Login Page"


def test_valid_login(tmp_path):
    at = AppTest.from_file("app.py").run()

    # Enter valid credentials
    at.text_input[0].input("sarah")
    at.text_input[1].input("password")

    # Click login
    at.button[0].click()
    at.run()

    # Check if it redirects to another page
    assert at.session_state["Professional"] is True

def test_invalid_login(tmp_path):
    at = AppTest.from_file("app.py").run()

    # Enter invalid credentials
    at.text_input[0].input("wronguser")
    at.text_input[1].input("wrongpass")

    # Click login
    at.button[0].click()
    at.run()

    # Check for error
    assert at.error[0].value == "Invalid username or password."

def test_continue_as_student(tmp_path):
    at = AppTest.from_file("app.py").run()

    # Click "Continue as Student"
    at.button[1].click()
    at.run()

    # Check session state
    assert at.session_state["Professional"] is False