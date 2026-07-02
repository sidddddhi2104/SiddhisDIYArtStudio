"""Tests for the admin dashboard, product management, and admin-only listing pages."""

import io

from conftest import login_admin


def test_admin_dashboard_requires_login(client):
    resp = client.get('/admin')
    assert resp.status_code == 302
    assert '/login' in resp.headers['Location']


def test_admin_dashboard_loads_when_logged_in(client, mock_db, mock_cursor):
    login_admin(client)
    mock_cursor.fetchall.return_value = []
    resp = client.get('/admin')
    assert resp.status_code == 200


def test_admin_products_requires_login(client):
    resp = client.get('/admin-products')
    assert resp.status_code == 302


def test_admin_products_loads_when_logged_in(client, mock_db, mock_cursor):
    login_admin(client)
    mock_cursor.fetchall.return_value = []
    resp = client.get('/admin-products')
    assert resp.status_code == 200


def test_admin_orders_requires_login(client):
    resp = client.get('/admin-orders')
    assert resp.status_code == 302


def test_admin_orders_loads_when_logged_in(client, mock_db, mock_cursor):
    login_admin(client)
    mock_cursor.fetchall.return_value = []
    resp = client.get('/admin-orders')
    assert resp.status_code == 200


def test_admin_contacts_requires_login(client):
    resp = client.get('/admin-contacts')
    assert resp.status_code == 302


def test_admin_contacts_loads_when_logged_in(client, mock_db, mock_cursor):
    login_admin(client)
    mock_cursor.fetchall.return_value = []
    resp = client.get('/admin-contacts')
    assert resp.status_code == 200


def test_add_product_uploads_and_redirects(client, mock_db, mock_cursor):
    data = {
        'name': 'New Candle',
        'category': 'Candles',
        'price': '299',
        'description': 'A nice candle',
        'image': (io.BytesIO(b'fake image bytes'), 'candle.jpg'),
    }
    resp = client.post('/add-product', data=data, content_type='multipart/form-data')
    assert resp.status_code == 302
    assert '/admin-products' in resp.headers['Location']
    mock_cursor.execute.assert_called_once()


def test_delete_product_redirects_to_admin(client, mock_db, mock_cursor):
    resp = client.get('/delete-product/1')
    assert resp.status_code == 302
    assert '/admin' in resp.headers['Location']


def test_update_product_redirects_to_admin_products(client, mock_db, mock_cursor):
    resp = client.post('/update-product/1', data={
        'name': 'Updated', 'category': 'Cat', 'price': '99', 'description': 'desc'
    })
    assert resp.status_code == 302
    assert '/admin-products' in resp.headers['Location']


def test_edit_product_shows_form(client, mock_db, mock_cursor):
    mock_cursor.fetchone.return_value = (1, 'Candle', 'Decor', 199, 'img.jpg', 'desc')
    resp = client.get('/edit-product/1')
    assert resp.status_code == 200
