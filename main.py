import sys
import json
from pathlib import Path

from PySide6.QtWidgets import QApplication, QMessageBox

from model import ContactBook
from main_window import MainWindow

DATA_PATH = Path("contacts.json")


def _save_on_exit(book):
    try:
        book.save(DATA_PATH)
    except OSError as e:
        print(f"Save failed: {e}", file=sys.stderr)

def main():
    app = QApplication(sys.argv)

    book = ContactBook()
    try:
        book.load(DATA_PATH)
    except FileNotFoundError:
        book.save(DATA_PATH)                                     
    except (ValueError, json.JSONDecodeError) as e:
        QMessageBox.warning(None, "Load failed", f"Couldn't load contacts:\n{e}")

    window = MainWindow(book, DATA_PATH)
    window.show()
    app.aboutToQuit.connect(lambda: _save_on_exit(book))
    sys.exit(app.exec())


if __name__ == "__main__":
    main() 