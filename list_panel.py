from PySide6.QtWidgets import QWidget, QLineEdit, QVBoxLayout, QLabel, QPushButton, QTableView, QMessageBox, QAbstractItemView, QHeaderView
from PySide6.QtCore import Signal, Qt, QTimer


class ContactListPanel(QWidget):
    delete_requested = Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)

        # Main Layout Setup
        self.outer_layout = QVBoxLayout(self)
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.setInterval(200)

        self.model = None

        # Build UI Components
        self._setup_header()
        self._setup_search_bar()
        self._setup_table()
        self._setup_buttons()

    def _setup_header(self):
        topic = QLabel("Contacts")
        topic.setObjectName("topic")
        topic.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.outer_layout.addWidget(topic)

    def _setup_search_bar(self):
        self.search_bar = QLineEdit()
        self.search_bar.setObjectName("searchBar")
        self.search_bar.setPlaceholderText("Search contacts...")
        self.search_bar.textChanged.connect(self.timer.start)
        self.timer.timeout.connect(self._on_search_timeout)

        self.outer_layout.addWidget(self.search_bar)

    def _setup_table(self):
        self.table = QTableView()
        self.table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(
            QAbstractItemView.SelectionMode.ExtendedSelection)
        self.table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.outer_layout.addWidget(self.table)

    def _setup_buttons(self):
        self.delete_btn = QPushButton("Delete")
        self.delete_btn.setObjectName("deleteBtn")
        self.outer_layout.addWidget(self.delete_btn)

        # Signal connection
        self.delete_btn.clicked.connect(self._on_delete_clicked)

    def _on_delete_clicked(self):
        rows = [idx.row()
                for idx in self.table.selectionModel().selectedRows()]
        if not rows:
            QMessageBox.warning(self, "Nothing selected",
                                "Pick a contact first.")
            return

        self.delete_requested.emit(rows)

    def set_model(self, model) -> None:
        self.model = model
        self.table.setModel(model)

    def _on_search_timeout(self):
        if self.model is None:
            return

        text = self.search_bar.text()
        self.model.search(text)