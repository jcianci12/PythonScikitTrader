import decimal
from pybit.unified_trading import WebSocket
from time import sleep, time
import csv
from TrainAndTest import trade_loop

from bybitapi import place_order
from functions.clock import call_decide_every_n_seconds
from generateTPandSL import calculate_prices, save_updated_prices
import asciichartpy
import threading


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
    orders = get_open_orders()
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
                po = place_order(testmode,"market","BTC/USDT", new_side,None,None
                            ,qty)
                closeprice = po['price']
                order['profit'] = ((closeprice - closeprice) * \
                    qty if side == 'buy' else (
                        takeprofitprice - closeprice) * (qty))
                # Set the flag to True
                changed = True
            elif (side == 'buy' and market_price <= stoplossprice) or (side == 'sell' and market_price >= stoplossprice):
                # Stop loss
                new_side = 'Sell' if side == 'buy' else 'buy'
                po = place_order(testmode,"market","BTC/USDT", new_side,takeprofitprice,stoplossprice,
                            qty)
                closeprice = po['price']

                order['profit'] = ((closeprice - closeprice) * \
                    qty if side == 'buy' else (
                        stoplossprice - closeprice) * (qty))
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
prices = []

def get_open_orders():
    global orders
    return orders

def print_orders():
    orders = get_open_orders()
    # Define the width of each column
    width = 10

    # Print the header
    print("TP".rjust(width) + "\t" + "SL".rjust(width))

    # Print the data
    for order in orders:
        if not order['profit']:
            # Format the numbers to two decimal places
            tp = "{:.2f}".format(float(order['takeprofitprice']))
            sl = "{:.2f}".format(float(order['stoplossprice']))
            print(tp.rjust(width) + "\t" + sl.rjust(width))
# Define the plot_ascii_chart function
def plot_ascii_chart(data):
    # Extract the usdIndexPrice from the data
    usd_index_price = float(data["data"]["usdIndexPrice"])

    # Append the usdIndexPrice to the global list
    global prices
    prices.append(usd_index_price)

    # Clear the console
    print("\033[H\033[J")
    print_orders()

    # Plot the prices using asciichart
    print(asciichartpy.plot(prices[-40:]))


# Define the handle_message function
def handle_message(message):
  print(message['data']['usdIndexPrice'])
  
  if 'topic' in message and message['topic'] == 'tickers.BTCUSDT':
    usdindexprice = message['data']['usdIndexPrice']
    if(usdindexprice!=''):
      last_price = float(message['data']['usdIndexPrice'])
      check_orders(True, "BTCUSDT", last_price)
      # Call the plot_ascii_chart function with the message as an argument
      plot_ascii_chart(message)

 
def startListening():
    getws().ticker_stream(
        symbol="BTCUSDT",
        callback=handle_message
    )
    
    while True:
        sleep(1)
        



# create two thread objects
t1 = threading.Thread(target=startListening)
t2 = threading.Thread(target=call_decide_every_n_seconds, args=(300, trade_loop))
t1.start()
t2.start()
# check_orders(True, "BTCUSDT", 30000)

