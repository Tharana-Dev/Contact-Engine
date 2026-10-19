import pytest
from PySide6.QtCore import Qt
from input_panel import InputPanel

@pytest.fixture
def panel(qtbot):
    """Fixture to create the panel for each test."""
    panel = InputPanel()
    qtbot.addWidget(panel)
    return panel

def test_empty_form_does_not_emit(panel, qtbot):
    assert panel.first_name_error.isHidden()
    assert panel.last_name_error.isHidden()
    assert panel.email_error.isHidden()
    assert panel.phone_error.isHidden()

    #Click once and ensure the success signal is NOT emitted
    with qtbot.assertNotEmitted(panel.contact_added):
        qtbot.mouseClick(panel.add_btn, Qt.MouseButton.LeftButton)

    # 3. Allow Qt to process the internal state update
    qtbot.wait(10)

    # 4. Assert that they are no longer hidden
    assert not panel.first_name_error.isHidden()
    assert not panel.last_name_error.isHidden()
    assert not panel.email_error.isHidden()
    assert not panel.phone_error.isHidden()

    assert panel.first_name_error.text() == "Required"
    assert panel.last_name_error.text() == "Required"
    assert panel.email_error.text() == "Invalid email"
    assert panel.phone_error.text() == "Invalid phone"


@pytest.mark.parametrize(
    "first, last, phone, email, expected_errors",
    [
        # Scenario 1: Empty First Name
        ("", "Lovelace", "555-0001", "ada@example.com", {"first": "Required"}),
        
        # Scenario 2: Empty Last Name
        ("Ada", "", "555-0001", "ada@example.com", {"last": "Required"}),
        
        # Scenario 3: Invalid Phone
        ("Ada", "Lovelace", "abc-123", "ada@example.com", {"phone": "Invalid phone"}),
        
        # Scenario 4: Invalid Email
        ("Ada", "Lovelace", "555-0001", "not-an-email", {"email": "Invalid email"}),
    ]
)
def test_individual_field_errors(panel, qtbot, first, last, phone, email, expected_errors):
    # Fill out the form fields
    if first: qtbot.keyClicks(panel.first_name, first)
    if last: qtbot.keyClicks(panel.last_name, last)
    if phone: qtbot.keyClicks(panel.phone, phone)
    if email: qtbot.keyClicks(panel.email, email)
    
    # Click button and ensure no signal emits
    with qtbot.assertNotEmitted(panel.contact_added):
        qtbot.mouseClick(panel.add_btn, Qt.MouseButton.LeftButton)
    
    qtbot.wait(10)
    
    # Dynamically assert hidden/visible states based on our expected_errors dictionary
    assert panel.first_name_error.isHidden() == ("first" not in expected_errors)
    assert panel.last_name_error.isHidden() == ("last" not in expected_errors)
    assert panel.phone_error.isHidden() == ("phone" not in expected_errors)
    assert panel.email_error.isHidden() == ("email" not in expected_errors)
    
    # Check the text for fields that are supposed to have errors
    if "first" in expected_errors: assert panel.first_name_error.text() == expected_errors["first"]
    if "last" in expected_errors: assert panel.last_name_error.text() == expected_errors["last"]
    if "phone" in expected_errors: assert panel.phone_error.text() == expected_errors["phone"]
    if "email" in expected_errors: assert panel.email_error.text() == expected_errors["email"]


def test_valid_form_emits_signal(panel, qtbot):
    qtbot.keyClicks(panel.first_name, "Ada")
    qtbot.keyClicks(panel.last_name, "Lovelace")
    qtbot.keyClicks(panel.phone, "555-0001")
    qtbot.keyClicks(panel.email, "ada@x.com")

    with qtbot.waitSignal(panel.contact_added, timeout=1000) as blocker:
        qtbot.mouseClick(panel.add_btn, Qt.MouseButton.LeftButton)
    assert blocker.args == ["Ada", "Lovelace", "555-0001", "ada@x.com"]

    assert panel.last_name_error.isHidden()
    assert panel.phone_error.isHidden()
    assert panel.email_error.isHidden()
    assert panel.first_name_error.isHidden()

    assert panel.first_name.text() == ""
    assert panel.last_name.text() == ""
    assert panel.phone.text() == ""
    assert panel.email.text() == ""

def test_form_clears_on_reset_clicked(panel, qtbot):
    # 1. Fill the form with sample data
    qtbot.keyClicks(panel.first_name, "Ada")
    qtbot.keyClicks(panel.last_name, "Lovelace")
    qtbot.keyClicks(panel.phone, "555-0001")
    qtbot.keyClicks(panel.email, "ada@example.com")
    
    qtbot.mouseClick(panel.reset_btn, Qt.MouseButton.LeftButton)
    qtbot.wait(10)

    # 4. Assert that all text input fields are completely empty
    assert panel.first_name.text() == ""
    assert panel.last_name.text() == ""
    assert panel.phone.text() == ""
    assert panel.email.text() == ""

    # 5. Assert that all error labels are hidden as well
    assert panel.first_name_error.isHidden()
    assert panel.last_name_error.isHidden()
    assert panel.phone_error.isHidden()
    assert panel.email_error.isHidden()

def test_full_user_workflow(panel, qtbot):
    with qtbot.assertNotEmitted(panel.contact_added):
        qtbot.mouseClick(panel.add_btn, Qt.MouseButton.LeftButton)

    qtbot.wait(10)

    assert not panel.first_name_error.isHidden()
    assert panel.first_name_error.text() == "Required"

    qtbot.mouseClick(panel.reset_btn, Qt.MouseButton.LeftButton)
    qtbot.wait(10)

    assert panel.first_name_error.isHidden()
    assert panel.first_name.text() == ""

    qtbot.keyClicks(panel.first_name, "Grace")
    qtbot.keyClicks(panel.last_name, "Hopper")
    qtbot.keyClicks(panel.phone, "555-1947")
    qtbot.keyClicks(panel.email, "grace-at-navy")

    with qtbot.assertNotEmitted(panel.contact_added):
        qtbot.mouseClick(panel.add_btn, Qt.MouseButton.LeftButton)
    qtbot.wait(10)

    assert panel.first_name_error.isHidden()
    assert not panel.email_error.isHidden()
    assert panel.email_error.text() == "Invalid email"

    panel.email.clear()
    qtbot.keyClicks(panel.email, "grace@navy.mil")

    with qtbot.waitSignal(panel.contact_added, timeout=1000) as blocker:
        qtbot.mouseClick(panel.add_btn, Qt.MouseButton.LeftButton)
    qtbot.wait(10)
    
    # Verify signal payload & that fields auto-cleared on success
    assert blocker.args == ["Grace", "Hopper", "555-1947", "grace@navy.mil"]
    assert panel.first_name.text() == ""
    assert panel.email_error.isHidden()