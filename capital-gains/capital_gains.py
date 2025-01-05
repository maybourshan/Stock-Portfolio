from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

# Base URLs for stocks services
STOCKS1_URL = os.getenv("STOCKS1_URL", "http://stocks1:5001")
STOCKS2_URL = os.getenv("STOCKS2_URL", "http://stocks2:5002")

# Function to fetch stocks from a specific service
def fetch_stocks(service_url, filters=None):
    try:
        url = f"{service_url}/stocks"
        response = requests.get(url, params=filters)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching stocks: {e}")
        return []

@app.route("/capital-gains", methods=["GET"])
def calculate_capital_gains():
    # Query parameters
    portfolio = request.args.get('portfolio')
    numshares_gt = request.args.get('numsharesgt', type=int)
    numshares_lt = request.args.get('numshareslt', type=int)

    # Determine which portfolio to query
    stocks = []
    if portfolio == "stocks1":
        stocks = fetch_stocks(STOCKS1_URL)
    elif portfolio == "stocks2":
        stocks = fetch_stocks(STOCKS2_URL)
    else:
        stocks.extend(fetch_stocks(STOCKS1_URL))
        stocks.extend(fetch_stocks(STOCKS2_URL))

    # Filter stocks by number of shares
    if numshares_gt is not None:
        stocks = [stock for stock in stocks if stock['shares'] > numshares_gt]
    if numshares_lt is not None:
        stocks = [stock for stock in stocks if stock['shares'] < numshares_lt]

    # Calculate capital gains
    total_gains = 0
    gains_details = []
    for stock in stocks:
        current_price = stock.get('purchase price')  # Assuming purchase price is current price
        purchase_price = stock['purchase price']
        shares = stock['shares']
        gain = (current_price - purchase_price) * shares
        total_gains += gain
        gains_details.append({
            "symbol": stock["symbol"],
            "gain": round(gain, 2)
        })

    return jsonify({
        "total_gains": round(total_gains, 2),
        "details": gains_details
    }), 200

@app.route('/kill', methods=['GET'])
def kill_container():
    os._exit(1)

if __name__ == "__main__":
    port = os.getenv("PORT", 5003)
    app.run(host="0.0.0.0", port=port, debug=True)
