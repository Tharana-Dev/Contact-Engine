import pytest

from database import Database


@pytest.fixture
def db(tmp_path):
    """A fresh, isolated database per test. No teardown, no cross-test pollution."""
    path = tmp_path / "test.db"
    database = Database(str(path))
    yield database
    database.close()
