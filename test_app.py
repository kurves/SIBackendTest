# test_app.py

import pytest
from app import app, db, Customer, Order

@pytest.fixture
def client():
    with app.test_client() as client:
        with app.app_context():
            db.create_all()  
            yield client
            db.session.remove()
            db.drop_all() 

def test_add_customer(client):
    # Test adding a customer
    response = client.post('/customers', json={
        'name': 'John Doe',
        'code': 'JD123',
        'number': '+254100716916'
    })
    assert response.status_code == 201  

def test_add_order(client):
    # Test adding a customer first
    client.post('/customers', json={
        'name': 'John Doe',
        'code': 'JD123',
        'number': '+254100716916'
    })

    # Then test adding an order
    response = client.post('/orders', json={
        'item': 'Laptop',
        'amount': 1200.00,
        'customer_id': 1  
    })
    assert response.status_code == 201 
