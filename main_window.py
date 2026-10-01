from model import ContactBook
from input_panel import InputPanel
from list_panel import ContactListPanel

from PySide6.QtWidgets import QMainWindow, QDockWidget, QMessageBox, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QKeySequence

from pathlib import Path


class MainWindow(QMainWindow):
    def __init__(self, book: ContactBook, data_path:Path):
        super().__init__()
        self.book = book
        self.input_panel = InputPanel()
        self.contact_list = ContactListPanel()
        self.data_path = data_path

        self.contacts_num = QLabel(f"Contacts: {len(self.book.contacts)}")
        self.contacts_num.setObjectName("counterLabel")

        self._build_actions()
        self._init_ui()
        self._build_dock()
        self._build_menu_bar()
        self._build_status_bar()
        self.contact_list.refresh(self.book.contacts)

        self._wire_signals()

    def _build_actions(self):
        self.new_action = QAction("Add New Contact", self)
        self.new_action.setShortcut(QKeySequence("Ctrl+N"))
        self.new_action.triggered.connect(self._on_create_new_triggered)
        self.new_action.setStatusTip("Create a new contact.")

        self.close_action = QAction("Exit", self)
        self.close_action.setShortcuts([
            QKeySequence(QKeySequence.StandardKey.Quit), 
            QKeySequence("Ctrl+Q")
        ])
        self.close_action.triggered.connect(self.close)
        self.close_action.setStatusTip("Close the app")

        self.act_about = QAction("About", self)
        self.act_about.triggered.connect(self._show_about)
        self.act_about.setStatusTip("See app details")

    def _init_ui(self):
        self.setWindowTitle("Contact Engine")
        self.setMinimumSize(900,800)
        self.setCentralWidget(self.contact_list)

    def _build_dock(self):
        self.form_dock = QDockWidget("Add Contact", self)
        self.form_dock.setWidget(self.input_panel)
        self.addDockWidget(Qt.DockWidgetArea.TopDockWidgetArea, self.form_dock)

    def _wire_signals(self):
        self.input_panel.contact_added.connect(self._add_contact)
        self.contact_list.delete_requested.connect(self._delete_contact)

    def _build_menu_bar(self):
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("File")
        file_menu.addAction(self.new_action)
        file_menu.addSeparator()
        file_menu.addAction(self.close_action)

        view_menu = menu_bar.addMenu("View")
        view_menu.addAction(self.form_dock.toggleViewAction())

        help_menu = menu_bar.addMenu("Help")
        help_menu.addAction(self.act_about)

    def _build_status_bar(self):
        status_bar = self.statusBar()
        status_bar.addPermanentWidget(self.contacts_num)

    def _show_about(self):
        QMessageBox.about(self, "About", "My Phone Book\n  Version 0.3")
    
    def _on_create_new_triggered(self):
        self.form_dock.show()
        self.input_panel.first_name.setFocus()

    def _after_mutation(self, status_message: str, error_context: str) -> None:
        self.contact_list.refresh(self.book.contacts)
        self.contacts_num.setText(f"Contacts: {len(self.book.contacts)}")
        self.statusBar().showMessage(status_message, 3000)
        try:
            self.book.save(self.data_path)
        except OSError as e:
            QMessageBox.warning(self, "Save failed", f"{error_context}:\n{e}")

    def _add_contact(self, first, last, phone, email):
        self.book.add(first, last, phone, email)
        self._after_mutation("Contact added", "Couldn't save after adding")

    def _delete_contact(self, rows):
        for row in sorted(rows, reverse=True):
            self.book.remove(row)
        self._after_mutation("Contact(s) deleted", "Couldn't save after deleting")