"""Tests for database.Database - public interface only."""
import sqlite3

from contact import Contact
from database import Database


# --------------------------------------------------------------------- schema

def test_schema_objects_created(tmp_path):
    path = tmp_path / "schema.db"
    database = Database(str(path))
    try:
        conn = sqlite3.connect(str(path))
        try:
            names = {
                row[0]
                for row in conn.execute(
                    "SELECT name FROM sqlite_master WHERE type IN ('table', 'trigger')"
                )
            }
        finally:
            conn.close()
    finally:
        database.close()

    assert "Contacts" in names
    assert "contacts_fts" in names
    assert {"contacts_after_insert", "contacts_after_delete", "contacts_after_update"} <= names


def test_reopening_same_path_is_idempotent(tmp_path):
    path = str(tmp_path / "idempotent.db")
    Database(path).close()
    Database(path).close()


# ---------------------------------------------------------------- basic CRUD

def test_insert_contact_returns_contact_with_id(db):
    contact = db.insert_contact("Ada", "Lovelace", "555-0100", "ada@example.com")
    assert isinstance(contact, Contact)
    assert contact.id is not None
    assert contact.first_name == "Ada"


def test_fetch_all_on_empty_db_returns_empty_list(db):
    assert db.fetch_all() == []


def test_fetch_all_returns_contacts_ordered_by_id(db):
    db.insert_contact("First", "One", "1", "one@example.com")
    db.insert_contact("Second", "Two", "2", "two@example.com")
    db.insert_contact("Third", "Three", "3", "three@example.com")
    contacts = db.fetch_all()
    assert [c.id for c in contacts] == sorted(c.id for c in contacts)
    assert [c.first_name for c in contacts] == ["First", "Second", "Third"]


def test_delete_contacts_removes_row(db):
    keep = db.insert_contact("Keep", "Me", "1", "keep@example.com")
    drop = db.insert_contact("Drop", "Me", "2", "drop@example.com")
    db.delete_contacts([drop.id])
    remaining = db.fetch_all()
    assert [c.id for c in remaining] == [keep.id]


def test_delete_contacts_with_empty_list_is_a_noop(db):
    db.insert_contact("Keep", "Me", "1", "keep@example.com")
    db.delete_contacts([])
    assert len(db.fetch_all()) == 1


# ---------------------------------------------------------------- FTS search

def test_search_matches_first_name_prefix(db):
    db.insert_contact("Adam", "Smith", "1", "adam@example.com")
    db.insert_contact("Zoe", "Jones", "2", "zoe@example.com")
    assert [c.first_name for c in db.search("ad")] == ["Adam"]


def test_search_matches_last_name(db):
    db.insert_contact("Adam", "Smith", "1", "adam@example.com")
    db.insert_contact("Zoe", "Jones", "2", "zoe@example.com")
    assert [c.last_name for c in db.search("smith")] == ["Smith"]


def test_search_matches_email(db):
    db.insert_contact("Adam", "Smith", "1", "adam@gmail.com")
    db.insert_contact("Zoe", "Jones", "2", "zoe@yahoo.com")
    assert [c.email for c in db.search("gmail")] == ["adam@gmail.com"]


def test_search_empty_string_returns_all(db):
    db.insert_contact("Adam", "Smith", "1", "adam@example.com")
    db.insert_contact("Zoe", "Jones", "2", "zoe@example.com")
    assert len(db.search("")) == 2


def test_search_unknown_term_returns_empty(db):
    db.insert_contact("Adam", "Smith", "1", "adam@example.com")
    assert db.search("zzz") == []


# ---------------------------------------------------- FTS <-> Contacts sync

def test_inserted_contact_is_searchable(db):
    db.insert_contact("Zaphod", "Beeblebrox", "555", "zaphod@example.com")
    assert [c.first_name for c in db.search("zaphod")] == ["Zaphod"]


def test_deleted_contact_is_not_searchable(db):
    contact = db.insert_contact("Zaphod", "Beeblebrox", "555", "zaphod@example.com")
    assert db.search("zaphod") != []
    db.delete_contacts([contact.id])
    assert db.search("zaphod") == []


# --------------------------------------------------------------- sanitisation

def test_search_with_apostrophe_does_not_crash(db):
    db.insert_contact("Sean", "O'Brien", "555", "sean@example.com")
    assert isinstance(db.search("O'Brien"), list)


def test_search_with_hyphen_does_not_crash(db):
    db.insert_contact("Anne", "Smith-Jones", "555", "anne@example.com")
    assert isinstance(db.search("a-b"), list)


def test_search_with_only_symbols_returns_all(db):
    db.insert_contact("Adam", "Smith", "1", "adam@example.com")
    assert len(db.search("@#$")) == 1
