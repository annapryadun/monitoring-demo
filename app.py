from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from prometheus_client import Counter, Histogram, Gauge, generate_latest, REGISTRY
import random
import time
import os

app = Flask(__name__)
CORS(app)

# Define Prometheus metrics
REQUESTS = Counter('erp_requests_total', 'Total ERP requests', ['endpoint'])
RESPONSE_TIME = Histogram('erp_response_time_seconds', 'Response time in seconds', ['endpoint'])
ACTIVE_USERS = Gauge('erp_active_users', 'Number of active users')
INVENTORY_LEVEL = Gauge('erp_inventory_level', 'Current inventory level')

# Initialize with random values
ACTIVE_USERS.set(random.randint(50, 200))
INVENTORY_LEVEL.set(random.randint(1000, 5000))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/sales', methods=['POST'])
def create_sale():
    REQUESTS.labels(endpoint='/sales').inc()
    with RESPONSE_TIME.labels(endpoint='/sales').time():
        time.sleep(random.uniform(0.1, 0.5))
        sale_amount = random.randint(1, 10)
        current_inventory = INVENTORY_LEVEL._value.get()
        new_inventory = max(0, current_inventory - sale_amount)
        INVENTORY_LEVEL.set(new_inventory)
        return jsonify({"status": "success", "message": f"Sale of {sale_amount} items recorded"}), 201

@app.route('/inventory', methods=['GET'])
def get_inventory():
    REQUESTS.labels(endpoint='/inventory').inc()
    with RESPONSE_TIME.labels(endpoint='/inventory').time():
        time.sleep(random.uniform(0.05, 0.2))
        current_inventory = INVENTORY_LEVEL._value.get()
        fluctuation = random.randint(-5, 5)
        new_inventory = max(0, current_inventory + fluctuation)
        INVENTORY_LEVEL.set(new_inventory)
        return jsonify({"inventory_level": new_inventory}), 200

@app.route('/users', methods=['GET'])
def get_users():
    REQUESTS.labels(endpoint='/users').inc()
    with RESPONSE_TIME.labels(endpoint='/users').time():
        time.sleep(random.uniform(0.05, 0.2))
        current_users = ACTIVE_USERS._value.get()
        change = random.randint(-10, 10)
        new_users = max(0, current_users + change)
        ACTIVE_USERS.set(new_users)
        return jsonify({"active_users": new_users}), 200

@app.route('/metrics')
def metrics():
    return generate_latest(REGISTRY), 200, {'Content-Type': 'text/plain'}

if __name__ == '__main__':
    # Use 0.0.0.0 to bind to all interfaces
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8081)), debug=True)