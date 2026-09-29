from model import ContactBook
from input_panel import InputPanel
from list_panel import ContactListPanel

from PySide6.QtWidgets import QMainWindow, QDockWidget, QMessageBox, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QKeySequence


class MainWindow(QMainWindow):
    def __init__(self, book: ContactBook):
        super().__init__()
        self.book = book
        self.data_panel = InputPanel()
        self.contact_list = ContactListPanel()

        self.contacts_num = QLabel(f"Contacts: {len(self.book.contacts)}")

        self._actions()
        self._init_ui()
        self._build_dock()
        self._build_menu_bar()
        self._build_status_bar()
        self.contact_list.refresh(self.book.contacts)

        self._wire_signals()

    def _init_ui(self):
        self.setWindowTitle("My Phone Book")
        self.setMinimumHeight(800)
        self.setMinimumWidth(900)
        self.setCentralWidget(self.contact_list)

    def _build_dock(self):
        self.form_dock = QDockWidget("Add Contact", self)
        self.form_dock.setWidget(self.data_panel)
        self.addDockWidget(Qt.DockWidgetArea.TopDockWidgetArea, self.form_dock)

    def _add_contact(self, first, last, phone, email):
        self.book.add(first, last, phone, email)
        self.contact_list.refresh(self.book.contacts)
        self.contacts_num.setText(f"Contacts: {len(self.book.contacts)}")
        self.statusBar().showMessage("Contact Added",3000)

    def _delete_contact(self, rows):
        for row in sorted(rows, reverse=True):
            self.book.remove(row)
        self.contact_list.refresh(self.book.contacts)
        self.contacts_num.setText(f"Contacts: {len(self.book.contacts)}")
        self.statusBar().showMessage("Contact(s) Deleted",3000)

    def _wire_signals(self):
        self.data_panel.contact_added.connect(self._add_contact)
        self.contact_list.delete_requested.connect(self._delete_contact)

    def _actions(self):
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
        self.close_action.setStatusTip("Close The App")

        self.act_about = QAction("About", self)
        self.act_about.triggered.connect(self._show_about)
        self.act_about.setStatusTip("See app details")

    def _build_menu_bar(self):
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("File")
        file_menu.addAction(self.new_action)
        file_menu.addSeparator()
        file_menu.addAction(self.close_action)

        help_menu = menu_bar.addMenu("Help")
        help_menu.addAction(self.act_about)

    def _build_status_bar(self):
        status_bar = self.statusBar()
        status_bar.addPermanentWidget(self.contacts_num)

    def _show_about(self):
        QMessageBox.about(self, "About", "My Phone Book\n  Version 0.2")
    
    def _on_create_new_triggered(self):
        self.form_dock.show()
        self.data_panel.first_name.setFocus()
