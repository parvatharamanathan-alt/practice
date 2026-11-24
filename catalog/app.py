import os
import requests
from flask import Flask, request, render_template_string

app = Flask(__name__)

# Matches your Terraform Cloud Map Service Discovery DNS
PAYMENT_SERVICE_URL = os.getenv(
    "PAYMENT_SERVICE_URL",
    "http://containerconnection.habibi.dxb.local:5000/pay"
)

PRODUCTS = [
    {
        "id": 1,
        "name": "Wireless Headphones",
        "price": 99.99,
        "badge": "Best Seller",
        "badge_color": "#ff4757",
        "desc": "Noise-canceling over-ear headphones with 30h battery",
        "image": "/static/headphones.png",
    },
    {
        "id": 2,
        "name": "Smart Watch",
        "price": 149.99,
        "badge": "New Arrival",
        "badge_color": "#1e90ff",
        "desc": "AMOLED fitness tracker with heart-rate & GPS monitor",
        "image": "/static/smartwatch.png",
    },
    {
        "id": 3,
        "name": "Mechanical Keyboard",
        "price": 79.99,
        "badge": "Hot Deal",
        "badge_color": "#ffa502",
        "desc": "Compact RGB backlit tactile gaming & coding keyboard",
        "image": "/static/keyboard.png",
    },
]

CATALOG_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>ShoppersStop - Online Store</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #fdfbfb 0%, #ebedee 100%);
            min-height: 100vh;
            color: #2f3542;
        }
        header {
            background: linear-gradient(90deg, #ff6b6b, #845ec2, #00c9a7);
            color: white;
            padding: 36px 20px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
        }
        header h1 {
            font-size: 2.8em;
            letter-spacing: 1.5px;
            text-shadow: 0 2px 6px rgba(0,0,0,0.2);
        }
        header p {
            margin-top: 8px;
            font-size: 1.1em;
            opacity: 0.95;
        }
        .container {
            max-width: 1050px;
            margin: 40px auto;
            padding: 0 20px 50px;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 28px;
        }
        .card {
            background: white;
            border-radius: 16px;
            overflow: hidden;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
            transition: transform 0.25s ease, box-shadow 0.25s ease;
            display: flex;
            flex-direction: column;
            position: relative;
        }
        .card:hover {
            transform: translateY(-8px);
            box-shadow: 0 14px 32px rgba(132, 94, 194, 0.22);
        }
        .badge {
            position: absolute;
            top: 14px;
            left: 14px;
            color: white;
            font-size: 0.78em;
            font-weight: bold;
            padding: 5px 12px;
            border-radius: 20px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.2);
        }
        .card img {
            width: 100%;
            height: 220px;
            object-fit: cover;
            display: block;
        }
        .card-body {
            padding: 22px;
            text-align: center;
            flex-grow: 1;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }
        .card-body h3 {
            font-size: 1.35em;
            color: #2f3542;
            margin-bottom: 8px;
        }
        .card-body p {
            color: #57606f;
            font-size: 0.95em;
            line-height: 1.4;
        }
        .price {
            font-size: 1.65em;
            font-weight: bold;
            color: #845ec2;
            margin: 16px 0;
        }
        .btn {
            display: inline-block;
            background: linear-gradient(90deg, #ff6b6b, #ff9f43);
            color: white;
            padding: 12px 26px;
            text-decoration: none;
            border-radius: 30px;
            font-weight: bold;
            font-size: 1em;
            transition: opacity 0.2s ease, transform 0.2s ease;
            box-shadow: 0 4px 12px rgba(255, 107, 107, 0.35);
        }
        .btn:hover {
            opacity: 0.92;
            transform: scale(1.03);
        }
    </style>
</head>
<body>
    <header>
        <h1>ShoppersStop</h1>
        <p>Your Colorful Tech & Lifestyle Destination</p>
    </header>
    <div class="container">
        <div class="grid">
            {% for p in products %}
            <div class="card">
                <span class="badge" style="background: {{ p.badge_color }};">{{ p.badge }}</span>
                <img src="{{ p.image }}" alt="{{ p.name }}">
                <div class="card-body">
                    <div>
                        <h3>{{ p.name }}</h3>
                        <p>{{ p.desc }}</p>
                    </div>
                    <div>
                        <div class="price">${{ "%.2f"|format(p.price) }}</div>
                        <a class="btn" href="/payment?name={{ p.name }}&price={{ p.price }}">Buy Now</a>
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
</body>
</html>
"""

PAYMENT_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>ShoppersStop - Checkout</title>
    <style>
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #845ec2 0%, #00c9a7 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0;
            padding: 20px;
        }
        .box {
            background: white;
            padding: 32px;
            border-radius: 16px;
            box-shadow: 0 12px 32px rgba(0,0,0,0.2);
            max-width: 440px;
            width: 100%;
        }
        h2 { color: #845ec2; margin-top: 0; text-align: center; }
        .summary {
            background: #f8f9fa;
            padding: 14px;
            border-radius: 10px;
            border-left: 4px solid #ff6b6b;
            margin-bottom: 18px;
        }
        label { font-weight: bold; font-size: 0.9em; color: #2f3542; }
        input {
            width: 100%;
            padding: 11px;
            margin: 8px 0 16px;
            box-sizing: border-box;
            border: 1px solid #ced6e0;
            border-radius: 8px;
            font-size: 0.95em;
        }
        button {
            width: 100%;
            background: linear-gradient(90deg, #00c9a7, #00b894);
            color: white;
            padding: 13px;
            border: none;
            border-radius: 30px;
            font-size: 1.05em;
            font-weight: bold;
            cursor: pointer;
            box-shadow: 0 4px 12px rgba(0, 201, 167, 0.35);
        }
        button:hover { opacity: 0.92; }
        .back { text-align: center; margin-top: 16px; }
        .back a { color: #845ec2; text-decoration: none; font-weight: bold; }
    </style>
</head>
<body>
    <div class="box">
        <h2>ShoppersStop Checkout</h2>
        <div class="summary">
            <p style="margin: 4px 0;"><strong>Product:</strong> {{ name }}</p>
            <p style="margin: 4px 0;"><strong>Total Amount:</strong> ${{ price }}</p>
        </div>
        <form action="/process-payment" method="POST">
            <input type="hidden" name="name" value="{{ name }}">
            <input type="hidden" name="price" value="{{ price }}">
            <label>Cardholder Name</label>
            <input type="text" name="customer" placeholder="John Doe" required>
            <label>Card Number (Test)</label>
            <input type="text" name="card" placeholder="4111-1111-1111-1111" required>
            <button type="submit">Confirm & Pay ${{ price }}</button>
        </form>
        <div class="back"><a href="/">&larr; Back to ShoppersStop</a></div>
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
        response = requests.post(PAYMENT_SERVICE_URL, json=payload, timeout=5)
        data = response.json()
        return f"""
        <div style="font-family: 'Segoe UI', Arial; max-width: 500px; margin: 60px auto; padding: 30px; background: #f0fff4; border: 2px solid #00c9a7; border-radius: 16px; text-align: center;">
            <h2 style="color: #00b894;">Payment Successful!</h2>
            <p><strong>Store:</strong> ShoppersStop</p>
            <p><strong>Transaction ID:</strong> {data.get('transaction_id')}</p>
            <p><strong>Item:</strong> {data.get('item')}</p>
            <p><strong>Amount Paid:</strong> ${data.get('amount')}</p>
            <p><strong>Processed By:</strong> {data.get('service')}</p>
            <a href="/" style="display:inline-block; margin-top:15px; padding:10px 22px; background:#845ec2; color:white; text-decoration:none; border-radius:25px;">Continue Shopping</a>
        </div>
        """
    except Exception as e:
        return f"""
        <div style="font-family: 'Segoe UI', Arial; max-width: 500px; margin: 60px auto; padding: 30px; background: #fff5f5; border: 2px solid #ff4757; border-radius: 16px; text-align: center;">
            <h2 style="color: #ff4757;">Payment Service Unreachable</h2>
            <p>Could not connect to <code>{PAYMENT_SERVICE_URL}</code></p>
            <p><strong>Error:</strong> {str(e)}</p>
            <a href="/" style="display:inline-block; margin-top:15px; padding:10px 22px; background:#845ec2; color:white; text-decoration:none; border-radius:25px;">Return to ShoppersStop</a>
        </div>
        """, 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
