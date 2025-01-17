from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'Hemanth'

db = SQLAlchemy(app)

# Database Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name1 = db.Column(db.String(100), nullable=False)
    number1 = db.Column(db.Integer, nullable=False)
    address1 = db.Column(db.String(100), nullable=False)
    pincode1 = db.Column(db.Integer, nullable=False)
    names1 = db.Column(db.String(100), nullable=False)
    total1 = db.Column(db.Integer, nullable=False)

@app.route('/users', methods=['GET'])
def users_page():
    users = User.query.all()
    return render_template('users.html', users=users)

# Sample Product List
products = [
    {'id': 1, 'name': '6pcs Brown cups', 'price': 99, 'image': '/static/images/btcups.jpg'},
    {'id': 2, 'name': 'White cups set', 'price': 129, 'image': '/static/images/wtset.jpg'},
    # Add other products here...
]

@app.route('/')
def home():
    if 'customer_name' not in session or 'customer_number' not in session:
        return redirect(url_for('login'))
    return render_template('index.html', products=products)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['customer_name'] = request.form.get('customer_name')
        session['customer_number'] = request.form.get('customer_number')
        return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/address', methods=['GET', 'POST'])
def address():
    if request.method == 'POST':
        session['customer_address'] = request.form.get('customer_address')
        session['customer_pincode'] = request.form.get('customer_pincode')
        return redirect(url_for('order'))
    return render_template('address.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully!', 'success')
    return redirect(url_for('login'))

@app.route('/remove_from_cart/<int:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    cart = session.get('cart', [])
    for item in cart:
        if item['id'] == product_id:
            item['quantity'] -= 1
            if item['quantity'] <= 0:
                cart.remove(item)
            break
    session['cart'] = cart
    session.modified = True
    return redirect(url_for('view_cart'))

@app.route('/cart', methods=['GET'])
def view_cart():
    cart = session.get('cart', [])
    total = sum(item['price'] * item['quantity'] for item in cart)
    return render_template('try.html', cart=cart, total=total)

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
        flash(f"{product['name']} has been added to your cart!")
    else:
        flash("Product not found!", "error")
    return redirect(url_for('view_cart'))

@app.route('/order', methods=['POST', 'GET'])
def order():
    if 'cart' not in session or not session['cart']:
        flash('Your cart is empty. Please add items before placing an order.', 'error')
        return redirect(url_for('home'))

    try:
        order_history = session.get('order_history', [])
        total_price = sum(item['price'] * item['quantity'] for item in session['cart'])

        # Prepare order details
        item_details = [f"{item['id']} {item['name']} {item['price']} {item['quantity']}" for item in session['cart']]
        item_string = "+".join(item_details)

        # Save to database
        user_details = User(
            name1=session['customer_name'],
            number1=session['customer_number'],
            address1=session['customer_address'],
            pincode1=session['customer_pincode'],
            names1=item_string,
            total1=total_price
        )
        db.session.add(user_details)
        db.session.commit()

        # Update session
        order_history.append({
            'order_id': len(order_history) + 1,
            'names': session['cart'],
            'total': total_price,
            'customer_name': session['customer_name'],
            'customer_number': session['customer_number'],
            'customer_address': session['customer_address'],
            'customer_pincode': session['customer_pincode'],
        })
        session['order_history'] = order_history
        session.pop('cart', None)
        session.modified = True

        flash('Your order has been placed successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f"An error occurred while placing the order: {str(e)}", 'error')

    return render_template('order.html')

@app.route('/cart/history', methods=['GET'])
def order_history():
    orders = session.get('order_history', [])
    return render_template('history.html', orders=orders)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensure database tables are created
    app.run(debug=True)
