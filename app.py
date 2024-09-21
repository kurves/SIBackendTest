
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///customers_orders.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Customer model
class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(50), unique=True, nullable=False)

    def __repr__(self):
        return f"<Customer {self.name}>"

# Order model
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    time = db.Column(db.DateTime, default=datetime.utcnow)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)

    customer = db.relationship('Customer', backref=db.backref('orders', lazy=True))

    def __repr__(self):
        return f"<Order {self.item}>"

# Route to add a customer
@app.route('/customers', methods=['POST'])
def add_customer():
    data = request.get_json()
    if 'name' not in data or 'code' not in data:
        return jsonify({'error': 'Name and code are required'}), 400

    customer = Customer(name=data['name'], code=data['code'])
    db.session.add(customer)
    db.session.commit()
    return jsonify({'message': 'Customer added successfully'}), 201

# Route to add an order
@app.route('/orders', methods=['POST'])
def add_order():
    data = request.get_json()
    if 'item' not in data or 'amount' not in data or 'customer_id' not in data:
        return jsonify({'error': 'Item, amount, and customer_id are required'}), 400

    customer = Customer.query.get(data['customer_id'])
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404

    order = Order(item=data['item'], amount=data['amount'], customer_id=customer.id)
    db.session.add(order)
    db.session.commit()
    return jsonify({'message': 'Order added successfully'}), 201

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

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Creates tables if they do not exist
    app.run(debug=True)


