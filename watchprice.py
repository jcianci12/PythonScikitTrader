from asyncio import sleep
import datetime
from time import time
import csv
from check_amount import check_amount, Adjust_Amount_for_fees
from config import ORDERCOLUMNS

import asciichartpy
from binance import ThreadedWebsocketManager
from KEYS import API_KEY,API_SECRET
from api import exchange, get_free_balance
from functions.logger import logger
from messengerservice import send_telegram_message

from config import TRADINGPAIR
from pending import getpending, setpending


orders = []
order_refresh_time = 0
trade_refresh_time = 0

def save_updated_prices(conn, orders):
    """ Save updated prices to the SQLite database """
    try:
        cur = conn.cursor()
        for order in orders:
            cur.execute('''
                UPDATE orders SET
                datetime = ?,
                symbol = ?,
                side = ?,
                usdtbalance = ?,
                btcbalance = ?,
                totalbalance = ?,
                filled = ?,
                price = ?,
                tp = ?,
                sl = ?,
                column1 = ?,
                column2 = ?,
                column3 = ?
                WHERE clientOrderId = ?
            ''', (
                order['datetime'],
                order['symbol'],
                order['side'],
                order['usdtbalance'],
                order['btcbalance'],
                order['totalbalance'],
                order['filled'],
                order['price'],
                order['tp'],
                order['sl'],
                order['column1'],
                order['column2'],
                order['column3'],
                order['clientOrderId']
            ))
        conn.commit()
    except Error as e:
        print(e)

def refresh_orders(conn):
    """ Refresh orders from the SQLite database """
    global orders
    global order_refresh_time

    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM orders")
        rows = cur.fetchall()

        # Convert rows to list of dictionaries
        orders = [dict(zip([column[0] for column in cur.description], row)) for row in rows]

        order_refresh_time = time()
    except Error as e:
        print(e)


# Define constants
REFRESH_INTERVAL = 5
BUY = 'buy'
SELL = 'sell'

# Define a function to calculate the profit or loss
def calculate_profit_loss(entry_price, close_price, side, amount,fee):
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
    
    while getpending()==True:
        logger("there is a pending order.... returning.")
        return
    
    print("Pending http orders:",getpending())

    orders = get_open_orders()

    # Refresh the orders if it has been more than REFRESH_INTERVAL seconds since the last refresh
    if time() - order_refresh_time > REFRESH_INTERVAL:
        refresh_orders(create_connection())
        
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
            new_side = SELL if side == BUY else BUY


            # Check if the market price has reached the take profit or stop loss prices
            if check_price_reached(market_price, take_profit_price, stop_loss_price, side):
                error_message = check_amount(amount,market_price,new_side)
                usdt = get_free_balance("USDT")
                btc = get_free_balance("BTC")
                # Close the order at the market price
                setpending(True)

                if(error_message ==None):
                    logger("Closing order ",order['uid'])
                    try:
                        order_result = exchange.create_market_order(symbol, new_side, amount)
                        logger("Order closed:",order_result)
                        fee =order_result['fees'][0]['cost']
                        close_price = order_result['price']
                        # Calculate the profit or loss
                        profit= calculate_profit_loss(entry_price, close_price, side, amount,fee)
                        order['profit'] = profit
                        order['exitprice'] = close_price
                        profit =  order['profit']
                        order["usdt"]=usdt
                        order['btc']=btc
                        order['total']=(usdt+(btc*close_price))
                    except Exception as e:
                            logger("Error:", e)
                            order['profit']=e
                    

                    # send_telegram_message(f"Order closed|Entry:{entry_price}|Close:{close_price}|Amount|{amount}|P+L:{profit}")
                else:
                    logger("Error",error_message)
                    profit = error_message
                    order['profit'] = profit
                    # send_telegram_message(f"Not enough to close|Entry:{entry_price}|Close:NA|Amount|{amount}|P+L:{profit}")
                setpending(False)


                # Set the flag to True
                changed = True
            # Save the updated orders back to the CSV file only if the flag is True
    if changed:
        save_updated_prices(create_connection(), orders)

    PENDINGORDER = False

prices = []

def get_open_orders():
    global orders
    return orders

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False
    
def print_orders(entry_price):
    orders = get_open_orders()
    # Define the width of each column
    width = 10

    # Print the header
    print("TP".rjust(width) + "\t" + "SL".rjust(width) + "\t" + "TP Dist.".rjust(width) + "\t" + "SL Dist.".rjust(width))

    # Print the data
    profit = 0
    for order in orders:
        if not order['profit']:
            # Format the numbers to two decimal places
            tp = "{:.2f}".format(float(order['takeprofitprice']))
            sl = "{:.2f}".format(float(order['stoplossprice']))
            tp_dist = "{:.2f}".format(float(order['takeprofitprice'])-entry_price)
            sl_dist = "{:.2f}".format(entry_price-float(order['stoplossprice']) )
            print(tp.rjust(width) + "\t" + sl.rjust(width) + "\t" + tp_dist.rjust(width) + "\t" + sl_dist.rjust(width))

        if  is_number(order['profit']):
            profit+=    float(order['profit'])    
    
    print("PROFIT")
    print(profit)





# Define the plot_ascii_chart function
# Define the plot_ascii_chart function
def plot_ascii_chart(data):
    # Extract the usdIndexPrice from the data
    usd_index_price = float(data['k']['c'])

    # Append the usdIndexPrice to the global list
    global prices
    prices.append(usd_index_price)


    
    # Plot the prices using asciichart
    print(asciichartpy.plot(prices[-40:]))
    print("Pending http orders:",getpending())


# Define the handle_message function
def handle_message(message):
    print(message['k']['c'])
  
#   if 'topic' in message and message['topic'] == 'tickers.BTCUSDT':
    usdindexprice = message['k']['c']
    if(usdindexprice!=''):
        last_price = float(message['k']['c'])
        if(last_price!=None):
            check_orders(True, TRADINGPAIR, last_price)
        # Call the plot_ascii_chart function with the message as an argument
            # Clear the console
        print("\033[H\033[J")
        print_orders(last_price)
        plot_ascii_chart(message)
        print(datetime.datetime.now())

def startListening():
    symbol = 'BTCUSDT'
    twm = ThreadedWebsocketManager(api_key=API_KEY, api_secret=API_SECRET)
    # start is required to initialise its internal loop
    twm.start()

    def handle_socket_message(msg):
        # print(f"message type: {msg}")
        # print(msg)
        if(msg['e']!='error' ):
            twm.stop()
            handle_message(msg)
            twm.start_kline_socket(callback=handle_socket_message, symbol=symbol)

    twm.start_kline_socket(callback=handle_socket_message, symbol=symbol)

    # multiple sockets can be started
    # twm.start_depth_socket(callback=handle_socket_message, symbol=symbol)

    # or a multiplex socket can be started like this
    # see Binance docs for stream names
    twm.join()


startListening()
