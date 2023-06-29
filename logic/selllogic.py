import decimal
from bybitapi import place_sell_order
from config import *
from functions.logger import logger
from functions.map_range import map_range


def selllogic(confidence_score, sellthreshold, btcbalance, btcmarketvalue):
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
    
    # Calculate the percentage of capital to sell based on the confidence score
    capitalpercent = map_range(confidence_score, 0, sellthreshold, MAXSELLPERCENTOFCAPITAL, minsellamount)
    
    # Calculate the transaction amount
    transactionamount = (capitalpercent * btcbalance) * btcmarketvalue
    
    # Check if the transaction amount is greater than the minimum transaction size
    if transactionamount > MINIMUMTRANSACTIONSIZE:
        logger("Decided to sell %", capitalpercent, " of BTC balance. |BTC balance: ", btcbalance,
               " | Market value: ", btcmarketvalue, "transaction amount:", transactionamount)
        
        # Calculate the quantity to sell
        qty = (capitalpercent / 100) * btcbalance
        qty_rounded = qty.quantize(decimal.Decimal('.000001'), rounding=decimal.ROUND_DOWN)
        
        # Check if qty_rounded is less than the minimum order quantity
        min_qty = decimal.Decimal('0.000001')
        if qty_rounded < min_qty:
            logger(f"Sale of {qty_rounded} was below minimum amount.")
            qty_rounded = min_qty
        
        # Place the sell order
        response = place_sell_order(TEST, capitalsymbol, marketsymbol, qty_rounded)
        print(response)
    else:
        logger("Not enough ", capitalsymbol, " balance is:", btcmarketvalue)



