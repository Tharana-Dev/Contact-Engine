import sys
from pathlib import Path

from database import Database
from PySide6.QtWidgets import QApplication
from main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(Path("style.qss").read_text())
    database = Database()
    window = MainWindow(database)
    window.show()
    app.aboutToQuit.connect(database.close)
    sys.exit(app.exec())


if __name__ == "__main__":
    main() 