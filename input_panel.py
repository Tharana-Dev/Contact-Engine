from PySide6.QtWidgets import QWidget,QLabel, QPushButton, QHBoxLayout, QVBoxLayout, QLineEdit
from PySide6.QtCore import Signal, Qt, QRegularExpression
from PySide6.QtGui import QRegularExpressionValidator

import sys
from PySide6.QtWidgets import QApplication

class InputPanel(QWidget):
    contact_added = Signal(str, str, str, str) # (first_name, last_name, phone, email)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.regex_patterns = {
            "first_name": r"[\p{L}\s'-]*",
            "last_name": r"[\p{L}\s'-]*",
            "email": r"[\p{L}\p{N}@._%+\-]*",
            "phone": r"[\d\s+\-().]*",
            "email_on_submit": r"^[\p{L}\p{N}._%+\-]+@[\p{L}\p{N}.\-]+\.[\p{L}]{2,}$",
            "phone_on_submit": r"^[+]?[\d\s\-().]{7,20}$"
        }

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
        self.first_name, self.first_name_error = self._create_input_row_with_validator(
            "First Name: ",
            "Enter Your First Name Here",
            self.regex_patterns.get("first_name", r"[\p{L}\s'\-]*")
        )

        self.last_name, self.last_name_error = self._create_input_row_with_validator(
            "Last Name: ",
            "Enter Your Last Name Here",
            self.regex_patterns.get("last_name", r"[\p{L}\s'\-]*")
        )

        self.email, self.email_error = self._create_input_row_with_validator(
            "Email: ",
            "Enter Your Email Here",
            self.regex_patterns.get('email', r"[\p{L}\p{N}@._%+\-]*")
        )

        self.phone, self.phone_error = self._create_input_row_with_validator(
            "Phone: ",
            "Enter Your Contact Number Here",
            self.regex_patterns.get('phone', r"[\d\s+\-().]*")
        )

        self.first_name.textChanged.connect(
            lambda _, f=self.first_name, l=self.first_name_error: self._set_error(f, l, False))
        self.last_name.textChanged.connect(
            lambda _, f=self.last_name, l=self.last_name_error: self._set_error(f, l, False))
        self.email.textChanged.connect(
            lambda _, f=self.email, l=self.email_error: self._set_error(f, l, False))
        self.phone.textChanged.connect(
            lambda _, f=self.phone, l=self.phone_error: self._set_error(f, l, False))

    def _create_input_row_with_validator(self, label_text, placeholder_text, pattern):
        """Helper method to construct a single form row."""
        row_layout = QHBoxLayout()
        row_layout.setSpacing(12)
        self.input_layout.addLayout(row_layout)

        label = QLabel(label_text)
        label.setAlignment(Qt.AlignmentFlag.AlignLeft |
                           Qt.AlignmentFlag.AlignVCenter)
        label.setObjectName("fieldLabel")

        line_edit = QLineEdit()
        line_edit.setObjectName("input")
        line_edit.setPlaceholderText(placeholder_text)
        line_edit.setValidator(QRegularExpressionValidator(
            QRegularExpression(pattern), self))


        error_label = QLabel("")
        error_label.setObjectName('errorLabel')
        error_label.setVisible(False)

        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)   # kill default padding
        left_layout.setSpacing(2)

        left_layout.addWidget(label)
        left_layout.addWidget(error_label)

        row_layout.addWidget(left_widget, 4)
        row_layout.addWidget(line_edit, 6)

        return (line_edit, error_label)

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
        first_name_text = self.first_name.text()
        last_name_text = self.last_name.text()
        email_text = self.email.text()
        phone_text = self.phone.text()

        email_pattern = self.regex_patterns.get(
            'email_on_submit', r'^[\p{L}\p{N}._%+\-]+@[\p{L}\p{N}.\-]+\.[\p{L}]{2,}$')
        email_re = QRegularExpression(email_pattern)
        email_match = email_re.match(email_text)

        phone_pattern = self.regex_patterns.get(
            'phone_on_submit', r'^[+]?[\d\s\-().]{7,20}$')
        phone_re = QRegularExpression(phone_pattern)
        phone_match = phone_re.match(phone_text)

        self._set_error(self.first_name, self.first_name_error, False)
        self._set_error(self.last_name, self.last_name_error, False)
        self._set_error(self.email, self.email_error, False)
        self._set_error(self.phone, self.phone_error, False)

        has_errors = False

        if not first_name_text:
            self._set_error(self.first_name,
                            self.first_name_error, True, "Required")
            has_errors = True
        if not last_name_text:
            self._set_error(
                self.last_name, self.last_name_error, True, "Required")
            has_errors = True
        if not email_match.hasMatch():
            self._set_error(self.email, self.email_error,
                            True, "Invalid email")
            has_errors = True
        if not phone_match.hasMatch():
            self._set_error(self.phone, self.phone_error,
                            True, "Invalid phone")
            has_errors = True

        if  has_errors:
                return

        self.contact_added.emit(first_name_text, last_name_text, phone_text, email_text)
        self._clear_fields()

        

    def _clear_fields(self):
        self.first_name.clear()
        self.last_name.clear()
        self.email.clear()
        self.phone.clear()

    def _set_error(self, field, label, is_error, message=""):
        field.setProperty("error", is_error)
        field.style().unpolish(field)
        field.style().polish(field)

        if is_error:
            label.setText(message)
            label.setVisible(True)
        else:
            label.setVisible(False)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = InputPanel()
    window.setFixedSize(500, 400)
    window.show()
    sys.exit(app.exec())