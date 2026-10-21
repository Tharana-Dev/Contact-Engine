import pytest
from PySide6.QtCore import Qt, QModelIndex
from database import Database
from dataclasses import replace
from table_model import ContactModel
from contact import Contact

@pytest.fixture
def model(qtbot):
    db = Database(":memory:")
    model = ContactModel(db)
    return model

def test_initial_state(model):
    assert model.rowCount() == 0
    assert model.columnCount() == 4

def test_add_contact(qtbot, model):
    with qtbot.waitSignal(model.rowsInserted, timeout=1000) as blocker:
        model.add_contact("Ada", "Lovelace", "555", "ada@x.com")

    assert model.rowCount() == 1

    assert model.index(0, 0).data() == "Ada"
    assert model.index(0, 1).data() == "Lovelace"
    assert model.index(0, 2).data() == "555"
    assert model.index(0, 3).data() == "ada@x.com"

def test_update_contact_emits_data_changed(qtbot, model):
    model.add_contact("Ada", "Lovelace", "555", "ada@x.com")
    
    # We need the contact object to update it
    contact = model.contacts[0]
    
    with qtbot.waitSignal(model.dataChanged, timeout=1000) as blocker:
        model.update_contact(0, replace(contact, first_name="Augusta"))

    top_left_signal_index = blocker.args[0]
    assert top_left_signal_index.row() == 0
    assert top_left_signal_index.column() == 0 

    assert model.index(0, 0).data() == "Augusta"
    assert model.index(0, 1).data() == "Lovelace"

def test_remove_contact(qtbot, model):
    model.add_contact("Ada", "Lovelace", "555", "ada@x.com")
    model.add_contact("Adam", "Smith", "222", "adam@x.com")
    model.add_contact("John", "Doe", "111", "john@x.com")
    # 2. Use qtbot.waitSignal(model.rowsRemoved)
    with qtbot.waitSignal(model.rowsRemoved, timeout=1000) as blocker:
        model.remove_contacts([1])

    assert model.rowCount() == 2
    assert model.columnCount() == 4

    assert model.contacts[1] == Contact(first_name='John', last_name='Doe', phone='111', email='john@x.com', id=3) #index has changed id is auto assigned pk

def test_data_roles(model):
    model.add_contact("Ada", "Lovelace", "555", "ada@x.com")
    index = model.index(0, 0)

    assert model.data(index, Qt.ItemDataRole.DisplayRole) == "Ada"

    # Unhandled roles (like background color or tooltips) must return None safely
    assert model.data(index, Qt.ItemDataRole.BackgroundRole) is None
    assert model.data(index, Qt.ItemDataRole.ToolTipRole) is None


def test_invalid_index_handling(model):
    model.add_contact("Ada", "Lovelace", "555", "ada@x.com")
    
    # An invalid index should return None safely when reading data
    assert model.data(QModelIndex(), Qt.ItemDataRole.DisplayRole) is None
    
    # Requesting a row or column that is out of bounds should return None gracefully
    invalid_index = model.index(5, 5) 
    assert model.data(invalid_index, Qt.ItemDataRole.DisplayRole) is None

def test_header_data(model):
    # Verify your horizontal headers return the correct column names
    assert model.headerData(0, Qt.Orientation.Horizontal, Qt.ItemDataRole.DisplayRole) == "First Name"
    assert model.headerData(1, Qt.Orientation.Horizontal, Qt.ItemDataRole.DisplayRole) == "Last Name"

def test_add_contact_persists_to_database(model):
    model.add_contact("Ada", "Lovelace", "555", "ada@x.com")
    
    # Query your database utility directly to prove it committed the row
    all_db_contacts = model.db.fetch_all() 
    assert len(all_db_contacts) == 1
    assert all_db_contacts[0].first_name == "Ada"

def test_remove_multiple_contacts(qtbot, model):
    model.add_contact("Ada", "Lovelace", "555", "ada@x.com")    # Row 0
    model.add_contact("Adam", "Smith", "222", "adam@x.com")     # Row 1
    model.add_contact("John", "Doe", "111", "john@x.com")       # Row 2
    
    # deleting Row 0 and Row 2 at the same time
    with qtbot.waitSignal(model.rowsRemoved, timeout=1000):
        model.remove_contacts([0, 2])
        
    assert model.rowCount() == 1
    assert model.contacts[0].first_name == "Adam"
