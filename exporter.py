import csv
import json
from typing import Any
from contact import Contact

class Exporter:
    def __init__(self, contacts: list[Contact]) -> None:
        self.contacts: list[Contact] = contacts

    def _sanitize_csv(self, value: Any) -> str:
        """Prevents CSV Formula Injection (CWE-1236) in Excel/Sheets."""
        if value is None:
            return ""
        val_str = str(value)
        # If the string starts with a formula trigger, prefix with a single quote
        if val_str.startswith(('=', '+', '-', '@')):
            return f"'{val_str}"
        return val_str

    def _escape_vcard(self, value: Any) -> str:
        """Escapes special vCard characters (backslash, semicolon, comma, newline)."""
        if value is None:
            return ""
        val_str = str(value)
        # Order matters: escape the backslash FIRST, otherwise we double-escape
        # the backslashes we are about to add.
        val_str = val_str.replace('\\', '\\\\')
        val_str = val_str.replace(';', '\\;')
        val_str = val_str.replace(',', '\\,')
        val_str = val_str.replace('\n', '\\n')
        return val_str

    def write_to_csv(self, path: str) -> None:
        with open(path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["first_name", "last_name", "phone", "email"])

            for c in self.contacts:
                writer.writerow([
                    self._sanitize_csv(getattr(c, "first_name")),
                    self._sanitize_csv(getattr(c, "last_name")),
                    self._sanitize_csv(getattr(c, 'phone')),
                    self._sanitize_csv(getattr(c, 'email'))
                ])

    def write_to_json(self, path: str) -> None:
        with open(path, 'w', encoding='utf-8') as f:
            f.write("[\n")
            for i, c in enumerate(self.contacts):
                obj = {
                    'first_name': getattr(c, "first_name"),
                    'last_name': getattr(c, "last_name"),
                    'phone': getattr(c, "phone"),
                    'email': getattr(c, "email")
                }
                # ensure_ascii=False keeps accented characters as-is instead of escaping them to \u00ed
                f.write(json.dumps(obj, ensure_ascii=False, indent=2))
                if i < len(self.contacts) - 1:
                    f.write(",")
                f.write("\n")
            f.write("]\n")

    def write_to_vcard(self, path: str) -> None:
        with open(path, 'w', encoding='utf-8') as f:
            for c in self.contacts:
                # Extract and escape values once
                first = self._escape_vcard(getattr(c, 'first_name'))
                last = self._escape_vcard(getattr(c, 'last_name'))
                phone = self._escape_vcard(getattr(c, 'phone'))
                email = self._escape_vcard(getattr(c, 'email'))

                f.write("BEGIN:VCARD\n")
                f.write("VERSION:3.0\n")
                f.write(f"N:{last};{first};;;\n")
                f.write(f"FN:{first} {last}\n")
                f.write(f"TEL;TYPE=CELL:{phone}\n")
                f.write(f"EMAIL:{email}\n")
                f.write("END:VCARD\n")