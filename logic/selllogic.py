import decimal
from bybitapi import get_market_bid_price, place_sell_order
from config import *
from functions.logger import logger
from functions.map_range import map_range


def selllogic(confidence_score, btcbalance, btcmarketvalue):
    if(ALLOWEDTOSELL):
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

        tradeamount = map_range(confidence_score, 0, SELLTHRESHOLD,float(getmaxtransactionsizeinusdt(btcbalance,btcmarketvalue)), float(getminimumtransactionamountinusdt(marketsymbol)))
        tradeamount = decimal.Decimal(tradeamount) /btcmarketvalue
        # Calculate the transaction amount
        # Calculate the quantity to sell
        logger("Decided to sell ", tradeamount, " of BTC balance of: ", btcbalanceUSDT,
            " | Market value: ", btcmarketvalue, "USDT transaction amount:", tradeamount)
                
        # Check if the transaction amount is greater than the minimum transaction size
        if tradeamount > getminimumtransactionamountinbtc():   

            
            # Place the sell order
            response = place_sell_order(TEST,  marketsymbol, tradeamount) 

        else:
            logger("Not enough ", capitalsymbol, " balance is:", btcbalanceUSDT)
    else:
        logger("Not allowed to sell. If you want to change this, please edit the config.py file.")

def getminimumtransactionamountinusdt(marketsymbol):
    return decimal.Decimal(MINIMUMBTCTRANSACTIONSIZE)*decimal.Decimal(get_market_bid_price(TEST,marketsymbol))

def getminimumtransactionamountinbtc():
    return decimal.Decimal(MINIMUMBTCTRANSACTIONSIZE)

def getmaxtransactionsizeinusdt(btcbalance,btcmarketvalue):
    return ((decimal.Decimal(MAXBUYPERCENTOFCAPITAL)/100)*btcbalance)*btcmarketvalue


