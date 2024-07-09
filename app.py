from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
import os
import json
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'static/uploads/'

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
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                category TEXT NOT NULL
            )
        ''')
        cur.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cur.fetchall()]
        if 'cart' not in columns:
            cur.execute("ALTER TABLE users ADD COLUMN cart TEXT")
        con.commit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/review', methods=['GET', 'POST'])
def review():
    if request.method == 'POST':
        username = request.form['username']
        text = request.form['review']
        image = request.files['image']
        image_url = None

        if image:
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image_url = filename

        with get_db_connection() as con:
            cur = con.cursor()
            cur.execute('INSERT INTO reviews (username, text, image_url) VALUES (?, ?, ?)', (username, text, image_url))
            con.commit()

        return redirect(url_for('review'))

    with get_db_connection() as con:
        cur = con.cursor()
        cur.execute('SELECT * FROM reviews')
        reviews = cur.fetchall()

    return render_template('review.html', reviews=reviews)

@app.route('/menu')
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
def checkout():
    return render_template('checkout.html')

@app.route('/process_payment', methods=['POST'])
def process_payment():
    return redirect(url_for('index'))

@app.route('/manager')
def manager():
    return render_template('manager.html')

@app.route('/add_dish', methods=['POST'])
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
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['role'] = user['role']
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
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/cart', methods=['GET', 'POST'])
def cart():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
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
