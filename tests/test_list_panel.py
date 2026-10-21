import pytest
from PySide6.QtCore import Qt, QModelIndex
from database import Database
from dataclasses import replace
from table_model import ContactModel
from list_panel import ContactListPanel

@pytest.fixture
def panel_and_model(qtbot):
    db = Database(":memory:")
    model = ContactModel(db)
    panel = ContactListPanel()
    panel.set_model(model)
    # Return both components together as a tuple
    return panel, model


def test_empty_state(panel_and_model):
    panel, _ = panel_and_model
    assert panel.stacked_layout.currentIndex() == 1
    assert not panel.update_btn.isEnabled()
    assert not panel.delete_btn.isEnabled()


def test_after_adding_a_contact(panel_and_model, qtbot):
    panel, model = panel_and_model
    
    model.add_contact("Ada", "Lovelace", "555", "ada@x.com")
    qtbot.wait(10)

    assert panel.stacked_layout.currentIndex() == 0
    assert not panel.update_btn.isEnabled()
    assert panel.delete_btn.isEnabled()
    
def test_search_unmaching_result(panel_and_model, qtbot):
    panel, model = panel_and_model

    model.add_contact("Ada", "Lovelace", "555", "ada@x.com")
    qtbot.wait(10)

    qtbot.keyClicks(panel.search_bar, "adam")
    qtbot.wait(250)

    assert panel.stacked_layout.currentIndex() == 1
    assert not panel.update_btn.isEnabled()
    assert not panel.delete_btn.isEnabled()


def test_select_row_and_click_update(panel_and_model, qtbot):
    panel, model = panel_and_model

    model.add_contact("Ada", "Lovelace", "555", "ada@x.com")     # Row 0
    model.add_contact("Adam", "Smith", "222", "adam@x.com")     # Row 1
    model.add_contact("John", "Doe", "111", "john@x.com")       # Row 2
    
    # 2. Programmatically select Row 2
    selection_model = panel.table.selectionModel()
    row_2_index = model.index(2, 0)
    selection_model.select(row_2_index, selection_model.SelectionFlag.Select | selection_model.SelectionFlag.Rows)
    
    with qtbot.waitSignal(panel.edit_requested, timeout=1000) as blocker:
        qtbot.mouseClick(panel.update_btn, Qt.MouseButton.LeftButton)
        
    assert blocker.args[0] == 2

def test_select_multiple_rows_and_click_delete(panel_and_model, qtbot):
    panel, model = panel_and_model
    
    model.add_contact("Ada", "Lovelace", "555", "ada@x.com")
    model.add_contact("Adam", "Smith", "222", "adam@x.com")
    model.add_contact("John", "Doe", "111", "john@x.com")
    
    selection_model = panel.table.selectionModel()
    selection_model.select(model.index(0, 0), selection_model.SelectionFlag.Select | selection_model.SelectionFlag.Rows)
    selection_model.select(model.index(1, 0), selection_model.SelectionFlag.Select | selection_model.SelectionFlag.Rows)
    
    with qtbot.waitSignal(panel.delete_requested, timeout=1000) as blocker:
        qtbot.mouseClick(panel.delete_btn, Qt.MouseButton.LeftButton)
        
    assert blocker.args[0] == [0, 1]


def test_debounce_search(panel_and_model, qtbot):
    panel, model = panel_and_model

    assert panel.stacked_layout.currentIndex() == 1

    model.add_contact("Ada", "Lovelace", "555", "ada@x.com")
    model.add_contact("Adam", "Smith", "222", "adam@x.com")
    model.add_contact("John", "Doe", "111", "john@x.com")
    qtbot.wait(10)

    assert panel.stacked_layout.currentIndex() == 0
    assert panel.delete_btn.isEnabled()

    assert panel.table.model().rowCount() == 3

    qtbot.keyClicks(panel.search_bar, "John")
    qtbot.wait(250)

    assert panel.table.model().rowCount() == 1
    assert panel.table.model().index(0, 0).data() == "John"
    assert panel.table.model().index(0, 1).data() == "Doe"    

def test_end_to_end_list_panel(panel_and_model, qtbot):
    panel, model = panel_and_model

    # 1. Start by forcing a physical layout size so selection works seamlessly later
    panel.resize(600, 400)
    panel.show()
    qtbot.wait(20)

    # At the start it should start with empty state since the database is empty
    assert panel.stacked_layout.currentIndex() == 1
    assert not panel.update_btn.isEnabled()
    assert not panel.delete_btn.isEnabled()
 
    # Add initial contacts to see the state change
    model.add_contact("Ada", "Lovelace", "555", "ada@x.com")
    model.add_contact("Adam", "Smith", "222", "adam@x.com")
    model.add_contact("John", "Doe", "111", "john@x.com")
    qtbot.wait(10)

    # Test the state change
    assert panel.stacked_layout.currentIndex() == 0
    assert panel.delete_btn.isEnabled()
    assert not panel.update_btn.isEnabled() # update btn should still be disabled because no contact is selected
    assert panel.table.model().rowCount() == 3

    # --- ACTION: Search a contact ---
    qtbot.keyClicks(panel.search_bar, "John")
    qtbot.wait(250)
    assert panel.table.model().rowCount() == 1
    assert panel.table.model().index(0, 0).data() == "John"
    assert panel.table.model().index(0, 1).data() == "Doe" 

    # --- ACTION: User searches an unmatching contact ---
    panel.search_bar.clear()  # FIX: Clear out "John" before typing "Harry"
    qtbot.keyClicks(panel.search_bar, "Harry")
    qtbot.wait(250)

    assert panel.stacked_layout.currentIndex() == 1
    assert not panel.update_btn.isEnabled()
    assert not panel.delete_btn.isEnabled()

    # --- ACTION: Clear search to bring back all rows for selection testing ---
    panel.search_bar.clear()
    qtbot.wait(250) # Allow debounce timer to reset table row count to 3
    assert panel.table.model().rowCount() == 3

    # --- ACTION: User selects only one contact ---
    view_model = panel.table.model()
    selection_model = panel.table.selectionModel()
    
    # Select Ada (Row 0)
    selection_model.select(
        view_model.index(0, 0), 
        selection_model.SelectionFlag.Select | selection_model.SelectionFlag.Rows
    )
    qtbot.wait(50)

    assert panel.update_btn.isEnabled()
    assert panel.delete_btn.isEnabled()

    # --- ACTION: User selects multiple rows ---
    # Clear the first selection so we start clean
    selection_model.clearSelection()
    qtbot.wait(10)

    # Select both Row 0 (Ada) and Row 1 (Adam)
    selection_model.select(
        view_model.index(0, 0), 
        selection_model.SelectionFlag.Select | selection_model.SelectionFlag.Rows
    )
    selection_model.select(
        view_model.index(1, 0), 
        selection_model.SelectionFlag.Select | selection_model.SelectionFlag.Rows
    )   
    qtbot.wait(50)

    # Update button must disable on multi-selection, but delete stays active!
    assert not panel.update_btn.isEnabled()
    assert panel.delete_btn.isEnabled()
