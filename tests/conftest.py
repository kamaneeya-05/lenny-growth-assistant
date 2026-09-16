"""
Pytest configuration and global fixtures.
Initializes test database and prepares fixtures.
"""

import pytest
from backend.app.db.database import init_db, engine, Base


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Ensure database schema is created before tests run."""
    init_db()
    yield
