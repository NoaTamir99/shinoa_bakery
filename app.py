from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/blog')
def blog():
    return render_template('blog.html')

@app.route('/menu')
def menu():
    return render_template('menu.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/cart')
def cart():
    return render_template('cart.html')

@app.route('/checkout')
def checkout():
    return render_template('checkout.html')

@app.route('/process_payment', methods=['POST'])
def process_payment():
    full_name = request.form['full-name']
    card_number = request.form['card-number']
    expiry_date = request.form['expiry-date']
    cvv = request.form['cvv']
    
    # כאן תוכל להוסיף את הלוגיקה לטיפול בתשלום, כגון אימות והעברה לשירות תשלומים
    # לדוגמה, הדפסה למסך לצורכי בדיקות בלבד:
    print(f"Full Name: {full_name}")
    print(f"Card Number: {card_number}")
    print(f"Expiry Date: {expiry_date}")
    print(f"CVV: {cvv}")

    # הפניה חזרה לדף הבית לאחר תשלום
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
