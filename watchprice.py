from pybit.unified_trading import WebSocket
from time import sleep, time
import csv

from bybitapi import place_order
from generateTPandSL import calculate_prices, save_updated_prices

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

def check_orders(testmode, symbol, market_price, ohlc):
    global orders
    global last_refresh_time

    # Refresh the orders if it has been more than 5 seconds since the last refresh
    if time() - last_refresh_time > 5:
        refresh_orders()

    # Check for open orders that have reached their take profit or stop loss prices
    for order in orders:
        if not order['profit']:
            entry_price = float(order['entryprice'])
            takeprofitprice, stoplossprice = calculate_prices(entry_price, ohlc)
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
    save_updated_prices('orders.csv', orders)




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
