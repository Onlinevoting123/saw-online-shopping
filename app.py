from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

app.secret_key = 'Hemanth'

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

products = [
    {'id': 1, 'name': '6pcs Brown cups', 'price': 99, 'image': '/static/images/btcups.jpg'},
    {'id': 2, 'name': 'White cups set', 'price': 129, 'image': '/static/images/wtset.jpg'},
    {'id': 3, 'name': 'Red snack set', 'price': 129, 'image': '/static/images/rsset.jpg'},
    {'id': 4, 'name': '2pcs Soup cups', 'price': 99, 'image': '/static/images/bscups.jpg'},
    {'id': 5, 'name': 'Plastic boxes', 'price': 129, 'image': '/static/images/tboxes.jpg'},
    {'id': 6, 'name': '2pcs Brown cups', 'price': 99, 'image': '/static/images/btcup.jpg'},
    {'id': 7, 'name': '2pcs Green cups', 'price': 99, 'image': '/static/images/gtcups.jpg'},
    {'id': 8, 'name': '4pcs Glass bowls', 'price': 99, 'image': '/static/images/hcups.jpg'},
    {'id': 9, 'name': '2pcs Soup bowls', 'price': 99, 'image': '/static/images/sb.jpg'},
    {'id': 10, 'name': '3pcs White plates', 'price': 99, 'image': '/static/images/plates.jpg'},
    {'id': 11, 'name': '3pcs Plastic cups', 'price': 99, 'image': '/static/images/plasticcups.jpg'},
    {'id': 12, 'name': '4pcs Spoons', 'price': 99, 'image': '/static/images/spoons.jpg'},
    {'id': 13, 'name': '3pcs Plates', 'price': 99, 'image': '/static/images/yplates.jpg'},
    {'id': 14, 'name': 'Brush stand', 'price': 99, 'image': '/static/images/plas.jpg'},
    {'id': 15, 'name': 'Cups set', 'price': 99, 'image': '/static/images/homeset.jpg'},
    {'id': 16, 'name': 'Square plates', 'price': 99, 'image': '/static/images/splates.jpg'},
    {'id': 17, 'name': 'White cup', 'price': 99, 'image': '/static/images/wc.jpg'},
    {'id': 18, 'name': 'Red box', 'price': 99, 'image': '/static/images/redb.jpg'},
]


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


from flask import flash

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
    if 'cart' in session:
        order_history = session.get('order_history', [])
        total_price = sum(item['price'] * item['quantity'] for item in session['cart'])
        p=[]
        z=[]
        a=""
        for i in session['cart']:
            p.append(str(i['id']))
            p.append(i['name'])
            p.append(str(i['price']))
            p.append(str(i['quantity']))
            a=" ".join(p)
            z.append(a)
            p=[]
            a=""
        a="+".join(z)
        order_history.append({
            'order_id': len(order_history) + 1,
            'names': session['cart'],
            'total': total_price,
            'customer_name': session['customer_name'],
            'customer_number': session['customer_number'],
            'customer_address': session['customer_address'],
            'customer_pincode': session['customer_pincode'],
        })
        user_details = User(
            name1=session['customer_name'],
            number1=session['customer_number'],
            address1=session['customer_address'],
            pincode1=session['customer_pincode'],
            names1=a,
            total1=total_price
        )
        db.session.add(user_details)
        db.session.commit()
        session['order_history'] = order_history
        session.pop('cart', None)  
        session.modified = True
        flash('Your order has been placed successfully!', 'success')

    return render_template('order.html')


@app.route('/cart/history', methods=['GET'])
def order_history():
    orders = session.get('order_history', [])
    return render_template('history.html', orders=orders)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
