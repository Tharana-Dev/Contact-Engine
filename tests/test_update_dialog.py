import pytest
from PySide6.QtWidgets import QDialog
from PySide6.QtCore import Qt
from dataclasses import replace
from contact_dialog import ContactDialog
from contact import Contact

@pytest.fixture
def dialog(qtbot):
    c = Contact(
        first_name="Ada",
        last_name="Lovelace",
        email="ada@x.com",
        phone="555-0001"
    )
    dialog = ContactDialog(c)
    return dialog

@pytest.mark.parametrize(
    "widget_attr, expected_text",
    [
        ("first_name_input", "Ada"),
        ("last_name_input", "Lovelace"),
        ("phone_input", "555-0001"),
        ("email_input", "ada@x.com"),
    ]
)
def test_prefilling_worked(dialog, qtbot, widget_attr, expected_text):
    dialog.resize(600, 400)
    dialog.show()
    qtbot.wait(20)

    widget = getattr(dialog, widget_attr)
    assert widget.text() == expected_text


@pytest.mark.parametrize(
    "field_to_modify, new_value, error_label_attr, expected_error_msg",
    [
        ("first_name_input", "", "first_name_error", "First name cannot be empty."),
        ("email_input", "invalid-email-format", "email_error", "Invalid email address."),
    ]
)
def test_invalid_dialog_updates_keep_dialog_open(
    dialog, qtbot, field_to_modify, new_value, error_label_attr, expected_error_msg
):
    dialog.resize(600, 400)
    dialog.show()
    qtbot.wait(20)

    # Grab the input layout target component
    input_widget = getattr(dialog, field_to_modify)
    input_widget.clear()
    if new_value:
        qtbot.keyClicks(input_widget, new_value)
        
    qtbot.mouseClick(dialog.save_button, Qt.MouseButton.LeftButton)
    qtbot.wait(10)

    assert dialog.result() != QDialog.DialogCode.Accepted
    assert dialog.isVisible()

    # Verify error label tracking matches text
    error_label = getattr(dialog, error_label_attr)
    assert not error_label.isHidden()
    assert error_label.text() == expected_error_msg


def test_valid_dialog_submission_returns_new_data(dialog, qtbot):
    dialog.resize(600, 400)
    dialog.show()
    qtbot.wait(20)

    dialog.first_name_input.clear()
    qtbot.keyClicks(dialog.first_name_input, "Margaret")

    dialog.last_name_input.clear()
    qtbot.keyClicks(dialog.last_name_input, "Hamilton")

    dialog.phone_input.clear()
    qtbot.keyClicks(dialog.phone_input, "555-1969")

    dialog.email_input.clear()
    qtbot.keyClicks(dialog.email_input, "margaret@nasa.gov")

    qtbot.mouseClick(dialog.save_button, Qt.MouseButton.LeftButton)
    qtbot.wait(10)

    assert dialog.result() == QDialog.DialogCode.Accepted
    assert not dialog.isVisible()

    expected_data_tuple = ("Margaret", "Hamilton", "555-1969", "margaret@nasa.gov")
    assert dialog.get_data() == expected_data_tuple

def test_end_to_end_dialogbox(dialog, qtbot):
    dialog.resize(600, 400)
    dialog.show()
    qtbot.wait(20)

    # we will assume user has successfully got upto updating a contact and the dialogbox is opened corectly by the user

    # =========================================================================
    # STEP 1: Verify current pre-filled data is completely visible to the user
    # =========================================================================
    assert dialog.first_name_input.text() == "Ada"
    assert dialog.last_name_input.text() == "Lovelace"
    assert dialog.phone_input.text() == "555-0001"
    assert dialog.email_input.text() == "ada@x.com"

    # =========================================================================
    # STEP 2: Simulate user making validation mistakes (Validation checks)
    # =========================================================================
    # Clear first name and click update
    dialog.first_name_input.clear()
    qtbot.mouseClick(dialog.save_button, Qt.MouseButton.LeftButton)
    qtbot.wait(10)
    
    # Dialog must stay open, and error must fire
    assert dialog.result() != QDialog.DialogCode.Accepted
    assert not dialog.first_name_error.isHidden()
    assert dialog.first_name_error.text() == "First name cannot be empty."

    # Fix the first name, but type an invalid email layout
    qtbot.keyClicks(dialog.first_name_input, "Margaret")
    dialog.email_input.clear()
    qtbot.keyClicks(dialog.email_input, "margaret-nasa")
    
    qtbot.mouseClick(dialog.save_button, Qt.MouseButton.LeftButton)
    qtbot.wait(10)
    
    # First name error should clear, email error should show up
    assert dialog.first_name_error.isHidden()
    assert not dialog.email_error.isHidden()
    assert dialog.email_error.text() == "Invalid email address."

    # =========================================================================
    # STEP 3: User corrects everything and submits valid modifications
    # =========================================================================
    # Clear the old data text boxes and type all new pristine data parameters
    dialog.last_name_input.clear()
    qtbot.keyClicks(dialog.last_name_input, "Hamilton")
    
    dialog.phone_input.clear()
    qtbot.keyClicks(dialog.phone_input, "555-1969")
    
    dialog.email_input.clear()
    qtbot.keyClicks(dialog.email_input, "margaret@nasa.gov")

    # Click update to save confirmed changes
    qtbot.mouseClick(dialog.save_button, Qt.MouseButton.LeftButton)
    qtbot.wait(10)

    # Final Verification: Dialog successfully accepted changes and closed down
    assert dialog.result() == QDialog.DialogCode.Accepted
    assert not dialog.isVisible()

    # The payload tuple data matches our expected entries perfectly
    expected_data_tuple = ("Margaret", "Hamilton", "555-1969", "margaret@nasa.gov")
    assert dialog.get_data() == expected_data_tuple