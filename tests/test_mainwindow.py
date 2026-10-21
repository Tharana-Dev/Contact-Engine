import pytest
import os
from pathlib import Path
from unittest.mock import patch
from PySide6.QtWidgets import QFileDialog, QMessageBox, QDialog, QApplication
from PySide6.QtCore import Qt, QSettings, QTimer
from table_model import ContactModel
# App modules
from main_window import MainWindow
from database import Database
from contact import Contact


@pytest.fixture
def isolated_settings(tmp_path):
    QSettings.setPath(
        QSettings.Format.IniFormat,  # storage format
        QSettings.Scope.UserScope,  # scope
        str(tmp_path)
    )
    yield tmp_path

    QSettings.setPath(
        QSettings.Format.IniFormat,
        QSettings.Scope.UserScope,
        ""
    )  # reset


@pytest.fixture
def window(isolated_settings, qtbot):
    db = Database(":memory:")
    window = MainWindow(db)
    window.resize(600, 200)
    window.show()
    qtbot.addWidget(window)
    yield window
    window.close()


def test_initial_state(window, qtbot):
    assert window.windowTitle() == "Contact Engine"
    assert window.input_panel.isEnabled()
    assert window.contact_list.isEnabled()

    assert window.model is not None
    assert isinstance(window.model, ContactModel)
    assert window.contact_list.table.model() is not None

    assert window.contact_list.stacked_layout.currentIndex() == 1


def test_e2e_add_contact(window, qtbot):
    with qtbot.assertNotEmitted(window.input_panel.contact_added):
        qtbot.mouseClick(window.input_panel.add_btn, Qt.MouseButton.LeftButton)

    qtbot.wait(10)

    assert not window.input_panel.first_name_error.isHidden()
    assert window.input_panel.first_name_error.text() == "Required"

    qtbot.mouseClick(window.input_panel.reset_btn, Qt.MouseButton.LeftButton)
    qtbot.wait(10)

    assert window.input_panel.first_name_error.isHidden()
    assert window.input_panel.first_name.text() == ""

    qtbot.keyClicks(window.input_panel.first_name, "Grace")
    qtbot.keyClicks(window.input_panel.last_name, "Hopper")
    qtbot.keyClicks(window.input_panel.phone, "555-1947")
    qtbot.keyClicks(window.input_panel.email, "grace-at-navy")

    with qtbot.assertNotEmitted(window.input_panel.contact_added):
        qtbot.mouseClick(window.input_panel.add_btn, Qt.MouseButton.LeftButton)
    qtbot.wait(10)

    assert window.input_panel.first_name_error.isHidden()
    assert not window.input_panel.email_error.isHidden()
    assert window.input_panel.email_error.text() == "Invalid email"

    window.input_panel.email.clear()
    qtbot.keyClicks(window.input_panel.email, "grace@navy.mil")

    with qtbot.waitSignal(window.input_panel.contact_added, timeout=1000) as blocker:
        qtbot.mouseClick(window.input_panel.add_btn, Qt.MouseButton.LeftButton)
    qtbot.wait(10)

    # Verify signal payload & that fields auto-cleared on success
    assert blocker.args == ["Grace", "Hopper", "555-1947", "grace@navy.mil"]
    assert window.input_panel.first_name.text() == ""
    assert window.input_panel.email_error.isHidden()

    assert window.contacts_num.text() == "Rows: 1"
    assert len(window.db.fetch_all()) == 1
    assert window.contact_list.stacked_layout.currentIndex() == 0

def test_e2e_edit_contact(window, qtbot): 
    window.model.add_contact(first='Ada', last='Lovelace', email='ada@x.com', phone='5555-000') 
    
    # Select the row 
    view_model = window.contact_list.table.model() 
    selection_model = window.contact_list.table.selectionModel() 
    selection_model.select( 
        view_model.index(0, 0), 
        selection_model.SelectionFlag.Select | selection_model.SelectionFlag.Rows 
    ) 
    qtbot.wait(50) 
    
    def interact_with_dialog_cancel(): 
        dialog = QApplication.activeModalWidget() 
        assert dialog.first_name_input.text() == "Ada" 
        dialog.first_name_input.clear() 
        qtbot.keyClicks(dialog.first_name_input, "Augusta") 
        qtbot.mouseClick(dialog.cancel_button, Qt.MouseButton.LeftButton) 
        
    QTimer.singleShot(50, interact_with_dialog_cancel) 
    qtbot.mouseClick(window.contact_list.update_btn, Qt.MouseButton.LeftButton) 
    qtbot.wait(100)  # Increased wait time to ensure the singleShot finishes and dialog closes
    
    assert window.model.contacts[0].first_name == "Ada" 
    
    selection_model.select( 
        view_model.index(0, 0), 
        selection_model.SelectionFlag.Select | selection_model.SelectionFlag.Rows 
    ) 
    qtbot.wait(50) 
    
    def interact_with_dialog_save(): 
        dialog = QApplication.activeModalWidget() 
        assert dialog.last_name_input.text() == "Lovelace" 
        dialog.email_input.clear() 
        qtbot.keyClicks(dialog.email_input, "adaL.123") 
        qtbot.mouseClick(dialog.save_button, Qt.MouseButton.LeftButton) 
        assert not dialog.email_error.isHidden() 
        dialog.email_input.clear() 
        qtbot.keyClicks(dialog.email_input, "adal@example.com") 
        qtbot.mouseClick(dialog.save_button, Qt.MouseButton.LeftButton) 
        
    QTimer.singleShot(50, interact_with_dialog_save)
    qtbot.mouseClick(window.contact_list.update_btn, Qt.MouseButton.LeftButton) 
    qtbot.wait(150)
    
    assert window.model.contacts[0].email == "adal@example.com"

def test_e2e_delete_contact(window, qtbot, mocker):
    # 1. Arrange: Add initial seed data fixture
    window.model.add_contact("Ada", "Lovelace", "555", "ada@x.com")
    qtbot.wait(10)

    # --- PHASE 1: Test warning box behavior with empty selections ---
    mock_exec = mocker.patch.object(QMessageBox, "exec", return_value=0)
    
    # We call the method directly because the button is naturally disabled right now
    window.contact_list._on_delete_clicked()
    mock_exec.assert_called_once()
    
    # --- PHASE 2: Test successful deletion flow ---
    view_model = window.contact_list.table.model()
    selection_model = window.contact_list.table.selectionModel()
    
    # Select the row programmatically
    selection_model.select(
        view_model.index(0, 0), 
        selection_model.SelectionFlag.Select | selection_model.SelectionFlag.Rows
    )
    qtbot.wait(50)  # Give Qt's signal slot synchronization engine a microsecond to enable the button!
    
    # Assert defensively that your UI controller code actually unlocked the button
    assert window.contact_list.delete_btn.isEnabled() is True
    
    # Click the Delete button via qtbot to run the full UI pipeline
    qtbot.mouseClick(window.contact_list.delete_btn, Qt.MouseButton.LeftButton)
    qtbot.wait(50)
    
    # --- PHASE 3: Assert application state variations ---
    assert window.model.rowCount() == 0
    assert len(window.db.fetch_all()) == 0
    assert window.contacts_num.text() == "Rows: 0"
    assert window.contact_list.stacked_layout.currentIndex() == 1

def test_export_csv(window,mocker, tmp_path):
    window.model.add_contact("Ada", "Lovelace", "555", "ada@x.com")
    fake_path = str(tmp_path / "contacts.csv")
    mocker.patch("main_window.QFileDialog.getSaveFileName", return_value=(fake_path, "CSV (*.csv)"))
    window._export_as("csv")
    assert os.path.exists(fake_path)

    with open(fake_path, "r") as f:
        content = f.read()
        assert "Ada" in content

def test_export_json(window,mocker, tmp_path):
    window.model.add_contact("Ada", "Lovelace", "555", "ada@x.com")
    fake_path = str(tmp_path / "contacts.json")
    mocker.patch("main_window.QFileDialog.getSaveFileName", return_value=(fake_path, "JSON (*.json)"))
    window._export_as("json")
    assert os.path.exists(fake_path)
    with open(fake_path, "r") as f:
        content = f.read()
        assert "Ada" in content


def test_export_vcard(window,mocker, tmp_path):
    window.model.add_contact("Ada", "Lovelace", "555", "ada@x.com")
    fake_path = str(tmp_path / "contacts.vcf")
    mocker.patch("main_window.QFileDialog.getSaveFileName", return_value=(fake_path, "vCard (*.vcf)"))
    window._export_as("vcard")
    assert os.path.exists(fake_path)
    with open(fake_path, "r") as f:
        content = f.read()
        assert "Ada" in content

def test_about_dialog(window, mocker):
    # 1. Intercept the whole QMessageBox construction layer inside your module
    mock_box_class = mocker.patch("main_window.QMessageBox")
    
    # 2. Extract a shortcut pointer hook to the generated object instance
    mock_instance = mock_box_class.return_value
    
    # 3. Fire the method trigger execution
    window._show_about()
    
    # 4. ASSERTIONS: Verify the properties assigned to the dialog instance match expectations!
    mock_box_class.assert_called_once_with(window)
    mock_instance.setWindowTitle.assert_called_with("Contact Engine")
    mock_instance.setText.assert_called_with("Version 0.7.3")
    mock_instance.exec.assert_called_once()

def test_window_layout_persistence(window, qtbot, isolated_settings):
    window.resize(950, 850)
    qtbot.wait(50)

    saved_geometry = window.saveGeometry()
    window.close()

    db2 = Database(":memory:")
    window2 = MainWindow(db2)
    qtbot.addWidget(window2)
    
    window2.show()
    qtbot.wait(50)

    #ASSERT: Prove that the restored window's raw geometry configuration
    assert window2.saveGeometry() == saved_geometry
