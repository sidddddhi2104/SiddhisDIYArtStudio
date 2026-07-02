"""
Shared pytest fixtures for testing app.py.

The database and Razorpay client are mocked, so these tests run fast and
do NOT need a real MySQL server or real Razorpay credentials.

Place this `tests/` folder in the same directory as your app.py, then run:
    pytest tests/ -v
"""

import os
import sys
from unittest.mock import MagicMock, patch

import pytest

# Make sure app.py (one directory up from tests/) is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Provide dummy env vars in case .env isn't loaded during test collection
os.environ.setdefault('RAZORPAY_KEY_ID', 'test_key_id')
os.environ.setdefault('RAZORPAY_KEY_SECRET', 'test_key_secret')
os.environ.setdefault('SECRET_KEY', 'test_secret_key')

import app as flask_app_module  # noqa: E402


@pytest.fixture
def app():
    flask_app_module.app.config.update(TESTING=True)
    # Each test run starts with a clean in-memory ORDERS dict
    flask_app_module.ORDERS.clear()
    yield flask_app_module.app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def mock_cursor():
    """A cursor whose fetchone/fetchall you configure per-test."""
    cursor = MagicMock()
    cursor.fetchone.return_value = None
    cursor.fetchall.return_value = []
    return cursor


@pytest.fixture
def mock_conn(mock_cursor):
    conn = MagicMock()
    conn.cursor.return_value = mock_cursor
    conn.is_connected.return_value = True
    return conn


@pytest.fixture
def mock_db(mock_conn):
    """Patches app.get_db_connection so no real MySQL connection is made."""
    with patch('app.get_db_connection', return_value=mock_conn):
        yield mock_conn


def login_user(client, user_id=1, user_name='Test User'):
    """Simulate a logged-in customer session."""
    with client.session_transaction() as sess:
        sess['user_id'] = user_id
        sess['user_name'] = user_name


def login_admin(client):
    """Simulate a logged-in admin session."""
    with client.session_transaction() as sess:
        sess['admin'] = True
