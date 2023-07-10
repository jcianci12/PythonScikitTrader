import decimal
from bybitapi import get_market_ask_price, get_market_bid_price, place_buy_order, place_limit_order
from config import *
from functions.logger import logger
from functions.map_range import map_range

import csv

def buylogic(confidence_score,  usdtbalance):
    """
    Function to determine if a buy order should be placed based on the confidence score and other parameters.
    :param confidence_score: The confidence score for the buy decision.
    :param buythreshold: The threshold for the confidence score to trigger a buy.
    :param usdtbalance: The current balance of USDT.
    """
    # Calculate the percentage of capital to buy based on the confidence score
    capitalpercent = map_range(confidence_score, 0, 1, float(getminimumtransactionamount()), MAXBUYPERCENTOFCAPITAL)
    capitalpercent = decimal.Decimal(capitalpercent)
    buyamountinusdt = usdtbalance*(capitalpercent/100)
    
    # Calculate the transaction amount
    transactionamount =    buyamountinusdt*decimal.Decimal(get_market_bid_price(TEST,"BTCUSDT"))
    
    #calculate the tp and sl
    tp = get_market_bid_price(TEST,"BTCUSDT") * (PERCENTCHANGEINDICATOR)
    sl = get_market_ask_price(TEST,"BTCUSDT") * (-PERCENTCHANGEINDICATOR)

    logger("Decided to buy %", capitalpercent, " of USDT balance. |USDT balance: ", usdtbalance,
           " | BTC TSCN QTY: ", buyamountinusdt, "USDT TSCN QTY:", transactionamount,)
    min_qty = getminimumtransactionamount()
    # Check if the transaction amount is greater than the minimum transaction size
    if buyamountinusdt > min_qty:
        logger("Enough USDT to cover purchase of ", "USDT", " balance is:", usdtbalance)
        
        # Calculate the quantity to buy
        qty = (capitalpercent / 100) * usdtbalance
        qty_rounded = decimal.Decimal(qty).quantize(decimal.Decimal('.000001'), rounding=decimal.ROUND_DOWN) 
        
        # Place the buy order
        response = place_buy_order(TEST,"Market" "BTCUSDT", "USDT", qty_rounded)
        order_id = response['order_id']
        take_profit_order_id = place_limit_order(TEST,"Limit","BTCUSDT","USDT",qty,tp)
        stop_loss_order_id = place_limit_order(TEST,"Limit","BTCUSDT","USDT",qty,sl)
    
        
        print(response)
    else:
        logger("Not enough ", "USDT", " balance is:", usdtbalance)

def getminimumtransactionamount():
    return decimal.Decimal(MINIMUMBTCTRANSACTIONSIZE)*decimal.Decimal(get_market_ask_price(TEST,"BTCUSDT"))

def write_order_to_csv(order_id, symbol, qty_rounded, price, take_profit_order_id, stop_loss_order_id):
    with open('orders.csv', mode='w') as orders_file:
        fieldnames = ['order_id', 'symbol', 'side', 'type', 'quantity', 'price', 'tp_order_id', 'sl_order_id']
        writer = csv.DictWriter(orders_file, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerow({'order_id': order_id, 'symbol': symbol, 'side': 'BUY', 'type': 'MARKET', 'quantity': qty_rounded, 'price': price, 'tp_order_id': take_profit_order_id, 'sl_order_id': stop_loss_order_id})