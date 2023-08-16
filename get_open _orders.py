import time
from bybitapi import exchange

def fetch_open_orders(symbol,minutes):
    orders = exchange.fetch_open_orders(symbol)
    # Get the current timestamp in milliseconds
    now = int(time.time() * 1000)
    # Filter the orders that are older than 5 minutes
    old_orders = [order for order in orders if now - order['timestamp'] > 5 * 60 * 1000]

    return old_orders
def closeorder(id:str):
    exchange.cancel_order(id)

def close_orders_older_than(float: minutes):
    orders = fetch_open_orders(symbol,minutes)
    for o in orders:
        closeorder()

symbol = 'BTC/USDT'
fetch_open_orders(symbol)
