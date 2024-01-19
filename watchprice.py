from asyncio import sleep
import datetime
import time
from check_amount import check_amount

import asciichartpy
from binance import ThreadedWebsocketManager
from KEYS import API_KEY,API_SECRET
from api import  exchange, get_free_balance
from dbfuncs.dbops import fetchAllOrders, remove_closed_order_from_open_orders,  save_closed_order, setpending
from functions.logger import logger

from config import TRADINGPAIR

orders = []
order_refresh_time = 0
trade_refresh_time = 0
dblocked=0


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




    orders = fetchAllOrders()

    # Refresh the orders if it has been more than REFRESH_INTERVAL seconds since the last refresh
    # if (time.time() - order_refresh_time > REFRESH_INTERVAL):
    #     refresh_orders()
        
    # Check for open orders that have reached their take profit or stop loss prices
    for order in orders:
        if not order['profit']:
            entry_price = float(order['price'])
            take_profit_price = float(order['tp'])
            stop_loss_price = float(order['sl'])
            side = order['side'].lower()
            amount =   float(order['filled']) 
            new_side = SELL if side == BUY else BUY


            # Check if the market price has reached the take profit or stop loss prices
            if check_price_reached(market_price, take_profit_price, stop_loss_price, side):
                error_message = check_amount(amount,market_price,new_side)
                usdt = get_free_balance("USDT")
                btc = get_free_balance("BTC")
                # Close the order at the market price

                if(error_message ==None):
                    logger("Closing order ",order['clientOrderId'])
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
                                                #add the closed order to the table
                    save_closed_order(order)
                    #remove closed order from the orders table
                    remove_closed_order_from_open_orders(order)

                    # send_telegram_message(f"Order closed|Entry:{entry_price}|Close:{close_price}|Amount|{amount}|P+L:{profit}")
                else:
                    logger("Error",error_message)
                    profit = error_message
                    order['profit'] = profit
                    save_closed_order(order)
                    remove_closed_order_from_open_orders(order)

                    # send_telegram_message(f"Not enough to close|Entry:{entry_price}|Close:NA|Amount|{amount}|P+L:{profit}")


         
            # Save the updated orders back to the CSV file only if the flag is True



prices = []



def is_number(s):
    if s=='': return False
    try:
        float(s)
        return True
    except ValueError:
        return False
    
def print_orders(entry_price):
    orders = fetchAllOrders()
    # Define the width of each column
    width = 10

    # Print the header
    print("TP".rjust(width) + "\t" + "SL".rjust(width) + "\t" + "TP Dist.".rjust(width) + "\t" + "SL Dist.".rjust(width))

    # Print the data
    profit = 0
    for order in orders:
        if not order['profit']:
            # Format the numbers to two decimal places
            tp = "{:.2f}".format(float(order['tp']))
            sl = "{:.2f}".format(float(order['sl']))
            tp_dist = "{:.2f}".format(float(order['tp'])-entry_price)
            sl_dist = "{:.2f}".format(entry_price-float(order['sl']) )
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


# Define the handle_message function
def handle_message(message):
    # if(getpending()==1):
    #     return
    # setpending(1)
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
    # setpending(0)
def startListening():
    symbol = 'BTCUSDT'
    twm = ThreadedWebsocketManager(api_key=API_KEY, api_secret=API_SECRET)
    # start is required to initialise its internal loop
    twm.start()

    def handle_socket_message(msg):
        # print(f"message type: {msg}")
        # print(msg)
        if(msg['e']=='error' ):
            twm.stop()
    #check if pending
        else:
            sleep(5)
            handle_message(msg)  

    twm.start_kline_socket(callback=handle_socket_message, symbol=symbol)
    # twm.start_kline_socket(handle_socket_message_train, symbol,'5m')

    twm.join()   

startListening()
print("watchprice")