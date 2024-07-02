from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

app = Flask(__name__)

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
        cur.execute("INSERT INTO dishes (name, price, category) VALUES (?, ?, ?)",
                    (name, price, category))
        con.commit()
    return redirect(url_for('menu'))

@app.route('/remove_dish', methods=['POST'])
def remove_dish():
    name = request.form['name']
    with get_db_connection() as con:
        cur = con.cursor()
        cur.execute("DELETE FROM dishes WHERE name = ?", (name,))
        con.commit()
    return redirect(url_for('menu'))

if __name__ == '__main__':
    app.run(debug=True)
