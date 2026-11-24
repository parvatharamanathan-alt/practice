import uuid
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"}), 200

@app.route('/pay', methods=['POST'])
def pay():
    data = request.get_json() or {}
    return jsonify({
        "status": "Approved",
        "transaction_id": f"TXN-{uuid.uuid4().hex[:8].upper()}",
        "item": data.get("item", "N/A"),
        "amount": data.get("amount", "0.00"),
        "customer": data.get("customer", "Guest"),
        "service": "Private Payment ECS Microservice"
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)