"""Tests for the profile page and the account-details edit form."""

from conftest import login_user


def test_profile_requires_login(client):
    resp = client.get('/profile')
    assert resp.status_code == 302
    assert '/login' in resp.headers['Location']


def test_profile_shows_user_and_orders(client, mock_db, mock_cursor):
    login_user(client, user_id=1)
    mock_cursor.fetchone.return_value = {
        'id': 1, 'name': 'Test User', 'email': 't@t.com',
        'phone': '9999999999', 'address': '123 Test St'
    }
    mock_cursor.fetchall.return_value = []
    resp = client.get('/profile')
    assert resp.status_code == 200


def test_update_account_requires_login(client):
    resp = client.post('/update_account', data={
        'name': 'A', 'email': 'a@a.com', 'phone': '1', 'address': 'x'
    })
    assert resp.status_code == 302
    assert '/login' in resp.headers['Location']


def test_update_account_saves_and_redirects_to_profile(client, mock_db, mock_cursor):
    login_user(client, user_id=1)
    resp = client.post('/update_account', data={
        'name': 'Updated Name', 'email': 'updated@test.com',
        'phone': '9998887777', 'address': 'New Address'
    })
    assert resp.status_code == 302
    assert '/profile' in resp.headers['Location']
    mock_cursor.execute.assert_called_once()
    args, _ = mock_cursor.execute.call_args
    assert 'UPDATE users' in args[0]
    assert args[1] == ('Updated Name', 'updated@test.com', '9998887777', 'New Address', 1)
