import decimal
from bybitapi import get_market_bid_price, place_order, place_sell_order
from config import *
from functions.logger import logger
from functions.map_range import map_range
import ccxt


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
        
        USDTTradeAmount = map_range(confidence_score, 0, 1,float(getminimumtransactionamountinusdt(marketsymbol,btcbalance)),float(getmaxtransactionsizeinusdt(btcbalance,btcmarketvalue)) )
        USDTTradeAmount = decimal.Decimal(USDTTradeAmount) 

        percent = (USDTTradeAmount / btcbalance )*100
        BTCTradeAmount = USDTTradeAmount /btcmarketvalue

        # Calculate the transaction amount
        # Calculate the quantity to sell
        logger("Decided to sell ", percent, "percent of BTC balance of: ", btcbalanceUSDT,
            " | Market value: ", btcmarketvalue, "USDT transaction amount:", USDTTradeAmount)
                
        # Check if the transaction amount is greater than the minimum transaction size
        if BTCTradeAmount > getminimumtransactionamountinbtc(btcbalance):   

            
            # Place the sell order
            # response = place_sell_order(TEST,  marketsymbol, tradeamount/btcmarketvalue) 
            response = place_order(TEST,"market", "BTC/USDT","sell", None,None, BTCTradeAmount)


        else:
            logger("Not enough ", capitalsymbol, " balance is:", btcbalanceUSDT)
    else:
        logger("Not allowed to sell. If you want to change this, please edit the config.py file.")

def getminimumtransactionamountinusdt(marketsymbol,balance):
    mintransaction = MINIMUMBTCTRANSACTIONSIZE 
    
    return decimal.Decimal(mintransaction)*decimal.Decimal(get_market_bid_price(TEST,marketsymbol))

def getminimumtransactionamountinbtc(balance):
    mintransaction = MINIMUMBTCTRANSACTIONSIZE 

    return decimal.Decimal(mintransaction)

def getmaxtransactionsizeinusdt(btcbalance,btcmarketvalue):
    return ((decimal.Decimal(MAXBUYPERCENTOFCAPITAL)/100)*btcbalance)*btcmarketvalue


