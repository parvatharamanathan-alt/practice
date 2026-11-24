import os
import requests
from flask import Flask, request, render_template_string

app = Flask(__name__)

# Uses AWS Cloud Map Service Discovery DNS by default
PAYMENT_SERVICE_URL = os.getenv("PAYMENT_SERVICE_URL", "http://payment.ecommerce.local:5000/pay")

PRODUCTS = [
    {"id": 1, "name": "Wireless Headphones", "price": 99.99, "desc": "Noise-canceling over-ear headphones"},
    {"id": 2, "name": "Smart Watch", "price": 149.99, "desc": "Fitness tracker with heart-rate monitor"},
    {"id": 3, "name": "Mechanical Keyboard", "price": 79.99, "desc": "RGB backlit tactile keyboard"},
]

CATALOG_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>ECS E-Commerce Store</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 40px auto; padding: 20px; background: #f4f6f8; }
        h1 { text-align: center; color: #232f3e; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 20px; margin-top: 30px; }
        .card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 6px rgba(0,0,0,0.1); text-align: center; }
        .price { font-size: 1.4em; color: #0073bb; font-weight: bold; margin: 10px 0; }
        .btn { display: inline-block; background: #ff9900; color: #111; padding: 10px 20px; text-decoration: none; border-radius: 5px; font-weight: bold; }
        .btn:hover { background: #e68a00; }
    </style>
</head>
<body>
    <h1>AWS ECS E-Commerce Store</h1>
    <div class="grid">
        {% for p in products %}
        <div class="card">
            <h3>{{ p.name }}</h3>
            <p>{{ p.desc }}</p>
            <div class="price">${{ p.price }}</div>
            <a class="btn" href="/payment?name={{ p.name }}&price={{ p.price }}">Buy Now</a>
        </div>
        {% endfor %}
    </div>
</body>
</html>
"""

PAYMENT_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Checkout & Payment</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 500px; margin: 40px auto; padding: 20px; background: #f4f6f8; }
        .box { background: white; padding: 25px; border-radius: 8px; box-shadow: 0 2px 6px rgba(0,0,0,0.1); }
        input { width: 100%; padding: 10px; margin: 10px 0; box-sizing: border-box; border: 1px solid #ccc; border-radius: 4px; }
        button { width: 100%; background: #28a745; color: white; padding: 12px; border: none; border-radius: 5px; font-size: 1em; cursor: pointer; }
        button:hover { background: #218838; }
    </style>
</head>
<body>
    <div class="box">
        <h2>Payment Page</h2>
        <p><strong>Product:</strong> {{ name }}</p>
        <p><strong>Total Amount:</strong> ${{ price }}</p>
        <form action="/process-payment" method="POST">
            <input type="hidden" name="name" value="{{ name }}">
            <input type="hidden" name="price" value="{{ price }}">
            <label>Cardholder Name</label>
            <input type="text" name="customer" placeholder="John Doe" required>
            <label>Card Number (Test)</label>
            <input type="text" name="card" placeholder="4111-1111-1111-1111" required>
            <button type="submit">Confirm & Pay ${{ price }}</button>
        </form>
        <p style="text-align:center; margin-top:15px;"><a href="/">Back to Store</a></p>
    </div>
</body>
</html>
"""

@app.route('/')
def catalog():
    return render_template_string(CATALOG_HTML, products=PRODUCTS)

@app.route('/payment')
def payment_page():
    name = request.args.get('name', 'Unknown Item')
    price = request.args.get('price', '0.00')
    return render_template_string(PAYMENT_HTML, name=name, price=price)

@app.route('/process-payment', methods=['POST'])
def process_payment():
    payload = {
        "item": request.form.get('name'),
        "amount": request.form.get('price'),
        "customer": request.form.get('customer')
    }
    try:
        # Internal microservice call over AWS VPC
        response = requests.post(PAYMENT_SERVICE_URL, json=payload, timeout=5)
        data = response.json()
        return f"""
        <div style="font-family: Arial; max-width: 500px; margin: 40px auto; padding: 25px; border: 1px solid #28a745; border-radius: 8px;">
            <h2 style="color: #28a745;">Payment Successful!</h2>
            <p><strong>Transaction ID:</strong> {data.get('transaction_id')}</p>
            <p><strong>Item:</strong> {data.get('item')}</p>
            <p><strong>Amount Paid:</strong> ${data.get('amount')}</p>
            <p><strong>Processed By:</strong> {data.get('service')}</p>
            <a href="/">Return to Product Catalog</a>
        </div>
        """
    except Exception as e:
        return f"""
        <div style="font-family: Arial; max-width: 500px; margin: 40px auto; padding: 25px; border: 1px solid #dc3545; border-radius: 8px;">
            <h2 style="color: #dc3545;">Payment Service Unreachable</h2>
            <p>Could not connect to <code>{PAYMENT_SERVICE_URL}</code></p>
            <p><strong>Error:</strong> {str(e)}</p>
            <a href="/">Return to Product Catalog</a>
        </div>
        """, 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)