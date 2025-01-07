from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.urandom(24)

db = SQLAlchemy(app)

# Database Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name1 = db.Column(db.String(100), nullable=False)
    number1 = db.Column(db.String(15), nullable=False)
    address1 = db.Column(db.String(200), nullable=False)
    pincode1 = db.Column(db.String(10), nullable=False)
    names1 = db.Column(db.Text, nullable=False)
    total1 = db.Column(db.Integer, nullable=False)

# Products List
products = [
    {'id': 1, 'name': '6pcs Brown cups', 'price': 99, 'image': '/static/images/btcups.jpg'},
    {'id': 2, 'name': 'White cups set', 'price': 129, 'image': '/static/images/wtset.jpg'},
    # Add more products as needed
]

# Routes
@app.route('/')
def home():
    if 'customer_name' not in session or 'customer_number' not in session:
        return redirect(url_for('login'))
    return render_template('index.html', products=products)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['customer_name'] = request.form['customer_name']
        session['customer_number'] = request.form['customer_number']
        return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/address', methods=['GET', 'POST'])
def address():
    if request.method == 'POST':
        session['customer_address'] = request.form['customer_address']
        session['customer_pincode'] = request.form['customer_pincode']
        return redirect(url_for('order'))
    return render_template('address.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully!', 'success')
    return redirect(url_for('login'))

@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    product = next((p for p in products if p['id'] == product_id), None)
    if product:
        cart = session.get('cart', [])
        cart_item = next((item for item in cart if item['id'] == product_id), None)
        if cart_item:
            cart_item['quantity'] += 1
        else:
            cart.append({'id': product['id'], 'name': product['name'], 'price': product['price'], 'quantity': 1})
        session['cart'] = cart
        session.modified = True
    return redirect(url_for('view_cart'))

@app.route('/cart', methods=['GET'])
def view_cart():
    cart = session.get('cart', [])
    total = sum(item['price'] * item['quantity'] for item in cart)
    return render_template('try.html', cart=cart, total=total)

@app.route('/order', methods=['POST', 'GET'])
def order():
    if request.method == 'POST' and 'cart' in session:
        try:
            total_price = sum(item['price'] * item['quantity'] for item in session['cart'])
            order_details = '\n'.join([f"{item['quantity']}x {item['name']} - ${item['price'] * item['quantity']}" for item in session['cart']])

            new_user = User(
                name1=session.get('customer_name'),
                number1=session.get('customer_number'),
                address1=session.get('customer_address'),
                pincode1=session.get('customer_pincode'),
                names1=order_details,
                total1=total_price
            )
            db.session.add(new_user)
            db.session.commit()

            session.pop('cart', None)
            session.modified = True
            flash('Your order has been placed successfully!', 'success')
            return redirect(url_for('home'))

        except Exception as e:
            flash(f"An error occurred while placing the order: {str(e)}", 'danger')
            return redirect(url_for('view_cart'))

    return render_template('order.html')

@app.route('/users', methods=['GET'])
def users_page():
    users = User.query.all()
    return render_template('users.html', users=users)

# Run the App
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
