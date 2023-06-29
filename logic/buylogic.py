import decimal
from bybitapi import place_buy_order
from config import *
from functions.logger import logger
from functions.map_range import map_range


def buylogic(confidence_score, buythreshold, usdtbalance):
    """
    Function to determine if a buy order should be placed based on the confidence score and other parameters.
    :param confidence_score: The confidence score for the buy decision.
    :param buythreshold: The threshold for the confidence score to trigger a buy.
    :param usdtbalance: The current balance of USDT.
    """
    minbuyamount = 0.2  # don't want to buy too low an amount.
    
    # Calculate the percentage of capital to buy based on the confidence score
    capitalpercent = map_range(confidence_score, buythreshold, 1, minbuyamount, MAXBUYPERCENTOFCAPITAL)
    
    # Calculate the transaction amount
    transactionamount = ((capitalpercent / 100) * usdtbalance)
    
    logger("Decided to buy %", capitalpercent, " of USDT balance. |USDT balance: ", usdtbalance,
           " | Market value: ", transactionamount, "transaction amount:", transactionamount)
    
    # Check if the transaction amount is greater than the minimum transaction size
    if transactionamount > MINIMUMTRANSACTIONSIZE:
        logger("Enough USDT to cover purchase of ", "USDT", " balance is:", usdtbalance)
        
        # Calculate the quantity to buy
        qty = (capitalpercent / 100) * usdtbalance
        qty_rounded = qty.quantize(decimal.Decimal('.000001'), rounding=decimal.ROUND_DOWN)
        
        # Check if qty_rounded is less than the minimum order quantity
        min_qty = decimal.Decimal('0.000001')
        if qty_rounded < min_qty:
            logger(f"Sale of {qty_rounded} was below minimum amount.")
            qty_rounded = min_qty
        
        # Place the buy order
        response = place_buy_order(TEST, "BTCUSDT", "USDT", 10, 5, qty_rounded)
        print(response)
    else:
        logger("Not enough ", "USDT", " balance is:", usdtbalance)



