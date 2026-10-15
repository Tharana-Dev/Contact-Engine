import csv
import json
from contact import Contact

class Exporter:
    def __init__(self, contacts: list[Contact]) -> None:
        self.contacts: list[Contact] = contacts

    def write_to_csv(self, path: str) -> None:
        with open(path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["first_name", "last_name", "phone", "email"])

            for c in self.contacts:
                writer.writerow([getattr(c, "first_name"), getattr(c, "last_name"), getattr(c, 'phone'), getattr(c, 'email')])

    def write_to_json(self, path: str) -> None:
        with open(path, 'w', encoding='utf-8') as f:
            f.write("[\n")
            for i, c in enumerate(self.contacts):
                obj = {
                    'first_name':getattr(c, "first_name"),
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
                f.write("BEGIN:VCARD\n")
                f.write("VERSION:3.0\n")
                f.write(f"N:{getattr(c, 'last_name')};{getattr(c, 'first_name')};;;\n")
                f.write(f"FN:{getattr(c, 'first_name')} {getattr(c, 'last_name')}\n")
                f.write(f"TEL;TYPE=CELL:{getattr(c, 'phone')}\n")
                f.write(f"EMAIL:{getattr(c, 'email')}\n")
                f.write("END:VCARD\n")
