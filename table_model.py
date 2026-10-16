from contact import Contact
from PySide6.QtCore import QAbstractTableModel, QModelIndex, QPersistentModelIndex, Qt
from database import Database

class ContactModel(QAbstractTableModel):

    def __init__(self, db:Database , parent=None):
        super().__init__(parent)
        self.db = db
        self.contacts = self.db.fetch_all()
        self.columns = ('first_name', 'last_name', 'phone', 'email')
        self.headers = ('First Name', 'Last Name', 'Phone', 'Email')

    def rowCount(self, parent:QModelIndex | QPersistentModelIndex = QModelIndex()) -> int:
        if parent.isValid():
            return 0
        return len(self.contacts)

    def columnCount(self, parent: QModelIndex | QPersistentModelIndex = QModelIndex()) -> int:
        if parent.isValid():
            return 0
        return len(self.columns)

    def data(self,index:QModelIndex | QPersistentModelIndex, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        
        if role != Qt.ItemDataRole.DisplayRole:
            return None

        contact = self.contacts[index.row()]
        return getattr(contact, self.columns[index.column()])

    def headerData(self, section: int, orientation: Qt.Orientation, role=Qt.ItemDataRole.DisplayRole):
        if role != Qt.ItemDataRole.DisplayRole:
            return None

        if orientation == Qt.Orientation.Horizontal:
            if 0 <= section < len(self.headers):
                return self.headers[section]

        return None

    def add_contact(self,first:str, last:str, phone:str, email:str) -> Contact:
        res = self.db.insert_contact(first,last,phone,email)
        row = len(self.contacts)
        self.beginInsertRows(QModelIndex(), row, row)
        self.contacts.append(res)
        self.endInsertRows()
        return res

    def remove_contacts(self, rows: list[int]) -> None:
        ids = [self.contacts[r].id for r in rows]
        self.db.delete_contacts(ids)

        for row in sorted(rows, reverse=True):
            self.beginRemoveRows(QModelIndex(), row, row)
            del self.contacts[row]
            self.endRemoveRows()

    def load_all(self) -> None:
        self.beginResetModel()
        self.contacts = self.db.fetch_all()
        self.endResetModel()

    def search(self, query)->None:
        self.beginResetModel()
        self.contacts = self.db.search(query)
        self.endResetModel()

    def update_contact(self, row: int, updated_contact: Contact) -> None:
        """Updates a contact at a specific row, commits it to the database,
        and notifies the attached views to refresh.

        Propagates all database and validation exceptions up to the caller.
        """
        if row < 0 or row >= len(self.contacts):
            raise IndexError("Target row index out of range for the contact list.")

        self.db.update_contact(updated_contact)

        self.contacts[row] = updated_contact

        #Notify the View interface to redraw the updated row.
        top_left = self.index(row, 0)
        bottom_right = self.index(row, len(self.columns) - 1)
        self.dataChanged.emit(top_left, bottom_right, [Qt.ItemDataRole.DisplayRole])
