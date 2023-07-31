from bybitapi import exchange


# Set the symbol, order side, quantity, and prices
symbol = 'BTC/USDT'
side = 'sell'
quantity = 0.0004
price = 32000.07
stopPrice = 29283.03
stopLimitPrice = 29000.00
stopLimitTimeInForce = 'FOK'

# Place the OCO order
symbol = 'BTC/USDT'
market = exchange.market(symbol)
amount = 0.0004
price = 29000
stop_price = 31000
stop_limit_price = 28000

response = exchange.private_post_order_oco({
    'symbol': market['id'],
    'side': 'BUY',  # SELL, BUY
    'quantity': exchange.amount_to_precision(symbol, amount),
    'price': exchange.price_to_precision(symbol, price),
    'stopPrice': exchange.price_to_precision(symbol, stop_price),
    'stopLimitPrice': exchange.price_to_precision(symbol, stop_limit_price),  # If provided, stopLimitTimeInForce is required
    'stopLimitTimeInForce': 'GTC',  # GTC, FOK, IOC
    # 'listClientOrderId': exchange.uuid(),  # A unique Id for the entire orderList
    # 'limitClientOrderId': exchange.uuid(),  # A unique Id for the limit order
    # 'limitIcebergQty': exchangea.amount_to_precision(symbol, limit_iceberg_quantity),
    # 'stopClientOrderId': exchange.uuid()  # A unique Id for the stop loss/stop loss limit leg
    # 'stopIcebergQty': exchange.amount_to_precision(symbol, stop_iceberg_quantity),
    # 'newOrderRespType': 'ACK',  # ACK, RESULT, FULL
})
print(response)