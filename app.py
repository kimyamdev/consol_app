from ib_insync import *

# Connect to TWS or IB Gateway (port 7497 = TWS, 7496 = Gateway)
ib = IB()
ib.connect('127.0.0.1', 7496, clientId=1)

positions = ib.positions()
result = []

for pos in positions:
    contract = pos.contract
    position_size = pos.position
    currency = contract.currency

    # Fix for FX positions
    if contract.secType == 'CASH':
        contract.exchange = 'IDEALPRO'

    # Qualify to ensure exchange and conId are filled
    ib.qualifyContracts(contract)

    # Request market data
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

# Print result
for r in result:
    print(r)