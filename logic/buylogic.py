import decimal
from bybitapi import get_market_ask_price, get_market_bid_price, place_order
from config import *
from functions.logger import logger
from functions.map_range import map_range


def buylogic(confidence_score,  usdtbalance):
    """
    Function to determine if a buy order should be placed based on the confidence score and other parameters.
    :param confidence_score: The confidence score for the buy decision.
    :param buythreshold: The threshold for the confidence score to trigger a buy.
    :param usdtbalance: The current balance of USDT.
    """
    marketprice = decimal.Decimal(get_market_ask_price(TEST,"BTCUSDT"))
    usdtbalance = decimal.Decimal( usdtbalance)
    # Calculate the percentage of capital to buy based on the confidence score
    capitalpercent = map_range(confidence_score, 0, 1, float(getminimumtransactionamount()), MAXBUYPERCENTOFCAPITAL)
    capitalpercent = decimal.Decimal(capitalpercent)
    buyamountinbtc = usdtbalance*(capitalpercent/100)/marketprice
    buyamountinbtc = round(buyamountinbtc,6)
    buyamountinusdt = usdtbalance*(capitalpercent/100)
    buyamountinusdt = round(buyamountinusdt,2)
    # Calculate the transaction amount
    transactionamount =    buyamountinusdt*decimal.Decimal(get_market_bid_price(TEST,"BTCUSDT"))
    
    logger("Decided to buy %", capitalpercent, " of USDT balance. |USDT balance: ", usdtbalance,
           " | BTC TSCN QTY: ", buyamountinbtc, "USDT TSCN QTY:", buyamountinusdt)
    min_qty = getminimumtransactionamount()

    tp = float(marketprice+(marketprice * TAKEPROFIT))
    sl = float(marketprice  -(marketprice*STOPLOSS))
    # Check if the transaction amount is greater than the minimum transaction size
    if buyamountinusdt > min_qty:
        logger("Enough USDT to cover purchase of ", "USDT", " balance is:", usdtbalance)
        
        # Calculate the quantity to buy
        # qty = (capitalpercent / 100) * usdtbalance
        # qty_rounded = decimal.Decimal(qty).quantize(decimal.Decimal('.000001'), rounding=decimal.ROUND_DOWN) 
        
        # Place the buy order
        # response = place_order(TEST, "BTCUSDT", "USDT",TAKEPROFIT,STOPLOSS, qty_rounded)
        response = place_order(TEST,"market", "BTC/USDT","buy", tp,sl, buyamountinbtc)

        print(response)
    else:
        logger("Not enough ", "USDT", " balance is:", usdtbalance)

def getminimumtransactionamount():
    return decimal.Decimal(MINIMUMBTCTRANSACTIONSIZE)*decimal.Decimal(get_market_ask_price(TEST,"BTCUSDT"))

