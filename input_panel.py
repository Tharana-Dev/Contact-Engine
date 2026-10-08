from PySide6.QtWidgets import QWidget, QMessageBox, QLabel, QPushButton, QHBoxLayout, QVBoxLayout, QLineEdit
from PySide6.QtCore import Signal, Qt

import sys
from PySide6.QtWidgets import QApplication

class InputPanel(QWidget):
    contact_added = Signal(str, str, str, str) # (first_name, last_name, phone, email)

    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Main Layout Setup
        self.outer_layout = QVBoxLayout()
        self.setLayout(self.outer_layout)

        self.content_container = QWidget()
        self.content_container.setMinimumWidth(600)
        self.content_container.setMaximumWidth(700)
        self.outer_layout.addWidget(self.content_container)
        self.outer_layout.setAlignment(self.content_container, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)

        self.content_layout = QVBoxLayout()
        self.content_container.setLayout(self.content_layout)
        
        # Build UI Components
        self._setup_header()
        self._setup_form_fields()
        self._setup_buttons()

    def _setup_header(self):
        topic = QLabel("Data Handling center")
        topic.setObjectName("topic")
        topic.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content_layout.addWidget(topic)

    def _setup_form_fields(self):
        self.input_layout = QVBoxLayout()
        self.content_layout.addLayout(self.input_layout)
        
        # Create fields using the extracted helper method
        self.first_name = self._create_input_row("First Name: ", "Enter Your First Name Here")
        self.last_name = self._create_input_row("Last Name: ", "Enter Your Last Name Here")
        self.email = self._create_input_row("Email: ", "Enter Your Email Here")
        self.phone = self._create_input_row("Phone: ", "Enter Your Contact Number Here")

    def _create_input_row(self, label_text, placeholder_text):
        """Helper method to construct a single form row."""
        row_layout = QHBoxLayout()
        row_layout.setSpacing(12)
        self.input_layout.addLayout(row_layout)

        label = QLabel(label_text)
        label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        label.setObjectName("fieldLabel")

        line_edit = QLineEdit()
        line_edit.setObjectName("input")
        line_edit.setPlaceholderText(placeholder_text)

        row_layout.addWidget(label, 4)
        row_layout.addWidget(line_edit, 6)
        
        return line_edit

    def _setup_buttons(self):
        button_layout = QHBoxLayout()
        self.content_layout.addLayout(button_layout)

        self.add_btn = QPushButton("Add")
        self.add_btn.setObjectName("primaryBtn")
        self.reset_btn = QPushButton("Reset")
        self.reset_btn.setObjectName("smallBtn")

        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.reset_btn)

        # Signal connections
        self.add_btn.clicked.connect(self._on_add_clicked)
        self.reset_btn.clicked.connect(self._clear_fields)

    def _on_add_clicked(self):
        first = self.first_name.text().strip()
        last = self.last_name.text().strip()
        phone = self.phone.text().strip()
        email = self.email.text().strip()

        if not (first and last and phone and email):
            return

        self.contact_added.emit(first, last, phone, email)
        self._clear_fields()

    def _clear_fields(self):
        self.first_name.clear()
        self.last_name.clear()
        self.email.clear()
        self.phone.clear()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = InputPanel()
    window.setFixedSize(500, 400)
    window.show()
    sys.exit(app.exec())