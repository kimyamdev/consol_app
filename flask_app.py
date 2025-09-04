from flask import Flask, jsonify, render_template
from ib_insync import *
import asyncio

app = Flask(__name__)

@app.route('/')
def index():
    return jsonify({'message': 'Welcome to the IBKR Connect App'})

@app.route('/positions')
def get_positions():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    ib = IB()
    ib.connect('127.0.0.1', 7496, clientId=1)
    positions = ib.positions()
    result = []

    for pos in positions:
        contract = pos.contract
        position_size = pos.position
        currency = contract.currency

        if contract.secType == 'CASH':
            contract.exchange = 'IDEALPRO'

        ib.qualifyContracts(contract)
        ticker = ib.reqMktData(contract, '', False, False)
        ib.sleep(1)

        last_price = ticker.last if ticker.last else ticker.close if ticker.close else 0.0
        value = round(position_size * last_price, 2)

        result.append({
            'ticker': contract.symbol,
            'quantity': position_size,
            'last_price': last_price,
            'position_value': value,
            'currency': currency
        })

    ib.disconnect()
    return jsonify(result)

import asyncio
from ib_insync import IB

@app.route("/test_connection")
def test_connection():
    # Create and set a new event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    ib = IB()
    try:
        # Attempt to connect to IBKR
        ib.connect('127.0.0.1', 7496, clientId=1)
        if ib.isConnected():
            print("Successfully connected to IBKR")
            return {"status": "Connected to IBKR"}, 200
        else:
            print("Failed to connect to IBKR")
            return {"error": "Failed to connect to IBKR"}, 500
    except Exception as e:
        print(f"Connection error: {e}")
        return {"error": "Connection error"}, 500
    finally:
        ib.disconnect()

@app.route("/transactions")
def get_transactions():
    # Replace with your actual Flex Query ID and token
    flexQueryId = '1284995'
    token = '259410711391663956502224'

    # Debug prints
    print(f"Query ID: {flexQueryId}")
    print(f"Token: {token[:10]}...")  # Print only part of the token for security

    try:
        # Create an instance of FlexReport
        flex_report = FlexReport()

        # Download the Flex Report using the instance
        report = flex_report.download(queryId=flexQueryId, token=token)

        if report is None:
            print("Failed to download report: Report is None")
            return {"error": "Failed to fetch transactions"}, 500

        transactions = report.transactions()
        return render_template("transactions.html", transactions=transactions)
    except Exception as e:
        print(f"Error: {e}")
        return {"error": "Failed to fetch transactions"}, 500

if __name__ == '__main__':
    app.run(debug=True)
