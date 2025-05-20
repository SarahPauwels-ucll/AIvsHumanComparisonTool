import pytest
from unittest.mock import MagicMock, patch
from datetime import date
from sidebar import load_sidebar


@pytest.fixture
def mock_streamlit():
    with patch("sidebar.st") as mock_st:
        # Mock sidebar methods
        mock_sidebar = MagicMock()
        mock_st.sidebar = mock_sidebar
        mock_st.session_state = {}

        # Default inputs/outputs for sidebar UI elements
        mock_sidebar.text_input.side_effect = lambda label, value="", key=None: value
        mock_sidebar.radio.side_effect = lambda label, options, index=0, key=None: options[
            index]
        mock_sidebar.date_input.side_effect = lambda label, value=None, key=None, min_value=None, max_value=None: value

        yield mock_st


@pytest.fixture
def mock_cookie_controller():
    with patch("sidebar.CookieController") as MockController:
        mock_controller_instance = MagicMock()
        mock_controller_instance.get.side_effect = lambda key: {
            "ProfileNumber": "12345",
            "LastName": "Doe",
            "FirstName": "John",
            "Gender": "Male",
            "birthdate": "2000-01-01",
            "consultation date": "2020-01-01"
        }.get(key, None)
        MockController.return_value = mock_controller_instance
        yield mock_controller_instance


def test_load_sidebar_sets_session_state(mock_streamlit, mock_cookie_controller):
    # Call the function
    load_sidebar()

    # Assertions
    assert mock_streamlit.session_state["profile_number"] == "12345"
    assert mock_streamlit.session_state["last_name"] == "Doe"
    assert mock_streamlit.session_state["first_name"] == "John"
    assert mock_streamlit.session_state["gender"] == "Male"
    assert mock_streamlit.session_state["birthdate"] == date(2000, 1, 1)
    assert mock_streamlit.session_state["consultation date"] == date(
        2020, 1, 1)

    # Check that sidebar UI elements were rendered
    mock_streamlit.sidebar.text_input.assert_any_call(
        "Profile number", value="12345", key="profile_number")
    mock_streamlit.sidebar.radio.assert_called_once()
    mock_streamlit.sidebar.date_input.assert_any_call("Select birthdate", value=date(
        2000, 1, 1), key="birthdate", min_value=date(1900, 1, 1), max_value='today')


def test_invalid_profile_number_error(mock_streamlit, mock_cookie_controller):
    mock_streamlit.sidebar.text_input.side_effect = lambda label, value="", key=None: "abc"

    load_sidebar()

    # Should show an error for non-numeric input
    mock_streamlit.sidebar.error.assert_any_call(
        "Profile number must be a number.")
