import pytest

from backend.app.db.init_db import initialize_database


@pytest.fixture(scope="session", autouse=True)
def initialize_test_database():
    """Create the code-first SQLite schema and demo data before API tests."""
    initialize_database()
    yield
