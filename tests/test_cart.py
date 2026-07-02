"""Tests for cart viewing, adding, removing, and quantity updates."""

from conftest import login_user


def test_cart_requires_login(client):
    resp = client.get('/cart')
    assert resp.status_code == 302
    assert '/login' in resp.headers['Location']


def test_cart_shows_items_when_logged_in(client, mock_db, mock_cursor):
    login_user(client, user_id=1)
    mock_cursor.fetchall.return_value = [
        (1, 2, 'Candle', 'Decor', 199.0, 'candle.jpg', 'desc', 2)
    ]
    resp = client.get('/cart')
    assert resp.status_code == 200


def test_add_to_cart_requires_login(client):
    resp = client.get('/add-to-cart/1')
    assert resp.status_code == 302
    assert '/login' in resp.headers['Location']


def test_add_to_cart_inserts_new_item(client, mock_db, mock_cursor):
    login_user(client, user_id=1)
    mock_cursor.fetchone.return_value = None  # not already in cart
    resp = client.get('/add-to-cart/5')
    assert resp.status_code == 302
    assert '/products' in resp.headers['Location']


def test_add_to_cart_increments_existing_item(client, mock_db, mock_cursor):
    login_user(client, user_id=1)
    mock_cursor.fetchone.return_value = (1, 1, 5, 1)  # already in cart
    resp = client.get('/add-to-cart/5')
    assert resp.status_code == 302


def test_remove_from_cart_requires_login(client):
    resp = client.get('/remove-from-cart/1')
    assert resp.status_code == 302
    assert '/login' in resp.headers['Location']


def test_remove_from_cart_deletes_and_redirects(client, mock_db, mock_cursor):
    login_user(client, user_id=1)
    resp = client.get('/remove-from-cart/1')
    assert resp.status_code == 302
    assert '/cart' in resp.headers['Location']
    mock_cursor.execute.assert_called_once()


def test_update_cart_qty_increase(client, mock_db, mock_cursor):
    login_user(client, user_id=1)
    mock_cursor.fetchone.return_value = (2,)
    resp = client.get('/update-cart-qty/1/increase')
    assert resp.status_code == 302


def test_update_cart_qty_decrease_does_not_go_below_one(client, mock_db, mock_cursor):
    login_user(client, user_id=1)
    mock_cursor.fetchone.return_value = (1,)
    resp = client.get('/update-cart-qty/1/decrease')
    assert resp.status_code == 302
    # UPDATE should still run, but with quantity left at 1 (not 0)
    update_call = mock_cursor.execute.call_args_list[-1]
    assert update_call.args[1][0] == 1
