from flask import Flask, render_template, url_for, request, redirect
import sqlite3
import os

app = Flask(__name__)

@app.route('/add_pizza', methods=['GET', 'POST'])
def add_pizza():
    dish_name = 'pizza'
    price = 8    
    with get_db_connection() as con:
        cur = con.cursor()
        cur.execute("INSERT INTO dishes (name, price) VALUES (?, ?)", 
                    (dish_name, price))
        con.commit()
        
    return render_template('index.html')

def get_db_connection():
    conn = sqlite3.connect('sqlite.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/review')
def review():
    return render_template('review.html')

@app.route('/menu')
def menu():
    return render_template('menu.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/checkout')
def checkout():
    return render_template('checkout.html')

@app.route('/process_payment', methods=['POST'])
def process_payment():
    # Add payment processing logic here
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
