import asyncio
import decimal
from functools import partial
from pybit.unified_trading import WebSocket
from time import sleep, time
import csv

from bybitapi import place_order
from generateTPandSL import calculate_prices, save_updated_prices
from get_last_ohlc_bybit import get_last_ohlc_binance

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
def caller(callback):
    callback()

def check_orders(testmode, symbol, market_price):
    global orders
    global last_refresh_time
    print("check orders called")

    # Refresh the orders if it has been more than 5 seconds since the last refresh
    if time() - last_refresh_time > 5:
        refresh_orders()

    # Check for open orders that have reached their take profit or stop loss prices
    for order in orders:
        if not order['profit']:
            # ohlc = get_last_ohlc_bybit(symbol,"5")
            entry_price = float(order['entryprice'])
            takeprofitprice, stoplossprice = calculate_prices(entry_price, None )
            side = order['side'].lower()
            qty = float(order['qty'])

            if (side == 'buy' and market_price >= takeprofitprice) or (side == 'sell' and market_price <= takeprofitprice):
                # Take profit
                new_side = 'Sell' if side == 'buy' else 'buy'
                place_order(testmode,"market",symbol, new_side,
                            qty/market_price)
                order['profit'] = ((decimal.Decimal(market_price) - stoplossprice) * \
                    decimal.Decimal(qty) if side == 'buy' else (
                        takeprofitprice - market_price) * (qty))/market_price
            elif (side == 'buy' and market_price <= stoplossprice) or (side == 'sell' and market_price >= stoplossprice):
                # Stop loss
                new_side = 'Sell' if side == 'buy' else 'buy'
                place_order(testmode,"market",symbol, new_side,
                            qty/market_price)
                order['profit'] = ((decimal.Decimal(market_price) - stoplossprice) * \
                    decimal.Decimal(qty) if side == 'buy' else (
                        stoplossprice - market_price) * (qty))/market_price

    # Save the updated orders back to the CSV file
    save_updated_prices('orders.csv', orders)

def test():
    print("Hi!")

def getws():

    return WebSocket(
        testnet=True,
        channel_type="spot",
    )


def handle_message(message):
    print(message)
    

    if 'topic' in message and message['topic'] == 'tickers.BTCUSDT':
        last_price = float(message['data']['lastPrice'])
        check_orders(True, "BTCUSDT", last_price)
        test()
 
def startListening():
    getws().ticker_stream(
        symbol="BTCUSDT",
        callback=handle_message
    )
    
    while True:
        sleep(1)
        

# startListening()
# check_orders(True, "BTCUSDT", 30000)

