from pybit.unified_trading import WebSocket
from time import time
import csv
from check_amount import check_amount, get_amount

from generateTPandSL import save_updated_prices
import asciichartpy
from binance import ThreadedWebsocketManager
from KEYS import API_KEY,API_SECRET
from bybitapi import exchange, get_free_balance





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


# Define constants
REFRESH_INTERVAL = 5
BUY = 'buy'
SELL = 'sell'

# Define a function to calculate the profit or loss
def calculate_profit_loss(entry_price, close_price, side, amount):
    if side == BUY:
        return (close_price - entry_price) * amount
    elif side == SELL:
        return (entry_price - close_price) * amount

# Define a function to check if the market price has reached the take profit or stop loss prices
def check_price_reached(market_price, take_profit_price, stop_loss_price, side):
    if side == BUY:
        return market_price >= take_profit_price or market_price <= stop_loss_price
    elif side == SELL:
        return market_price <= take_profit_price or market_price >= stop_loss_price

def check_orders(testmode, symbol, market_price):
    orders = get_open_orders()

    # Refresh the orders if it has been more than REFRESH_INTERVAL seconds since the last refresh
    if time() - order_refresh_time > REFRESH_INTERVAL:
        refresh_orders()
        
    # Initialize a boolean flag to False
    changed = False

    # Check for open orders that have reached their take profit or stop loss prices
    for order in orders:
        if not order['profit']:
            entry_price = float(order['entryprice'])
            take_profit_price = float(order['takeprofitprice'])
            stop_loss_price = float(order['stoplossprice'])
            side = order['side'].lower()
            amount =   float(order['qty'])
            
            # Check if the market price has reached the take profit or stop loss prices
            if check_price_reached(market_price, take_profit_price, stop_loss_price, side):
                # Close the order at the market price
                new_side = SELL if side == BUY else BUY
                amount = get_amount(amount,new_side,market_price)
                enough = check_amount(amount,market_price,new_side)

                if(enough):
                    order_result = exchange.create_market_order(symbol,new_side,amount)
                    close_price = order_result['price']
                    # Calculate the profit or loss
                    order['profit'] = calculate_profit_loss(entry_price, close_price, side, amount)
                else:
                    order['profit'] = "Not enough"

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
# Define the plot_ascii_chart function
def plot_ascii_chart(data):
    # Extract the usdIndexPrice from the data
    usd_index_price = float(data['k']['c'])

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
    print(message['k']['c'])
  
#   if 'topic' in message and message['topic'] == 'tickers.BTCUSDT':
    usdindexprice = message['k']['c']
    if(usdindexprice!=''):
        last_price = float(message['k']['c'])
        check_orders(True, "BTCUSDT", last_price)
        # Call the plot_ascii_chart function with the message as an argument
        plot_ascii_chart(message)

def startListening():

    symbol = 'BTCUSDT'

    twm = ThreadedWebsocketManager(api_key=API_KEY, api_secret=API_SECRET)
    # start is required to initialise its internal loop
    twm.start()

    def handle_socket_message(msg):
        # print(f"message type: {msg}")
        # print(msg)
        handle_message(msg)

    twm.start_kline_socket(callback=handle_socket_message, symbol=symbol)

    # multiple sockets can be started
    # twm.start_depth_socket(callback=handle_socket_message, symbol=symbol)

    # or a multiplex socket can be started like this
    # see Binance docs for stream names
    twm.join()







startListening()
