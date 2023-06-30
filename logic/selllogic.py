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
    btcbalanceUSDT = btcmarketvalue * btcbalance
    # Calculate the percentage of capital to sell based on the confidence score

         

    tradeamount = map_range(confidence_score, 0, SELLTHRESHOLD, float(getminimumtransactionamountinusdt(marketsymbol)),float(getmaxtransactionsizeinusdt(btcbalanceUSDT)))

    # Calculate the transaction amount
    # Calculate the quantity to sell
    qty_rounded = decimal.Decimal(tradeamount)/btcmarketvalue
        
    # Check if the transaction amount is greater than the minimum transaction size
    if qty_rounded > getminimumtransactionamountinusdt(marketsymbol):   

        logger("Decided to sell %", tradeamount, " of BTC balance. |BTC balance: ", btcbalance,
            " | Market value: ", btcmarketvalue, "transaction amount:", tradeamount)
            
        # Place the sell order
        response = place_sell_order(TEST,  marketsymbol, qty_rounded)            
    else:
        logger("Not enough ", capitalsymbol, " balance is:", btcbalance)

def getminimumtransactionamountinusdt(marketsymbol):
    return decimal.Decimal(MINIMUMBTCTRANSACTIONSIZE)*decimal.Decimal(get_market_bid_price(TEST,marketsymbol))

def getminimumtransactionamountinbtc(marketsymbol):
    return decimal.Decimal(MINIMUMBTCTRANSACTIONSIZE)

def getmaxtransactionsizeinusdt(btcbalanceinusdt):
    return (decimal.Decimal(MAXBUYPERCENTOFCAPITAL)/100)*btcbalanceinusdt


