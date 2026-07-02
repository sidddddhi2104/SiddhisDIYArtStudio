"""Tests for routes that don't require login: home, about, products, etc."""


def test_home(client):
    resp = client.get('/')
    assert resp.status_code == 200


def test_about(client):
    resp = client.get('/about')
    assert resp.status_code == 200


def test_wishlist(client):
    resp = client.get('/wishlist')
    assert resp.status_code == 200


def test_welcome(client):
    resp = client.get('/welcome')
    assert resp.status_code == 200


def test_landing(client):
    resp = client.get('/landing')
    assert resp.status_code == 200


def test_products_lists_items(client, mock_db, mock_cursor):
    mock_cursor.fetchall.return_value = [
        (1, 'Candle', 'Decor', 199, 'candle.jpg', 'A nice candle')
    ]
    resp = client.get('/products')
    assert resp.status_code == 200


def test_product_detail_found(client, mock_db, mock_cursor):
    mock_cursor.fetchone.return_value = (1, 'Candle', 'Decor', 199, 'candle.jpg', 'desc')
    resp = client.get('/product/1')
    assert resp.status_code == 200


def test_contact_get(client):
    resp = client.get('/contact')
    assert resp.status_code == 200


def test_contact_post_saves_message(client, mock_db, mock_cursor):
    resp = client.post('/contact', data={
        'name': 'Alice', 'email': 'alice@test.com', 'message': 'Hello!'
    })
    assert resp.status_code in (200, 302)
    mock_cursor.execute.assert_called_once()
