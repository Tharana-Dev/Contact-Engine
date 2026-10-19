import sys
from pathlib import Path
import os
from database import Database
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QStandardPaths
from PySide6.QtGui import QIcon
from main_window import MainWindow


#for pyinstaller
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    # Safely checks for _MEIPASS at runtime, defaults to current directory if not found
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    
    return Path(base_path) / relative_path



def main():
    app = QApplication(sys.argv)

    app.setApplicationName("ContactEngine")
    app.setOrganizationName("TharanaDev")

    app.setWindowIcon(QIcon("book.ico"))

    
    app.setStyleSheet(resource_path("style.qss").read_text())

    data_dir = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation)
    Path(data_dir).mkdir(parents=True, exist_ok=True)
    db_path = Path(data_dir) / "contacts.db"

    database = Database(db_path=str(db_path))
    
    window = MainWindow(database)
    window.show()
    app.aboutToQuit.connect(database.close)
    sys.exit(app.exec())


if __name__ == "__main__":
    main() 