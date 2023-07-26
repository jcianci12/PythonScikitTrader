import asyncio
import csv
import datetime

import ccxt
from KEYS import API_KEY, API_SECRET
from bybitapi import cancel_order, get_session
# from pybit.unified_trading import HTTP

from config import ORDERCOLUMNS, TEST
from functions.logger import logger
from bybitapi import exchange
def check_closed_orders():

    closed_orders = exchange.fetchClosedOrders()
    canceled_orders = exchange.fetch_canceled_orders()
    closed_orders = closed_orders+canceled_orders    # open_orders = exchange.fetch_open_orders()


    # Read the order details from the CSV file
    with open('orders.csv', mode='r') as file:
        reader = csv.DictReader(file)
        orders = list(reader)
    # print("closed orders:")
    # for number in closed_orders:
    #             print(number['info']['orderId'])
    # Check the status of each order
    for order in orders:
        # Get a list of historical orders
        
        # print (order_history)
        if(order["profit"]==''):
            
            # Check if the take profit and stop loss orders have been executed
            take_profit_executed = any( o['id'] == order['takeprofitid'] and (o['status'] == 'closed'or o['status']=='canceled') for o in closed_orders)
            stop_loss_executed = any(o['id'] == order['stoplossid'] and (o['status'] == 'closed'or o['status']=='canceled') for o in closed_orders)       
            

            # Cancel the other order if one is executed
            if take_profit_executed:
                logger("take profit executed, cancelling order",order["uid"])
                cancel_order("BTCUSDT",order['stoplossid'])
                
                # Calculate the profit
                profit = float(order['takeprofitprice']) - float(order['entryprice'])
                
                # Update the CSV file with the profit and completed time
                order['profit'] = profit
                order['completedtime'] = datetime.datetime.now()

            elif stop_loss_executed:
                logger("stop loss executed, cancelling order",order["uid"])
                cancel_order("BTCUSDT",order['takeprofitid'])
                
                # Calculate the profit
                profit = float(order['stoplossprice']) - float(order['entryprice'])
                
                # Update the CSV file with the profit and completed time
                order['profit'] = profit
                order['completedtime'] = datetime.datetime.now()
            # logger("no executed orders linked to order id:",order["uid"])
        
            # Write the updated order details to the CSV file
            with open('orders.csv', mode='w') as file:
                fieldnames = ORDERCOLUMNS
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                
                writer.writeheader()
                writer.writerows(orders)

check_closed_orders()