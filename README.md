## Flask API for Customers and Orders with OAuth and SMS Notifications
This repository contains a Flask-based service that manages customers and orders, integrates OAuth for authentication (via OpenID Connect), and sends SMS alerts using Africa's Talking API when a new order is placed.

### Features
- Customer and Order Management: Add and retrieve customer and order data via REST APIs.
- OAuth Authentication: Secure the application using OAuth via an OpenID Connect provider.
- SMS Notifications: Notify customers via SMS using Africa's Talking API when an order is successfully placed.
- SQLite Database: Store customer and order data in an SQLite database.
- CI/CD: Tests with unit test coverage and continuous integration/deployment (CI/CD).


### Prerequisites
Before running this application, make sure you have the following dependencies installed:

Python 3.8+
pip (Python package installer)
Africa's Talking API credentials (username and API key)
OAuth provider credentials (e.g., Auth0)
SQLite for the database (already included with Python)


### Installation

**Clone the repository:

bash
Copy code
git clone <https://github.com/kurves/SIBackendTest>
cd <SIBackendTest>

**Create and activate a Python virtual environment:
bash
Copy code
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

Install the required packages:
bash
Copy code
pip install -r requirements.txt
Set up the environment variables in a .env file (copy from .env.example):

bash
Copy code
cp .env.example .env
Update the following variables in the .env file with your credentials:

username: Africa's Talking API username.
api_key: Africa's Talking API key.
AUTH0_CLIENT_ID: Your OAuth provider's client ID (e.g., Auth0).
AUTH0_CLIENT_SECRET: Your OAuth provider's client secret.
AUTH0_DOMAIN: Your OAuth provider's domain.
AUTH0_REDIRECT_URI: The redirect URI for OAuth callbacks (e.g., http://localhost:3000/callback).
APP_SECRET_KEY: A secret key for session management in Flask.

### Set up the database:

bash
Copy code
flask db upgrade
Run the Flask application:

bash
Copy code
python app.py
The app will start at http://localhost:3000.

#### API Endpoints

1. Customers

Add Customer
POST /customers
Request Body (JSON):

json
```
{
    "name": "John Doe",
    "code": "JD123",
    "number": "+254700123456"
}
```

Response:

json

```
{
    "message": "Customer added successfully"
}
```

Get Customers
GET /customers
Response:
```
[
    {
        "id": 1,
        "name": "John Doe",
        "code": "JD123",
        "number": "+254700123456"
    }
]
```

2. Orders
Add Order
POST /orders
Request Body (JSON):

```
{
    "item": "Laptop",
    "amount": 1500.99,
    "customer_id": 1
}

```

Response:
```
{
    "message": "Order added successfully"
}
``

Get Orders
GET /orders
```
[
    {
        "id": 1,
        "item": "Laptop",
        "amount": 1500.99,
        "customer_id": 1
    }
]
```


### SMS Notifications

When an order is placed, an SMS notification is sent to the customer automatically using Africa’s Talking API.

- Authentication (OAuth)
The app uses OAuth to authenticate users via an external OpenID Connect provider like Auth0.

- Login
To initiate login, navigate to /login. This redirects users to the OAuth provider for authentication.

- Callback
Once authenticated, the user is redirected back to the app at /callback where their token is processed.

- Logout
To log out, go to /logout. This clears the session and logs the user out.

#### Africa's Talking Integration

The application integrates with Africa's Talking to send SMS notifications. Make sure you have set the username and api_key in the .env file.

To send an SMS, the send_sms_alert function is triggered automatically when a new order is placed.

### Running Tests
To run the tests:

```
pytest --cov

```

Deployment
This app can be deployed to any PaaS (e.g., Heroku) or server environment. Ensure the environment variables and database are correctly set in your production environment.