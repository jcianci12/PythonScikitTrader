import csv
import datetime
from bybitapi import cancel_order, get_session
# from pybit.unified_trading import HTTP

from config import ORDERCOLUMNS, TEST
from functions.logger import logger

def check_closed_orders():
    
    # Read the order details from the CSV file
    with open('orders.csv', mode='r') as file:
        reader = csv.DictReader(file)
        orders = list(reader)
    
    # Check the status of each order
    for order in orders:
        # Get a list of historical orders
        order_history = get_session(TEST).get_order_history(
            category="spot",
            symbol=order['symbol']
        )['result']['list']
        # print (order_history)
        
        # Check if the take profit and stop loss orders have been executed
        take_profit_executed = any(o['orderId'] == order['takeprofitid'] and o['orderStatus'] == 'Filled' for o in order_history)
        stop_loss_executed = any(o['orderId'] == order['stoplossid'] and o['orderStatus'] == 'Filled' for o in order_history)
        
        # Cancel the other order if one is executed
        if take_profit_executed:
            cancel_order("BTCUSDT",order['stoplossid'])
            
            # Calculate the profit
            profit = float(order['takeprofitprice']) - float(order['entryprice'])
            
            # Update the CSV file with the profit and completed time
            order['profit'] = profit
            order['completedtime'] = datetime.datetime.now()
            logger("take profit executed, cancelling order",order["uid"])

        elif stop_loss_executed:
            cancel_order("BTCUSDT",order['takeprofitid'])
            
            # Calculate the profit
            profit = float(order['stoplossprice']) - float(order['entryprice'])
            
            # Update the CSV file with the profit and completed time
            order['profit'] = profit
            order['completedtime'] = datetime.datetime.now()
            logger("stop loss executed, cancelling order",order["uid"])
        logger("no executed orders linked to order id:",order["uid"])
    
    # Write the updated order details to the CSV file
    with open('orders.csv', mode='w') as file:
        fieldnames = ORDERCOLUMNS
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        
        writer.writeheader()
        writer.writerows(orders)