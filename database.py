import sqlite3
from contact import Contact


class Database:
    """Encapsulates all SQLite operations. 
    This is the sole point of contact between the project and the database file.
    """

    def __init__(self) -> None:
        self._db_path = "contacts.db"
        self._conn: sqlite3.Connection = sqlite3.connect(self._db_path)
        self._cursor = self._conn.cursor()
        self._connected: bool = True
        self._index_cols: tuple[str, ...] = ("first_name", "last_name", "email")

        self._init_modes()
        self._init_table()

    def _init_modes(self):
        with self._conn:
            self._conn.execute("PRAGMA journal_mode = WAL;")
            self._conn.execute("PRAGMA synchronous = NORMAL;")

    def _init_table(self) -> None:
        with self._conn:
            self._cursor.execute("""
                CREATE TABLE IF NOT EXISTS Contacts (
                    id INTEGER PRIMARY KEY,
                    first_name TEXT,
                    last_name TEXT,
                    phone TEXT,
                    email TEXT
                );
            """)
            for col in self._index_cols:
                query = f"CREATE INDEX IF NOT EXISTS idx_contacts_{col} ON Contacts({col});"
                self._cursor.execute(query)

    def insert_contact(self, first: str, last: str, phone: str, email: str) -> Contact:
        if not self._is_connected():
            raise sqlite3.ProgrammingError("Cannot execute query: Database is disconnected.")

        with self._conn:
            self._cursor.execute(
                """
                INSERT INTO Contacts (first_name, last_name, phone, email) 
                VALUES (?, ?, ?, ?)
                """, 
                (first, last, phone, email)
            )
            generated_id = self._cursor.lastrowid

        return Contact(
            id=generated_id,
            first_name=first,
            last_name=last,
            phone=phone,
            email=email
        )

    def fetch_all(self) -> list[Contact]:
        """Reads every row, returns as Contact objects, ordered by id ascending."""
        if not self._is_connected():
            return []

        self._cursor.execute(
            "SELECT id, first_name, last_name, phone, email FROM Contacts ORDER BY id ASC;"
        )
        rows = self._cursor.fetchall()

        return [
            Contact(
                id=row[0],
                first_name=row[1],
                last_name=row[2],
                phone=row[3],
                email=row[4]
            )
            for row in rows
        ]

    def delete_contacts(self, ids: list[int | None]) -> None:
        """Bulk deletes in one transaction, filtered by id."""
        if not ids or not self._is_connected():
            return

        placeholders = ",".join("?" for _ in ids)
        query = f"DELETE FROM Contacts WHERE id IN ({placeholders});"

        with self._conn:
            self._cursor.execute(query, ids)

    def close(self) -> None:
        """Properly close the database connection."""
        if self._conn and self._connected:
            self._cursor.close()
            self._conn.close()
            self._connected = False

    def _is_connected(self) -> bool:
        """Verifies that the database connection is alive and active."""
        return bool(self._connected)
