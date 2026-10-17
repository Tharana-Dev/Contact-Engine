import sys
from PySide6.QtWidgets import (
    QApplication, QDialog, QLabel, QLineEdit, 
    QPushButton, QVBoxLayout, QHBoxLayout, QFormLayout, QMainWindow
)
from PySide6.QtCore import Qt
from contact import Contact
from validation import is_valid_email, is_valid_phone

class ContactDialog(QDialog):

    def __init__(self, contact:Contact, parent=None):
        super().__init__(parent)
        self.contact = contact
        self.setWindowTitle("Edit Contact")
        self.setFixedSize(350, 320)

        self._init_ui()
        self.save_button.clicked.connect(self._on_save_clicked)
        self.cancel_button.clicked.connect(self.reject) 

    def _init_ui(self):
        # 1. Main container layout
        main_container = QVBoxLayout()
        # Add generous padding around the inside window edges
        main_container.setContentsMargins(20, 20, 20, 20)
        main_container.setSpacing(15)  # Spacing between the form and buttons group

        # 2. Form layout for fields
        form_layout = QFormLayout()
        form_layout.setSpacing(8)       # Clean, tight spacing between adjacent fields
        # Center-align labels vertically relative to their inputs
        form_layout.setFormAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        # --- First Name Field & Error ---
        self.first_name_input = QLineEdit(self.contact.first_name)
        self.first_name_error = QLabel("First name cannot be empty.")
        first_name_layout = self._create_field_layout(self.first_name_input, self.first_name_error)
        form_layout.addRow("First Name:", first_name_layout)

        # --- Last Name Field & Error ---
        self.last_name_input = QLineEdit(self.contact.last_name)
        self.last_name_error = QLabel("Last name cannot be empty.")
        last_name_layout = self._create_field_layout(self.last_name_input, self.last_name_error)
        form_layout.addRow("Last Name:", last_name_layout)

        # --- Phone Field & Error ---
        self.phone_input = QLineEdit(self.contact.phone)
        self.phone_error = QLabel("Invalid phone number format.")
        phone_layout = self._create_field_layout(self.phone_input, self.phone_error)
        form_layout.addRow("Phone:", phone_layout)

        # --- Email Field & Error ---
        self.email_input = QLineEdit(self.contact.email)
        self.email_error = QLabel("Invalid email address.")
        email_layout = self._create_field_layout(self.email_input, self.email_error)
        form_layout.addRow("Email:", email_layout)

        # --- Buttons ---
        self.save_button = QPushButton("Save")
        self.save_button.setObjectName("primaryBtn")
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setObjectName("smallBtn") 
        
        button_container = QHBoxLayout()
        button_container.setSpacing(10)
        # Push the buttons to the right side of the window natively
        button_container.setAlignment(Qt.AlignmentFlag.AlignRight)
        button_container.addWidget(self.save_button)
        button_container.addWidget(self.cancel_button)

        # --- Layout Assembly with Native Qt Alignment Fixes ---
        # Force the form to stick to the top instead of expanding vertically
        main_container.addLayout(form_layout)
        
        # Add a flexible spacer to swallow empty vertical space, keeping elements compact
        main_container.addStretch() 
        
        main_container.addLayout(button_container)
        self.setLayout(main_container)

    def _create_field_layout(self, input_field: QLineEdit, error_label: QLabel) -> QVBoxLayout:
        """Helper to style inputs, error labels, and stack them neatly."""
        layout = QVBoxLayout()
        layout.setSpacing(2)
        
        # 1. NATIVE SIZE FIX: Make the input field taller (e.g., 30px or 35px)
        input_field.setMinimumHeight(32) 
        
        # 2. OPTIONAL NATIVE FIX: Slightly larger font automatically scales the field box nicely
        font = input_field.font()
        font.setPointSize(11) # Increase base text size slightly
        input_field.setFont(font)

        # Style the error label
        error_label.setObjectName("errorLabel") # Let the QSS handle the color
        error_label.setVisible(False)
        
        layout.addWidget(input_field)
        layout.addWidget(error_label)
        return layout

    def get_data(self) -> tuple[str, str, str, str]:
        return (
            self.first_name_input.text().strip(),
            self.last_name_input.text().strip(),
            self.phone_input.text().strip(),
            self.email_input.text().strip()
        )

    def _on_save_clicked(self):
        first, last, phone, email = self.get_data()
        
        # Clear previous errors
        self._set_error(self.first_name_input, self.first_name_error, False)
        self._set_error(self.last_name_input, self.last_name_error, False)
        self._set_error(self.phone_input, self.phone_error, False)
        self._set_error(self.email_input, self.email_error, False)

        has_errors = False

        if not first:
            self._set_error(self.first_name_input, self.first_name_error, True)
            has_errors = True
        if not last:
            self._set_error(self.last_name_input, self.last_name_error, True)
            has_errors = True
        if not is_valid_phone(phone):
            self._set_error(self.phone_input, self.phone_error, True)
            has_errors = True
        if not is_valid_email(email):
            self._set_error(self.email_input, self.email_error, True)
            has_errors = True

        if not has_errors:
            self.accept()  # This is the "return True" of a QDialog

    def _set_error(self, field, label, is_error):
        field.setProperty("error", is_error)
        field.style().unpolish(field)
        field.style().polish(field)
        label.setVisible(is_error)

# --- Dummy Object Replacement for Demo Testing ---
class Contact_test:
    def __init__(self) -> None:
        self.id  =  1
        self.first_name = "Ada"
        self.last_name = "Lovelace"
        self.phone = "555-8888"
        self.email = "ada@ex.com"


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 1. Create your dummy data
    contact = Contact_test()
    
    # 2. Instantiate the dialog independently (no QMainWindow wrapper needed)
    dialog = ContactDialog(contact=contact)
    
    # 3. Open it as a modal dialog window
    dialog.exec()
