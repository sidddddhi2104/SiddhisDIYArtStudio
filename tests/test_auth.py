"""Tests for login, register, logout, and admin login."""


def test_login_get_shows_form(client):
    resp = client.get('/login')
    assert resp.status_code == 200


def test_login_with_admin_credentials_redirects_to_admin(client):
    resp = client.post('/login', data={'email': 'admin', 'password': 'admin123'})
    assert resp.status_code == 302
    assert '/admin' in resp.headers['Location']


def test_login_with_valid_user_credentials_succeeds(client, mock_db, mock_cursor):
    # (id, name, email, password) as returned by SELECT * FROM users
    mock_cursor.fetchone.return_value = (1, 'Test User', 'test@test.com', 'pass123')
    resp = client.post('/login', data={'email': 'test@test.com', 'password': 'pass123'})
    assert resp.status_code == 302
    assert resp.headers['Location'] == '/'


def test_login_with_invalid_credentials_redirects_back(client, mock_db, mock_cursor):
    mock_cursor.fetchone.return_value = None
    resp = client.post('/login', data={'email': 'wrong@test.com', 'password': 'wrong'})
    assert resp.status_code == 302
    assert '/login' in resp.headers['Location']


def test_register_get_shows_form(client):
    resp = client.get('/register')
    assert resp.status_code == 200


def test_register_new_user_succeeds(client, mock_db, mock_cursor):
    mock_cursor.fetchone.return_value = None  # no existing user with that email
    resp = client.post('/register', data={
        'name': 'New User', 'email': 'new@test.com', 'password': 'pass'
    })
    assert resp.status_code == 302
    assert '/login' in resp.headers['Location']


def test_register_duplicate_email_is_rejected(client, mock_db, mock_cursor):
    mock_cursor.fetchone.return_value = (1, 'Existing', 'dup@test.com', 'pass')
    resp = client.post('/register', data={
        'name': 'New User', 'email': 'dup@test.com', 'password': 'pass'
    })
    assert resp.status_code == 302
    assert '/register' in resp.headers['Location']


def test_logout_clears_session_and_redirects(client):
    resp = client.get('/logout')
    assert resp.status_code == 302
    assert '/welcome' in resp.headers['Location']


def test_admin_login_get_shows_form(client):
    resp = client.get('/admin-login')
    assert resp.status_code == 200


def test_admin_login_post_success(client):
    resp = client.post('/admin-login', data={'username': 'admin', 'password': 'admin123'})
    assert resp.status_code == 302
    assert '/admin' in resp.headers['Location']


def test_admin_login_post_failure(client):
    resp = client.post('/admin-login', data={'username': 'wrong', 'password': 'wrong'})
    assert resp.status_code == 302
    assert '/admin-login' in resp.headers['Location']
