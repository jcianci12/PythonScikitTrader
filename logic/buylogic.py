import decimal
from api import get_current_price, get_free_balance, get_market_ask_price,  get_min_qty_binance, place_order_tp_sl
from check_amount import get_investment_amount
from config import *
from datamanager import DataManager
from functions.logger import logger
from get_tp_sl import get_tp_sl

def buylogic(data):
    """
    Function to determine if a buy order should be placed based on the confidence score and other parameters.
    :param confidence_score: The confidence score for the buy decision.
    :param buythreshold: The threshold for the confidence score to trigger a buy.
    :param usdtbalance: The current balance of USDT.
    """

    
    logger("Decided to buy %", MAXBUYPERCENTOFCAPITAL, " of USDT balance. Checking if enough...")

    side = 'buy'
    tp,sl = get_tp_sl(DataManager().data,len(data)-1,get_current_price(SYMBOL))
    # tp,sl = tpsl_smallest_movement()
    amount,market_price,buyamountinbtc,buyamountinusdt,usdtbalance,error = get_investment_amount(side)
    # Check if the transaction amount is greater than the minimum transaction size
    if error==None:

        logger("Enough USDT to cover purchase of ", "USDT", "|USDT balance: ", usdtbalance,
           " |BTC TSCN QTY: ", buyamountinbtc, "USDT TSCN QTY:", amount)
        
        btcbalance = get_free_balance("BTC")


        response = place_order_tp_sl(TEST,"market", "BTCUSDT","buy",usdtbalance,btcbalance,tp,sl,  amount)

        print(response)
    else:
        logger(error)

def getminimumtransactionamountUSDT():
    return get_min_qty_binance(TRADINGPAIR)*get_market_ask_price(TRADINGPAIR)
def getminimumtransactionamountBTC():
    return decimal.Decimal(get_min_qty_binance(TRADINGPAIR))

