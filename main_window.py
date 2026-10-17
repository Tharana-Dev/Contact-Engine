from input_panel import InputPanel
from list_panel import ContactListPanel
from table_model import ContactModel
from database import Database
from PySide6.QtWidgets import QMainWindow, QDockWidget, QFileDialog, QMessageBox, QLabel, QDialog
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QKeySequence
from exporter import Exporter
from contact_dialog import ContactDialog
from dataclasses import replace

EXPORT_FORMATS = {
    "csv":   ("Export to CSV",   "contacts.csv",   "CSV (*.csv)",   ".csv",   "write_to_csv"),
    "json":  ("Export to JSON",  "contacts.json",  "JSON (*.json)", ".json",  "write_to_json"),
    "vcard": ("Export to vCard", "contacts.vcf",   "vCard (*.vcf)", ".vcf",   "write_to_vcard"),
}

class MainWindow(QMainWindow):
    def __init__(self, database: Database):
        super().__init__()
        self.db = database
        self.input_panel = InputPanel()
        self.contact_list = ContactListPanel()
        self.model = ContactModel(self.db)

        self.contacts_num = QLabel(f"Rows: {self.model.rowCount()}")
        self.contacts_num.setObjectName("counterLabel")

        self._build_actions()
        self._init_ui()
        self._build_dock()
        self._build_menu_bar()
        self._build_status_bar()
        self.contact_list.set_model(self.model)

        self._wire_signals()
        self.model.modelReset.connect(self._update_counter)
        self.contact_list.edit_requested.connect(self._edit_contact)

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

        self.export_csv_action = QAction("CSV", self)
        self.export_csv_action.triggered.connect(lambda: self._export_as("csv"))
        self.export_csv_action.setStatusTip(
            "Export the contacts as a .csv file.")

        self.export_json_action = QAction("JSON", self)
        self.export_json_action.triggered.connect(lambda: self._export_as("json"))
        self.export_json_action.setStatusTip(
            "Export the contacts as a .json file.")

        self.export_vcard_action = QAction("vCard", self)
        self.export_vcard_action.triggered.connect(lambda: self._export_as("vCard"))
        self.export_vcard_action.setStatusTip(
            "Export the contacts as a .vcf file.")

    def _init_ui(self):
        self.setWindowTitle("Contact Engine")
        self.setMinimumSize(900, 800)
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

        export_menu = file_menu.addMenu("Export")
        export_menu.addAction(self.export_csv_action)
        export_menu.addAction(self.export_json_action)
        export_menu.addAction(self.export_vcard_action)

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
        QMessageBox.about(self, "About", "Contact Engine\n  Version 0.6.0")

    def _on_create_new_triggered(self):
        self.form_dock.show()
        self.input_panel.first_name.setFocus()

    def _add_contact(self, first, last, phone, email):
        self.model.add_contact(first, last, phone, email)
        self._update_counter()
        self.statusBar().showMessage("Contact added", 3000)

    def _delete_contact(self, rows):
        self.model.remove_contacts(rows)
        self._update_counter()
        self.statusBar().showMessage("Contact(s) Removed", 3000)

    def _update_counter(self):
        self.contacts_num.setText(f"Rows: {self.model.rowCount()}")

    
    def _export_as(self, fmt):
        export_format = EXPORT_FORMATS.get(fmt,())
        if export_format:
            path, _ = QFileDialog.getSaveFileName(
                self, export_format[0], export_format[1], export_format[2])
            if not path:
                return
            if not path.endswith(export_format[3]):
                path += export_format[3]
            exporter = Exporter(self.model.contacts)
            try:
                getattr(exporter, export_format[4])(path)
                self.statusBar().showMessage(f"Exported {self.model.rowCount()} contacts", 3000)
            except OSError as e:
                QMessageBox.warning(self, "Export failed", str(e))

    def _edit_contact(self, row: int):
        contact = self.model.contacts[row]
        dialog = ContactDialog(contact, self)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            first, last, phone, email = dialog.get_data()
            # Using dataclasses.replace to swap values and create a new frozen Contact
            updated = replace(contact, first_name=first, last_name=last, phone=phone, email=email)
            
            self.model.update_contact(row, updated)
            self.statusBar().showMessage("Contact updated", 3000)