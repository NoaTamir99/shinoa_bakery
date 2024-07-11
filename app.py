from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import sqlite3
import os
import json
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import functools

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'static/uploads/'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id, username, role):
        self.id = id
        self.username = username
        self.role = role

@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect('sqlite.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    if user:
        return User(id=user[0], username=user[1], role=user[3])
    return None

def get_db_connection():
    conn = sqlite3.connect('sqlite.db')
    conn.row_factory = sqlite3.Row
    return conn

def setup_database():
    with get_db_connection() as con:
        cur = con.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('customer', 'admin', 'manager')),
            cart TEXT
        )
        """)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            items TEXT NOT NULL,
            total_amount REAL NOT NULL,
            status TEXT NOT NULL
        )
        """)
        cur.execute('''
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                text TEXT NOT NULL,
                image_url TEXT
            )
        ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS dishes (
                name TEXT NOT NULL,
                price INTEGER NOT NULL,
                category TEXT NOT NULL
            )
        ''')
        con.commit()

def role_required(role):
    def wrapper(fn):
        @functools.wraps(fn)
        @login_required
        def decorated_view(*args, **kwargs):
            if current_user.role != role:
                return 'Unauthorized', 401
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/review', methods=['GET', 'POST'])
@login_required
def review():
    if request.method == 'POST' and current_user.role != 'manager':
        username = request.form['username']
        text = request.form['review']
        image = request.files['image']
        image_url = None

        with get_db_connection() as con:
            cur = con.cursor()
            cur.execute('SELECT 1 FROM users WHERE username = ?', (username,))
            user_exists = cur.fetchone()

            if not user_exists:
                flash('Username does not exist. Please register before leaving a review.')
                return redirect(url_for('review'))

            if image:
                filename = secure_filename(image.filename)
                image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_url = filename

            cur.execute('INSERT INTO reviews (username, text, image_url) VALUES (?, ?, ?)', (username, text, image_url))
            con.commit()

        return redirect(url_for('review'))

    with get_db_connection() as con:
        cur = con.cursor()
        cur.execute('SELECT * FROM reviews')
        reviews = cur.fetchall()

    return render_template('review.html', reviews=reviews)

@app.route('/orders_management', endpoint='orders_management')
@role_required('admin')
def orders_management():
    with get_db_connection() as con:
        cur = con.cursor()
        cur.execute("SELECT * FROM orders")
        orders = cur.fetchall()
    return render_template('orders.html', orders=orders)

@app.route('/close_order/<int:order_id>', methods=['POST'], endpoint='close_order')
@role_required('admin')
def close_order(order_id):
    with get_db_connection() as con:
        cur = con.cursor()
        cur.execute('DELETE FROM orders WHERE id = ?', (order_id,))
        con.commit()
    return redirect(url_for('orders_management'))

@app.route('/menu')
@login_required
def menu():
    with get_db_connection() as con:
        cur = con.cursor()
        cur.execute("SELECT * FROM dishes")
        dishes = cur.fetchall()
    return render_template('menu.html', dishes=dishes)

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/checkout')
@login_required
def checkout():
    return render_template('checkout.html')

@app.route('/process_payment', methods=['POST'])
@login_required
def process_payment():
    if current_user.role != 'customer':
        return 'Unauthorized', 403
    
    # Retrieve cart details
    user_id = current_user.id
    with get_db_connection() as con:
        cur = con.cursor()
        cur.execute('SELECT cart FROM users WHERE id = ?', (user_id,))
        user_cart = cur.fetchone()['cart']
        cart = json.loads(user_cart) if user_cart else []
    
    # Calculate total amount
    total_amount = sum(item['price'] * item['quantity'] for item in cart)
    
    # Save order details to the database
    customer_name = current_user.username
    items = json.dumps(cart)
    cur.execute('INSERT INTO orders (customer_name, items, total_amount, status) VALUES (?, ?, ?, ?)',
                (customer_name, items, total_amount, 'open'))
    
    # Clear the cart
    cur.execute('UPDATE users SET cart = ? WHERE id = ?', (json.dumps([]), user_id))
    con.commit()
    
    return jsonify({'message': 'Payment successful!'})

@app.route('/order_confirmation')
def order_confirmation():
    return 'Order confirmed!'

@app.route('/manager')
@role_required('manager')
def manager():
    return render_template('manager.html')

@app.route('/add_dish', methods=['POST'])
@role_required('manager')
def add_dish():
    name = request.form['name']
    price = request.form['price']
    category = request.form['category']
    with get_db_connection() as con:
        cur = con.cursor()
        cur.execute("INSERT INTO dishes (name, price, category) VALUES (?, ?, ?)", (name, price, category))
        con.commit()
    return redirect(url_for('menu'))

@app.route('/delete_dish', methods=['POST'])
@role_required('manager')
def delete_dish():
    name = request.form['name']
    with get_db_connection() as con:
        cur = con.cursor()
        cur.execute("DELETE FROM dishes WHERE name = ?", (name,))
        con.commit()
    return redirect(url_for('menu'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        
        with get_db_connection() as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM users WHERE username = ? AND role = ?", (username, role))
            user = cur.fetchone()
            
            if user and check_password_hash(user['password'], password):
                user_obj = User(id=user['id'], username=user['username'], role=user['role'])
                login_user(user_obj)
                return redirect(url_for('index'))
            else:
                flash('Invalid username or password')
                return redirect(url_for('login'))
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        
        hashed_password = generate_password_hash(password)
        
        with get_db_connection() as con:
            cur = con.cursor()
            cur.execute("INSERT INTO users (username, password, role, cart) VALUES (?, ?, ?, ?)", (username, hashed_password, role, json.dumps([])))
            con.commit()
        
        flash('Registration successful. Please login.')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/cart', methods=['GET', 'POST'])
@login_required
def cart():
    user_id = current_user.id
    with get_db_connection() as con:
        cur = con.cursor()
        if request.method == 'POST':
            cart = request.json.get('cart')
            cur.execute('UPDATE users SET cart = ? WHERE id = ?', (json.dumps(cart), user_id))
            con.commit()
            return jsonify({'message': 'Cart updated successfully'})
        else:
            cur.execute('SELECT cart FROM users WHERE id = ?', (user_id,))
            user_cart = cur.fetchone()['cart']
            return jsonify(json.loads(user_cart) if user_cart else [])

if __name__ == '__main__':
    setup_database()
    app.run(debug=True)
