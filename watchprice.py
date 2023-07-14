from pybit.unified_trading import WebSocket
from time import sleep, time
import csv

from bybitapi import place_order

orders = []
last_refresh_time = 0


def refresh_orders():
    global orders
    global last_refresh_time

    # Load the orders from the CSV file
    with open('orders.csv', mode='r') as orders_file:
        reader = csv.DictReader(orders_file)
        orders = list(reader)

    last_refresh_time = time()


def check_orders(testmode, symbol, market_price):
    global orders
    global last_refresh_time

    # Refresh the orders if it has been more than 5 seconds since the last refresh
    if time() - last_refresh_time > 5:
        refresh_orders()

    # Check for open orders that have reached their take profit or stop loss prices
    for order in orders:
        if not order['profit']:
            takeprofitprice = float(order['takeprofitprice'])
            stoplossprice = float(order['stoplossprice'])
            side = order['side']
            qty = float(order['qty'])

            if (side == 'Buy' and market_price >= takeprofitprice) or (side == 'Sell' and market_price <= takeprofitprice):
                # Take profit
                new_side = 'Sell' if side == 'Buy' else 'Buy'
                place_order(testmode, symbol, new_side,
                            takeprofitprice, stoplossprice, qty)
                order['profit'] = (market_price - takeprofitprice) * \
                    qty if side == 'Buy' else (
                        takeprofitprice - market_price) * qty
            elif (side == 'Buy' and market_price <= stoplossprice) or (side == 'Sell' and market_price >= stoplossprice):
                # Stop loss
                new_side = 'Sell' if side == 'Buy' else 'Buy'
                place_order(testmode, symbol, new_side,
                            takeprofitprice, stoplossprice, qty)
                order['profit'] = (market_price - stoplossprice) * \
                    qty if side == 'Buy' else (
                        stoplossprice - market_price) * qty

    # Save the updated orders back to the CSV file
    with open('orders.csv', mode='w') as orders_file:
        fieldnames = ['uid', 'symbol', 'side', 'qty',
                      'takeprofitprice', 'stoplossprice', 'profit']
        writer = csv.DictWriter(orders_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(orders)


def getws():

    return WebSocket(
        testnet=True,
        channel_type="spot",
    )


def handle_message(message):
    if 'topic' in message and message['topic'] == 'tickers.BTCUSDT':
        last_price = float(message['data']['lastPrice'])
        # print(last_price)
        check_orders(True, "BTCUSDT", last_price)


getws().ticker_stream(
    symbol="BTCUSDT",
    callback=handle_message
)

# while True:
#     sleep(1)
