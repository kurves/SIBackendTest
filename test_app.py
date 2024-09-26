import pytest
from flask import url_for
from app import app, db, Customer, Order, send_sms_alert

# Test configuration
@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['WTF_CSRF_ENABLED'] = False
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client

# Test adding a customer
def test_add_customer(client):
    response = client.post('/customers', json={
        'name': 'John Doe',
        'code': 'CUST123',
        'number': '+254701234567'
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Customer added successfully'

    # Check if customer was added in the database
    customer = Customer.query.filter_by(name='John Doe').first()
    assert customer is not None
    assert customer.code == 'CUST123'

# Test fetching customers
def test_get_customers(client):
    # Add a customer to the database
    customer = Customer(name='John Doe', code='CUST123', number='+254701234567')
    db.session.add(customer)
    db.session.commit()

    # Fetch customers
    response = client.get('/customers')
    assert response.status_code == 200
    customers_data = response.get_json()
    assert len(customers_data) == 1
    assert customers_data[0]['name'] == 'John Doe'

# Test adding an order
def test_add_order(client):
    # Add a customer first
    customer = Customer(name='Jane Smith', code='CUST456', number='+254701234568')
    db.session.add(customer)
    db.session.commit()

    # Add an order for the customer
    response = client.post('/orders', json={
        'item': 'Laptop',
        'amount': 1299.99,
        'customer_id': customer.id
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data['message'] == 'Order added successfully'

    # Check if order was added in the database
    order = Order.query.filter_by(item='Laptop').first()
    assert order is not None
    assert order.amount == 1299.99
    assert order.customer_id == customer.id

# Test fetching orders
def test_get_orders(client):
    # Add a customer and an order
    customer = Customer(name='Jane Smith', code='CUST456', number='+254701234568')
    db.session.add(customer)
    db.session.commit()

    order = Order(item='Laptop', amount=1299.99, customer_id=customer.id)
    db.session.add(order)
    db.session.commit()

    # Fetch orders
    response = client.get('/orders')
    assert response.status_code == 200
    orders_data = response.get_json()
    assert len(orders_data) == 1
    assert orders_data[0]['item'] == 'Laptop'

# Test sending SMS alert after adding an order
def test_send_sms_alert(client, mocker):
    # Add a customer and an order
    customer = Customer(name='John Doe', code='CUST123', number='+254701234567')
    db.session.add(customer)
    db.session.commit()

    order = Order(item='Laptop', amount=1299.99, customer_id=customer.id)
    db.session.add(order)
    db.session.commit()

    # Mock the SMS sending to avoid actual API calls
    mock_send = mocker.patch('africastalking.SMS.send')
    mock_send.return_value = {'status': 'Success', 'message': 'Message sent'}

    # Trigger the SMS alert
    send_sms_alert(customer.id, order.id)

    # Assert that the mock was called
    mock_send.assert_called_once_with('Hello, Your Order 1 has been placed.', [customer.number])

# Test OAuth login
def test_login(client):
    # Mock the OAuth process
    with client.session_transaction() as session:
        session['user'] = {'email': 'test@example.com'}
    
    response = client.get('/')
    assert response.status_code == 200
    assert b'test@example.com' in response.data

# Test OAuth logout
def test_logout(client):
    # Mock the OAuth process
    with client.session_transaction() as session:
        session['user'] = {'email': 'test@example.com'}

    # Logout
    response = client.get('/logout')
    assert response.status_code == 302  # Redirect to Auth0 logout
