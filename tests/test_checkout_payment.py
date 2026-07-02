"""Tests for checkout, Razorpay order creation, payment verification,
the success page, and invoice download."""

from unittest.mock import patch

from conftest import login_user


def test_checkout_requires_login(client):
    resp = client.get('/checkout')
    assert resp.status_code == 302
    assert '/login' in resp.headers['Location']


def test_checkout_get_shows_cart_total(client, mock_db, mock_cursor):
    login_user(client, user_id=1)
    mock_cursor.fetchall.return_value = [(1, 'Candle', 199.0, 'img.jpg', 2)]
    resp = client.get('/checkout')
    assert resp.status_code == 200


def test_checkout_post_saves_shipping_details_and_redirects(client, mock_db, mock_cursor):
    login_user(client, user_id=1)
    resp = client.post('/checkout', data={
        'fullname': 'Test User', 'phone': '9999999999',
        'address': '123 Test St', 'total': '500'
    })
    assert resp.status_code == 302
    assert '/review' in resp.headers['Location']


def test_review_requires_checkout_data(client):
    resp = client.get('/review')
    assert resp.status_code == 302
    assert '/checkout' in resp.headers['Location']


def test_review_shows_shipping_summary(client):
    with client.session_transaction() as sess:
        sess['fullname'] = 'Test User'
        sess['phone'] = '9999999999'
        sess['address'] = '123 Test St'
        sess['total'] = '500'
    resp = client.get('/review')
    assert resp.status_code == 200


def test_payment_requires_checkout_data(client):
    resp = client.get('/payment')
    assert resp.status_code == 302


def test_payment_page_loads(client):
    with client.session_transaction() as sess:
        sess['total'] = '500'
    resp = client.get('/payment')
    assert resp.status_code == 200


def test_create_order_success(client):
    with patch('app.client') as mock_razorpay_client:
        mock_razorpay_client.order.create.return_value = {
            'id': 'order_test123', 'amount': 50000, 'currency': 'INR'
        }
        resp = client.post('/api/create-order', json={'amount': 50000})
    assert resp.status_code == 200
    assert resp.get_json()['order_id'] == 'order_test123'


def test_create_order_rejects_zero_amount(client):
    resp = client.post('/api/create-order', json={'amount': 0})
    assert resp.status_code == 400


def test_create_order_rejects_amount_below_minimum(client):
    resp = client.post('/api/create-order', json={'amount': 50})
    assert resp.status_code == 400


def test_verify_payment_requires_login(client):
    resp = client.post('/api/verify-payment', json={
        'razorpay_payment_id': 'pay_1', 'razorpay_order_id': 'order_1',
        'fullname': 'Test', 'phone': '999', 'address': 'addr', 'total': '500'
    })
    assert resp.status_code == 401


def test_verify_payment_creates_order(client, mock_db, mock_cursor):
    login_user(client, user_id=1)
    resp = client.post('/api/verify-payment', json={
        'razorpay_payment_id': 'pay_1', 'razorpay_order_id': 'order_1',
        'fullname': 'Test', 'phone': '999', 'address': 'addr', 'total': '500'
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['status'] == 'payment_verified'
    assert 'order_id' in data
    # confirm it attempted to insert the order into the DB
    mock_cursor.execute.assert_called_once()
    assert 'INSERT INTO orders' in mock_cursor.execute.call_args.args[0]


def test_success_page_requires_order(client):
    resp = client.get('/success')
    assert resp.status_code == 404


def test_success_page_shows_order(client, mock_db):
    login_user(client, user_id=1)
    verify_resp = client.post('/api/verify-payment', json={
        'razorpay_payment_id': 'pay_1', 'razorpay_order_id': 'order_1',
        'fullname': 'Test', 'phone': '999', 'address': 'addr', 'total': '500'
    })
    order_id = verify_resp.get_json()['order_id']
    resp = client.get(f'/success?order_id={order_id}')
    assert resp.status_code == 200


def test_download_invoice_returns_404_for_unknown_order(client):
    resp = client.get('/invoice/NONEXISTENT/download')
    assert resp.status_code == 404


def test_download_invoice_returns_pdf(client, mock_db):
    login_user(client, user_id=1)
    verify_resp = client.post('/api/verify-payment', json={
        'razorpay_payment_id': 'pay_1', 'razorpay_order_id': 'order_1',
        'fullname': 'Test', 'phone': '999', 'address': 'addr', 'total': '500'
    })
    order_id = verify_resp.get_json()['order_id']
    resp = client.get(f'/invoice/{order_id}/download')
    assert resp.status_code == 200
    assert resp.mimetype == 'application/pdf'
