from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QTableView, QMessageBox, QAbstractItemView, QHeaderView
from PySide6.QtCore import Signal, Qt


class ContactListPanel(QWidget):
    delete_requested = Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)

        # Main Layout Setup
        self.outer_layout = QVBoxLayout(self)

        # Build UI Components
        self._setup_header()
        self._setup_table()
        self._setup_buttons()

    def _setup_header(self):
        topic = QLabel("Contacts")
        topic.setObjectName("topic")
        topic.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.outer_layout.addWidget(topic)

    def _setup_table(self):
        self.table = QTableView()
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.outer_layout.addWidget(self.table)

    def _setup_buttons(self):
        self.delete_btn = QPushButton("Delete")
        self.delete_btn.setObjectName("deleteBtn")
        self.outer_layout.addWidget(self.delete_btn)
        
        # Signal connection
        self.delete_btn.clicked.connect(self._on_delete_clicked)


    def _on_delete_clicked(self):
        rows = [idx.row() for idx in self.table.selectionModel().selectedRows()]
        if len(rows) < 0:
            QMessageBox.warning(self, "Nothing selected", "Pick a contact first.")
            return
        
        self.delete_requested.emit(rows)

    def set_model(self, model) -> None:
        self.table.setModel(model)