import decimal
from bybitapi import get_market_bid_price, place_sell_order
from config import *
from functions.logger import logger
from functions.map_range import map_range


def selllogic(confidence_score, btcbalance, btcmarketvalue):
    """
    Function to determine if a sell order should be placed based on the confidence score and other parameters.
    :param confidence_score: The confidence score for the sell decision.
    :param sellthreshold: The threshold for the confidence score to trigger a sell.
    :param btcbalance: The current balance of BTC.
    :param btcmarketvalue: The current market value of BTC.
    """
    capitalsymbol = "BTC"
    marketsymbol = "BTCUSDT"
    minsellamount = 0  # don't want to sell too low an amount.
    transactioninusdt = btcmarketvalue * btcbalance
    # Calculate the percentage of capital to sell based on the confidence score
    capitalpercent = map_range(confidence_score, 0, SELLTHRESHOLD, MAXSELLPERCENTOFCAPITAL, minsellamount)
    
    # Calculate the transaction amount
    # Calculate the quantity to sell
    qty_rounded = decimal.Decimal(transactioninusdt).quantize(decimal.Decimal('.000001'), rounding=decimal.ROUND_DOWN)
        
    # Check if the transaction amount is greater than the minimum transaction size
    if qty_rounded > getminimumtransactionamount():
        logger("Decided to sell %", capitalpercent, " of BTC balance. |BTC balance: ", btcbalance,
               " | Market value: ", btcmarketvalue, "transaction amount:", transactioninusdt)
        
       
        
        # Place the sell order
        response = place_sell_order(TEST,  marketsymbol, qty_rounded)
            
    else:
        logger("Not enough ", capitalsymbol, " balance is:", btcbalance)

def getminimumtransactionamount():
    return decimal.Decimal(MINIMUMBTCTRANSACTIONSIZE)*decimal.Decimal(get_market_bid_price(TEST,"BTCUSDT"))


