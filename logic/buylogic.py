import decimal
from bybitapi import get_market_ask_price, get_market_bid_price, place_buy_order
from config import *
from functions.logger import logger
from functions.map_range import map_range


def buylogic(self,confidence_score,  usdtbalance):
    """
    Function to determine if a buy order should be placed based on the confidence score and other parameters.
    :param confidence_score: The confidence score for the buy decision.
    :param buythreshold: The threshold for the confidence score to trigger a buy.
    :param usdtbalance: The current balance of USDT.
    """
    minbuyamount = 0.2  # don't want to buy too low an amount.
    
    # Calculate the percentage of capital to buy based on the confidence score
    capitalpercent = map_range(confidence_score, BUYTHRESHOLD, 1, minbuyamount, MAXBUYPERCENTOFCAPITAL)
    
    # Calculate the transaction amount
    transactionamount =    ((capitalpercent / 100) * usdtbalance)/float(get_market_bid_price(TEST,"BTCUSDT"))
    
    logger("Decided to buy %", capitalpercent, " of USDT balance. |USDT balance: ", usdtbalance,
           " | Market value: ", transactionamount, "transaction amount:", transactionamount)
    min_qty = getminimumtransactionamount()
    # Check if the transaction amount is greater than the minimum transaction size
    if transactionamount > min_qty:
        logger("Enough USDT to cover purchase of ", "USDT", " balance is:", usdtbalance)
        
        # Calculate the quantity to buy
        qty = (capitalpercent / 100) * usdtbalance
        qty_rounded = decimal.Decimal(qty).quantize(decimal.Decimal('.000001'), rounding=decimal.ROUND_DOWN) 
        
        # Place the buy order
        response = place_buy_order(TEST, "BTCUSDT", "USDT",TAKEPROFIT,STOPLOSS, qty_rounded)
        print(response)
    else:
        logger("Not enough ", "USDT", " balance is:", usdtbalance)

def getminimumtransactionamount():
    return decimal.Decimal(MINIMUMBTCTRANSACTIONSIZE)*decimal.Decimal(get_market_ask_price(TEST,"BTCUSDT"))

