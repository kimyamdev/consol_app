from flask import Flask, jsonify
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

if __name__ == '__main__':
    app.run(debug=True)
