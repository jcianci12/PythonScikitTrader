import asyncio
import decimal
from functools import partial
from pybit.unified_trading import WebSocket
from time import sleep, time
import csv
from TrainAndTest import trade_loop

from bybitapi import place_order
from generateTPandSL import calculate_prices, save_updated_prices
from get_last_ohlc_bybit import get_last_ohlc_binance

orders = []
order_refresh_time = 0
trade_refresh_time = 0


def refresh_orders():
    global orders
    global order_refresh_time
    global trade_refresh_time


    # Load the orders from the CSV file
    with open('orders.csv', mode='r') as orders_file:
        reader = csv.DictReader(orders_file)
        orders = list(reader)

    order_refresh_time = time()

def check_orders(testmode, symbol, market_price):
    global orders
    global trade_refresh_time
    print("check orders called")

    # Refresh the orders if it has been more than 5 seconds since the last refresh
    if time() - order_refresh_time > 5:
        refresh_orders()

    if time() - trade_refresh_time > 300:
        trade_loop()
        trade_refresh_time = time

    # Initialize a boolean flag to False
    changed = False

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
                # Set the flag to True
                changed = True
            elif (side == 'buy' and market_price <= stoplossprice) or (side == 'sell' and market_price >= stoplossprice):
                # Stop loss
                new_side = 'Sell' if side == 'buy' else 'buy'
                place_order(testmode,"market",symbol, new_side,
                            qty/market_price)
                order['profit'] = ((decimal.Decimal(market_price) - stoplossprice) * \
                    decimal.Decimal(qty) if side == 'buy' else (
                        stoplossprice - market_price) * (qty))/market_price
                # Set the flag to True
                changed = True

    # Save the updated orders back to the CSV file only if the flag is True
    if changed:
        save_updated_prices('orders.csv', orders)




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
 
def startListening():
    getws().ticker_stream(
        symbol="BTCUSDT",
        callback=handle_message
    )
    
    while True:
        sleep(1)
        

startListening()
# check_orders(True, "BTCUSDT", 30000)

