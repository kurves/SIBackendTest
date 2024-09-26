from flask import Flask, request, jsonify, redirect, url_for, session, render_template
import json
from os import environ as env
from urllib.parse import quote_plus, urlencode
from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv
import requests
import africastalking
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

username = env.get("username")
api_key = env.get("api_key")

africastalking.initialize(username, api_key)
sms = africastalking.SMS

app = Flask(__name__)
app.secret_key = env.get("APP_SECRET_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///customers_orders.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# OAuth configuration (replace with your OIDC provider details)
oauth = OAuth(app)
oauth.register(
    "auth0",
    client_id=env.get("AUTH0_CLIENT_ID"),
    client_secret=env.get("AUTH0_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email",
    },

    server_metadata_url=f'https://{env.get("AUTH0_DOMAIN")}/.well-known/openid-configuration'
)

# customer model
class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(50), unique=True, nullable=False)
    number = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f"<Customer {self.name}>"

# order model
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    customer = db.relationship('Customer', backref=db.backref('orders', lazy=True))
    def __repr__(self):
        return f"<Order {self.item}>"



# OAuth configuration (replace with your OIDC provider details)
@app.route("/login")
def login():
    return oauth.auth0.authorize_redirect(redirect_uri=env.get('AUTH0_REDIRECT_URI'))
    
   



@app.route("/callback", methods=["GET", "POST"])
def callback():
    token = oauth.auth0.authorize_access_token()
    session["user"] = token
    return redirect("/")

@app.route('/customers', methods=['POST'])
def add_customer():
    data = request.get_json()
    if 'name' not in data or 'code' not in data:
        return jsonify({'error': 'Name and code are required'}), 400
    customer = Customer(name=data['name'], code=data['code'], number=data['number'])
    try:
        db.session.add(customer)
        db.session.commit()
        return jsonify({'message': 'Customer added successfully'}), 201
    except Exception as e:
        db.session.rollback()  # Rollback in case of an error
        return jsonify({'error': str(e)}), 500



def send_sms_alert(customer_id, order_id):
    # Fetch customer from the database
    customer = db.session.get(Customer, customer_id)
    if customer:
        recipients = [customer.number]
        print(recipients)
        message = f"Hello, Your Order {order_id} has been placed."
        #sender = "SI70"  
        try:
            # Send the SMS using Africa's Talking API
            response = sms.send(message, recipients)
            print(response)  # Log the response for debugging
        except Exception as e:
            print(f"Order Couldn't be Placed: {e}")
    else:
        print("Customer not found")

@app.route('/orders', methods=['POST'])
def add_order():
    data = request.get_json()
    if 'item' not in data or 'amount' not in data or 'customer_id' not in data:
        return jsonify({'error': 'Item, amount, and customer_id are required'}), 400


    customer = db.session.get(Customer, data['customer_id'])
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404  
    order = Order(item=data['item'], amount=data['amount'],customer_id=data['customer_id'] )
    db.session.add(order)
    db.session.commit()
    send_sms_alert(customer.id, order.id)
    return jsonify({'message': 'Order added successfully'}), 201
    

# Route to get all customers
@app.route('/customers', methods=['GET'])
def get_customers():
    customers = Customer.query.all()
    customers_data = [{'id': customer.id, 'name': customer.name, 'code': customer.code, 'number': customer.number} for customer in customers]
    return jsonify(customers_data), 200

# Route to get all orders
@app.route('/orders', methods=['GET'])
def get_orders():
    orders = Order.query.all()
    orders_data = [{'id': order.id, 'item': order.item, 'amount': order.amount, 'customer_id': order.customer_id} for order in orders]
    return jsonify(orders_data), 200


# Define an endpoint where the SMS alert is triggered
@app.route('/order/<int:customer_id>/<int:order_id>', methods=['GET'])
def handle_order(customer_id, order_id):
    order = Order.query.get(order_id)
    
    if order:
        # Call send_sms_alert after placing the order
        send_sms_alert(customer_id, order_id)
        return f"Order {order_id} for customer {customer_id} has been placed. SMS alert sent."
    else:
        return "Order not found", 404

@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        "https://" + env.get("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("home", _external=True),
                "client_id": env.get("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )

@app.route("/")
def home():
    return render_template("home.html", session=session.get('user'), pretty=json.dumps(session.get('user'), indent=4))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Creates tables if they do not exist
    app.run(debug=True, host="0.0.0.0", port=env.get("PORT", 3000))




