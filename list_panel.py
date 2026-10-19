from PySide6.QtWidgets import QWidget, QStackedLayout, QLineEdit, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QTableView, QMessageBox, QAbstractItemView, QHeaderView
from PySide6.QtCore import Signal, Qt, QTimer


class ContactListPanel(QWidget):
    delete_requested = Signal(list)
    edit_requested = Signal(int) 

    def __init__(self, parent=None):
        super().__init__(parent)

        # Main Layout Setup
        self.outer_layout = QVBoxLayout(self)
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.setInterval(200)

        self.model = None
        self.stacked_layout = QStackedLayout()
        
        # Build UI Components
        self._setup_header()
        self._setup_search_bar()
        self._setup_table()
        self._setup_empty_state()
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

        self.stacked_layout.addWidget(self.table)
        self.outer_layout.addLayout(self.stacked_layout)

    def _setup_empty_state(self):
        empty_widget = QWidget()
        empty_layout = QVBoxLayout(empty_widget)
        empty_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_label = QLabel("No contacts yet.")
        empty_label.setObjectName("emptyStateLabel") # so you can style it in QSS
        empty_layout.addWidget(empty_label)
        self.stacked_layout.addWidget(empty_widget)
        
    def _setup_buttons(self):
        button_row = QHBoxLayout()
        self.update_btn = QPushButton("Update")
        self.update_btn.setObjectName("updateBtn") # We'll style this later
        self.update_btn.setEnabled(False)  

        self.delete_btn = QPushButton("Delete")
        self.delete_btn.setObjectName("deleteBtn")

        button_row.addWidget(self.update_btn)
        button_row.addWidget(self.delete_btn)

        self.outer_layout.addLayout(button_row)

        # Signal connection
        self.delete_btn.clicked.connect(self._on_delete_clicked)
        self.update_btn.clicked.connect(self._on_update_clicked)

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

        self.table.selectionModel().selectionChanged.connect(self._on_selection_changed)
        
        # NOW the model exists. Safe to connect.
        self.model.rowsInserted.connect(self.update_layout_state)
        self.model.rowsRemoved.connect(self.update_layout_state)
        self.model.modelReset.connect(self.update_layout_state)
        
        self.update_layout_state()

    def _on_selection_changed(self, selected,deselected):
        rows = self.table.selectionModel().selectedRows()
        self.update_btn.setEnabled(len(rows) == 1)

    def _on_search_timeout(self):
        if self.model is None:
            return

        text = self.search_bar.text()
        self.model.search(text)

    def _on_update_clicked(self):
        # The button is only enabled when exactly 1 row is selected,
        # but defensive check is always good.
        rows = self.table.selectionModel().selectedRows()
        if len(rows) == 1:
            row_index = rows[0].row()
            self.edit_requested.emit(row_index)

    def update_layout_state(self, *args):
        """Switches the active card based on row count."""
        if self.model.rowCount() == 0:
            self.stacked_layout.setCurrentIndex(1)
            self.update_btn.setEnabled(False) # disable button when empty
            self.delete_btn.setEnabled(False)
        else:
            self.stacked_layout.setCurrentIndex(0)
            self.delete_btn.setEnabled(True)