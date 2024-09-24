from flask import Flask, request, jsonify, redirect, url_for, session, render_template
from models import db, Customer, Order
import json
from os import environ as env
from urllib.parse import quote_plus, urlencode
from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv
import africastalking


ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)
    
app = Flask(__name__)
app.secret_key = env.get("APP_SECRET_KEY")


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


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///customers_orders.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)


# OAuth configuration (replace with your OIDC provider details)
@app.route("/login")
def login():
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    ) 

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
    customer = Customer(name=data['name'], code=data['code'])
    db.session.add(customer)
    db.session.commit()
    return jsonify({'message': 'Customer added successfully'})

@app.route('/orders', methods=['POST'])
def add_order():
    data = request.get_json()
    if 'item' not in data or 'amount' not in data or 'customer_id' not in data:
        return jsonify({'error': 'Item, amount, and customer_id are required'}), 400

    customer = Customer.query.get(data['customer_id'])
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404
    order = Order(item=data['item'], amount=data['amount'], time=data['time'])
    db.session.add(order)
    db.session.commit()
    return jsonify({'message': 'Order added successfully'}), 201
    

#send message when order is palaced
def send_sms_alert(phone_number, item):
    message = f"Your order for {item} has been placed successfully!"
    try:
        response = sms.send(message, [phone_number])
        print(f"SMS sent: {response}")
    except Exception as e:
        print(f"Error sending SMS: {e}")


# Route to get all customers
@app.route('/customers', methods=['GET'])
def get_customers():
    customers = Customer.query.all()
    customers_data = [{'id': customer.id, 'name': customer.name, 'code': customer.code} for customer in customers]
    return jsonify(customers_data), 200

# Route to get all orders
@app.route('/orders', methods=['GET'])
def get_orders():
    orders = Order.query.all()
    orders_data = [{'id': order.id, 'item': order.item, 'amount': order.amount, 'time': order.time, 'customer_id': order.customer_id} for order in orders]
    return jsonify(orders_data), 200


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




