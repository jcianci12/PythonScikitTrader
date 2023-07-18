import asyncio
import decimal
from functools import partial
from pybit.unified_trading import WebSocket
from time import sleep, time
import csv

from bybitapi import place_order
from generateTPandSL import calculate_prices
from get_last_ohlc_bybit import get_last_ohlc_bybit

from ordersservice import OrderService

orderservice = OrderService()

def check_orders(testmode, symbol, market_price):
    print("check orders called")

    orders = orderservice.read_orders()
    # Check for open orders that have reached their take profit or stop loss prices
    for order in orders:
        if not order['profit']:
            # ohlc = get_last_ohlc_bybit(symbol,"5")
            entry_price = float(order['entryprice'])
            # takeprofitprice, stoplossprice = calculate_prices(entry_price, None )
            takeprofitprice = decimal.Decimal(order['takeprofitprice'])
            stoplossprice = decimal.Decimal(order['stoplossprice'])
            side = order['side'].lower()
            qty = float(order['qty'])

            if (side == 'buy' and market_price >= takeprofitprice) or (side == 'sell' and market_price <= takeprofitprice):
                # Take profit
                new_side = 'Sell' if side == 'buy' else 'buy'
                orderresult = place_order(testmode,"market",symbol, new_side,
                            qty/market_price)
                order['exitprice']=market_price
                order['profit'] = getOrderProfitLoss(order,entry_price,market_price,qty)['profit']
            elif (side == 'buy' and market_price <= stoplossprice) or (side == 'sell' and market_price >= stoplossprice):
                # Stop loss
                new_side = 'Sell' if side == 'buy' else 'buy'
                orderresult = place_order(testmode,"market",symbol, new_side,
                            qty/market_price)
                order['exitprice']=market_price
                order['profit'] = getOrderProfitLoss(order,entry_price,market_price,qty)['profit']

            newtp,newsl = calculate_prices(entry_price,None)
            order['takeprofitprice'] = newtp
            order['stoplossprice']= newsl

            # Save the updated orders back to the CSV file
        
   
            orderservice.write_orders('orders.csv', orders)

def getOrderProfitLoss(order,entry_price,market_price,qty):

    order['profit'] = (market_price-entry_price)*(qty/market_price)
    return order

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
        

# startListening()
check_orders(True, "BTCUSDT", 30000)

