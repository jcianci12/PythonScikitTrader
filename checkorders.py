import csv
import datetime
from pybit.unified_trading import HTTP
from bybitapi import get_session

from config import TEST

def check_orders():
    
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
        )
        
        # Check if the take profit and stop loss orders have been executed
        take_profit_executed = any(o['order_id'] == order['takeprofitid'] and o['order_status'] == 'Filled' for o in order_history)
        stop_loss_executed = any(o['order_id'] == order['stoplossid'] and o['order_status'] == 'Filled' for o in order_history)
        
        # Cancel the other order if one is executed
        if take_profit_executed:
            get_session(TEST).cancel_order(
                category="spot",
                symbol=order['symbol'],
                orderId=order['stoplossid']
            )
            
            # Calculate the profit
            profit = float(order['takeprofitprice']) - float(order['entryprice'])
            
            # Update the CSV file with the profit and completed time
            order['profit'] = profit
            order['completedtime'] = datetime.datetime.now()
        elif stop_loss_executed:
            get_session(TEST).cancel_order(
                category="spot",
                symbol=order['symbol'],
                orderId=order['takeprofitid']
            )
            
            # Calculate the profit
            profit = float(order['stoplossprice']) - float(order['entryprice'])
            
            # Update the CSV file with the profit and completed time
            order['profit'] = profit
            order['completedtime'] = datetime.datetime.now()
    
    # Write the updated order details to the CSV file
    with open('orders.csv', mode='w') as file:
        fieldnames = ['uid', 'symbol', 'side', 'qty', 'entryprice', 'takeprofitprice', 'stoplossprice', 'takeprofitid', 'stoplossid', 'profit', 'completedtime']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        
        writer.writeheader()
        writer.writerows(orders)
