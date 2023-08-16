import decimal
from pybit.unified_trading import WebSocket
from time import sleep, time
import csv

from bybitapi import place_order
from generateTPandSL import calculate_prices, save_updated_prices

orders = []
order_refresh_time = 0
trade_refresh_time = 0


def refresh_orders():
    global orders
    global order_refresh_time


    # Load the orders from the CSV file
    with open('orders.csv', mode='r') as orders_file:
        reader = csv.DictReader(orders_file)
        orders = list(reader)

    order_refresh_time = time()

def check_orders(testmode, symbol, market_price):
    global orders
    print("check orders called")

    # Refresh the orders if it has been more than 5 seconds since the last refresh
    if time() - order_refresh_time > 5:
        refresh_orders()

   

    # Initialize a boolean flag to False
    changed = False

    # Check for open orders that have reached their take profit or stop loss prices
    for order in orders:
        if not order['profit']:
            # ohlc = get_last_ohlc_bybit(symbol,"5")
            entry_price = float(order['entryprice'])
            takeprofitprice = float(order['takeprofitprice'])
            stoplossprice = float(order['stoplossprice'])
            side = order['side'].lower()
            qty =   float(order['qty'])

            if (side == 'buy' and market_price >= takeprofitprice) or (side == 'sell' and market_price <= takeprofitprice):
                # Take profit
                new_side = 'Sell' if side == 'buy' else 'buy'
                place_order(testmode,"market","BTC/USDT", new_side,
                            qty)
                order['profit'] = ((market_price - stoplossprice) * \
                    qty if side == 'buy' else (
                        takeprofitprice - market_price) * (qty))
                # Set the flag to True
                changed = True
            elif (side == 'buy' and market_price <= stoplossprice) or (side == 'sell' and market_price >= stoplossprice):
                # Stop loss
                new_side = 'Sell' if side == 'buy' else 'buy'
                place_order(testmode,"market","BTC/USDT", new_side,takeprofitprice,stoplossprice,
                            qty)
                order['profit'] = ((market_price - stoplossprice) * \
                    qty if side == 'buy' else (
                        stoplossprice - market_price) * (qty))
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

