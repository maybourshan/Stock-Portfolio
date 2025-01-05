from flask import Flask, request, jsonify
from datetime import datetime
import os
import requests
import uuid
from pymongo import MongoClient

app = Flask(__name__)

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongodb:27017/")
SERVICE_NAME = os.getenv("SERVICE_NAME", "stocks1")  # Environment variable for service name
client = MongoClient(MONGO_URI)
db = client[f"{SERVICE_NAME}_db"]  # Database name based on service
stocks_collection = db['stocks']  # Collection name

# Read the API key from the environment variable
API_KEY = os.getenv("NINJA_API_KEY")

# Function to fetch stock price
def get_stock_price(symbol):
    url = f"https://api.api-ninjas.com/v1/stockprice?ticker={symbol}"
    try:
        response = requests.get(url, headers={'X-Api-Key': API_KEY})
        if response.status_code != 200:
            return None
        response.raise_for_status()
        data = response.json()
        if isinstance(data, dict) and 'price' in data:
            return data['price']
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching stock price: {e}")
        return None

# Root route
@app.route("/", methods=["GET"])
def home():
    return f"Welcome to the {SERVICE_NAME} Stock Portfolio Manager!"

# Managing stocks (GET and POST)
@app.route('/stocks', methods=['GET', 'POST'])
def manage_stocks():
    if request.method == 'GET':
        # Handle GET request to fetch stocks
        symbol_query = request.args.get('symbol')
        query = {"symbol": symbol_query} if symbol_query else {}
        stocks = stocks_collection.find(query, {"_id": 0})  # Fetch stocks from MongoDB
        return jsonify(list(stocks)), 200

    elif request.method == 'POST':
        # Add a log to print incoming data
        print(f"Received data: {request.json}")

        data = request.json
        if not all(k in data for k in ('symbol', 'purchase price', 'shares')):
            print("Malformed data received")
            return jsonify({"error": "Malformed data"}), 400

        # רשימת כל מסדי הנתונים (כולל התיק הנוכחי)
        dbs_to_check = ["stocks1_db", "stocks2_db"]
        print(f"Databases to check: {dbs_to_check}")

        # לולאה לבדוק אם הסימול כבר קיים בכל מסדי הנתונים
        for db_name in dbs_to_check:
            collection = client[db_name]['stocks']
            print(f"Checking database: {db_name}")
            existing_stock = collection.find_one({"symbol": data['symbol']})
            if existing_stock:
                print(f"Found duplicate stock in {db_name}: {existing_stock}")
                return jsonify({
                    "error": f"Stock with symbol '{data['symbol']}' already exists in portfolio '{db_name}'."
                }), 400

        # אם לא קיים, הוסף את המניה לתיק הנוכחי
        stock = {
            'id': str(uuid.uuid4()),
            'name': data.get('name', 'NA'),
            'symbol': data['symbol'],
            'purchase price': round(data['purchase price'], 2),
            'purchase date': data.get('purchase date', 'NA'),
            'shares': int(data['shares']),
        }
        stocks_collection.insert_one(stock)  # Save stock to MongoDB
        print(f"Added stock: {stock}")
        return jsonify({'id': stock['id']}), 201

# Managing a stock by ID (GET, PUT, DELETE)
@app.route('/stocks/<string:id>', methods=['GET', 'PUT', 'DELETE'])
def manage_stock_by_id(id):
    if request.method == "GET":
        # Fetch stock by ID
        stock = stocks_collection.find_one({"id": id}, {"_id": 0})
        if not stock:
            return jsonify({"error": "Not found"}), 404
        return jsonify(stock), 200

    elif request.method == "PUT":
        # Update stock by ID
        if request.content_type != 'application/json':
            return jsonify({"error": "Expected application/json media type"}), 415
        data = request.json
        stock = stocks_collection.find_one({"id": id})
        if not stock:
            return jsonify({"error": "Not found"}), 404
        update_data = {
            "name": data.get("name", stock["name"]),
            "symbol": data.get("symbol", stock["symbol"]).upper(),
            "purchase price": round(float(data.get("purchase price", stock["purchase price"])), 2),
            "purchase date": data.get("purchase date", stock["purchase date"]),
            "shares": int(data.get("shares", stock["shares"]))
        }
        stocks_collection.update_one({"id": id}, {"$set": update_data})  # Update stock in MongoDB
        return jsonify({"id": id}), 200

    elif request.method == "DELETE":
        # Delete stock by ID
        result = stocks_collection.delete_one({"id": id})
        if result.deleted_count == 0:
            return jsonify({"error": "Not found"}), 404
        return '', 204

# Calculate stock value by ID
@app.route("/stock-value/<string:id>", methods=["GET"])
def stock_value(id):
    stock = stocks_collection.find_one({"id": id})
    if not stock:
        return jsonify({"error": "Not found"}), 404
    price = get_stock_price(stock["symbol"])
    if price is None:
        return jsonify({"server error": "Unable to fetch stock price"}), 500
    stock_value = round(price * stock["shares"], 2)
    return jsonify({
        "symbol": stock["symbol"],
        "ticker": price,
        "stock value": stock_value
    }), 200

# Calculate total portfolio value
@app.route("/portfolio-value", methods=["GET"])
def portfolio_value():
    total_value = 0
    stocks = stocks_collection.find({}, {"_id": 0})  # Fetch all stocks
    for stock in stocks:
        price = get_stock_price(stock["symbol"])
        if price is None:
            return jsonify({"server error": f"Unable to fetch stock price for {stock['symbol']}"}), 500
        stock_value = price * stock["shares"]
        total_value += stock_value
    current_date = datetime.now().strftime("%d-%m-%Y")
    return jsonify({
        "date": current_date,
        "portfolio value": round(total_value, 2)
    }), 200

@app.route('/kill', methods=['GET'])
def kill_container():
    os._exit(1)

if __name__ == "__main__":
    port = os.getenv("PORT", 5001)
    app.run(host='0.0.0.0', port=port, debug=True)