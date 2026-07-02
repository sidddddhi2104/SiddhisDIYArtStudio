"""Tests for small utility/debug routes."""

from unittest.mock import patch


def test_testdb_reports_success(client, mock_db, mock_cursor):
    mock_cursor.fetchone.return_value = (1,)
    resp = client.get('/testdb')
    assert resp.status_code == 200
    assert b'CONNECTED' in resp.data


def test_testdb_reports_failure_when_no_connection(client):
    with patch('app.get_db_connection', return_value=None):
        resp = client.get('/testdb')
    assert resp.status_code == 200
    assert b'FAILED' in resp.data


def test_debug_razorpay_returns_key_status(client):
    resp = client.get('/debug-razorpay')
    assert resp.status_code == 200
    assert 'key_id' in resp.get_json()
