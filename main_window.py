from model import ContactBook
from input_panel import InputPanel
from list_panel import ContactListPanel

from PySide6.QtWidgets import QMainWindow, QDockWidget
from PySide6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self,book:ContactBook):
        super().__init__()
        self.book = book
        self.data_panel = InputPanel()
        self.contact_list = ContactListPanel()

        self.init_ui()
        self.build_dock()

        self.contact_list.refresh(self.book.contacts)

        self.wire_signals()
        
    def init_ui(self):
        self.setWindowTitle("My Phone Book")
        self.setFixedSize(500, 400)
        self.setCentralWidget(self.contact_list)

    def build_dock(self):
        self.form_dock = QDockWidget("Add Contact", self)
        self.form_dock.setWidget(self.data_panel)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.form_dock)

    def _add_contact(self, first, last, phone, email):
        self.book.add(first, last, phone, email)
        self.contact_list.refresh(self.book.contacts)

    def _delete_contact(self, rows):
        for row in sorted(rows, reverse=True):
            self.book.remove(row)
        self.contact_list.refresh(self.book.contacts)

    def wire_signals(self):
        self.data_panel.contact_added.connect(self._add_contact)
        self.contact_list.delete_requested.connect(self._delete_contact)
