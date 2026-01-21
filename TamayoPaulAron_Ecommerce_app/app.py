from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

# ----------------------
# App Configuration
# ----------------------
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ----------------------
# Database Models
# ----------------------

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100))
    quantity = db.Column(db.Integer)
    total_price = db.Column(db.Float)

# ----------------------
# Schemas (Serialization)
# ----------------------

class ProductSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    price = fields.Float(required=True)
    stock = fields.Int(required=True)

class OrderSchema(Schema):
    id = fields.Int(dump_only=True)
    product_name = fields.Str()
    quantity = fields.Int()
    total_price = fields.Float()

product_schema = ProductSchema()
products_schema = ProductSchema(many=True)

order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)

# ----------------------
# PRODUCT CRUD
# ----------------------

# CREATE PRODUCT
@app.route('/products', methods=['POST'])
def add_product():
    data = request.json
    product = Product(
        name=data['name'],
        price=data['price'],
        stock=data['stock']
    )
    db.session.add(product)
    db.session.commit()
    return jsonify(product_schema.dump(product)), 201

# READ ALL PRODUCTS
@app.route('/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    return jsonify(products_schema.dump(products))

# READ ONE PRODUCT
@app.route('/products/<int:id>', methods=['GET'])
def get_product(id):
    product = Product.query.get_or_404(id)
    return jsonify(product_schema.dump(product))

# UPDATE PRODUCT
@app.route('/products/<int:id>', methods=['PUT'])
def update_product(id):
    product = Product.query.get_or_404(id)
    data = request.json
    product.name = data['name']
    product.price = data['price']
    product.stock = data['stock']
    db.session.commit()
    return jsonify(product_schema.dump(product))

# DELETE PRODUCT
@app.route('/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": "Product deleted"})

# ----------------------
# ORDER (BUY PRODUCT)
# ----------------------

@app.route('/orders', methods=['POST'])
def create_order():
    data = request.json
    product = Product.query.get_or_404(data['product_id'])

    if product.stock < data['quantity']:
        return jsonify({"error": "Not enough stock"}), 400

    total = product.price * data['quantity']

    order = Order(
        product_name=product.name,
        quantity=data['quantity'],
        total_price=total
    )

    product.stock -= data['quantity']

    db.session.add(order)
    db.session.commit()

    return jsonify(order_schema.dump(order)), 201

# VIEW ORDERS
@app.route('/orders', methods=['GET'])
def get_orders():
    orders = Order.query.all()
    return jsonify(orders_schema.dump(orders))

# ----------------------
# Run App
# ----------------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)