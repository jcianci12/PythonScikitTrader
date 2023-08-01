from bybitapi import exchange, place_order
from config import TEST
from generateTPandSL import calculate_prices

tp,sl = calculate_prices(None)
place_order(TEST,"","BTC/USDT","BUY",tp,sl,0.0004)

# # Place the OCO order
# symbol = 'BTC/USDT'
# market = exchange.market(symbol)
# amount = 0.0004
# price = 29000
# stop_price = 31000
# stop_limit_price = 28000

# buyresponse = exchange.create_market_buy_order(
#     market['id'],
#     amount
# )
# print(buyresponse)
# response = exchange.private_post_order_oco({
#     'symbol': market['id'],
#     'side': 'SELL',  # SELL, BUY
#     'quantity': exchange.amount_to_precision(symbol, amount),
#     'price': exchange.price_to_precision(symbol, price),
#     'stopPrice': exchange.price_to_precision(symbol, stop_limit_price),
#     'stopLimitPrice': exchange.price_to_precision(symbol, stop_price),  # If provided, stopLimitTimeInForce is required
#     'stopLimitTimeInForce': 'GTC',  # GTC, FOK, IOC
# })
# print(response)