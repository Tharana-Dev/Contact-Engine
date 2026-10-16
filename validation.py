from PySide6.QtCore import QRegularExpression

regex_patterns = {
    "first_name": r"[\p{L}\s'-]*",
    "last_name": r"[\p{L}\s'-]*",
    "email": r"[\p{L}\p{N}@._%+\-]*",
    "phone": r"[\d\s+\-().]*",
    "email_on_submit": r"^[\p{L}\p{N}._%+\-]+@[\p{L}\p{N}.\-]+\.[\p{L}]{2,}$",
    "phone_on_submit": r"^[+]?[\d\s\-().]{7,20}$"
}


def is_valid_email(email_text:str)->bool:
    email_pattern = regex_patterns.get(
            'email_on_submit', r'^[\p{L}\p{N}._%+\-]+@[\p{L}\p{N}.\-]+\.[\p{L}]{2,}$')
    email_re = QRegularExpression(email_pattern)
    email_match = email_re.match(email_text)

    return email_match.hasMatch()

def is_valid_phone(phone_text:str)->bool:
        phone_pattern = regex_patterns.get(
            'phone_on_submit', r'^[+]?[\d\s\-().]{7,20}$')
        phone_re = QRegularExpression(phone_pattern)
        phone_match = phone_re.match(phone_text)

        return phone_match.hasMatch()