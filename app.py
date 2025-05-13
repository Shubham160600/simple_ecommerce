from flask import Flask, render_template, redirect, url_for, session, request
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database setup
DB_PATH = 'data/products.db'

def get_products():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM products")
    products = c.fetchall()
    conn.close()
    return products

@app.route('/')
def index():
    products = get_products()
    return render_template('index.html', products=products)

@app.route('/product/<int:product_id>')
def product(product_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM products WHERE id=?", (product_id,))
    product = c.fetchone()
    conn.close()
    return render_template('product.html', product=product)

@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    if 'cart' not in session:
        session['cart'] = []
    session['cart'].append(product_id)
    return redirect(url_for('cart'))

@app.route('/cart')
def cart():
    cart_items = session.get('cart', [])
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    products = []
    total = 0
    for item_id in cart_items:
        c.execute("SELECT * FROM products WHERE id=?", (item_id,))
        product = c.fetchone()
        if product:
            products.append(product)
            total += product[2]
    conn.close()
    return render_template('cart.html', products=products, total=total)

@app.route('/clear_cart')
def clear_cart():
    session['cart'] = []
    return redirect(url_for('cart'))

if __name__ == '__main__':
    os.makedirs('data', exist_ok=True)
    if not os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE products (
                id INTEGER PRIMARY KEY,
                name TEXT,
                price REAL,
                description TEXT
            )
        ''')
        # Sample products
        products = [
            ('T-shirt', 15.99, 'Comfortable cotton T-shirt'),
            ('Mug', 9.99, 'Ceramic mug for coffee or tea'),
            ('Notebook', 5.49, '100 pages notebook'),
        ]
        c.executemany('INSERT INTO products (name, price, description) VALUES (?, ?, ?)', products)
        conn.commit()
        conn.close()

    app.run(debug=True)
