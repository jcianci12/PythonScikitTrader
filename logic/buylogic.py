import decimal
from bybitapi import get_market_ask_price, get_market_bid_price, get_min_qty_binance, place_order
from config import *
from functions.logger import logger
from functions.map_range import map_range
from generateTPandSL import calculate_prices
from bybitapi import exchange

def buylogic(confidence_score,  usdtbalance):
    """
    Function to determine if a buy order should be placed based on the confidence score and other parameters.
    :param confidence_score: The confidence score for the buy decision.
    :param buythreshold: The threshold for the confidence score to trigger a buy.
    :param usdtbalance: The current balance of USDT.
    """
    marketprice = get_market_ask_price("BTCUSDT")
    usdtbalance = float(usdtbalance)
    
    exchange.load_markets()
    

    # Calculate the percentage of capital to buy based on the confidence score
    # capitalpercent = map_range(confidence_score, 0, 1, float(getminimumtransactionamountUSDT()), MAXBUYPERCENTOFCAPITAL)
    # capitalpercent = decimal.Decimal(capitalpercent)
    buyamountinbtc = usdtbalance*(MAXBUYPERCENTOFCAPITAL/100)/marketprice
    # buyamountinbtc = exchange.amount_to_precision("BTC/USDT",amount)
    buyamountinusdt = usdtbalance*(MAXBUYPERCENTOFCAPITAL/100)
    # buyamountinusdt = round(buyamountinusdt,2)

    # formatted_amount = exchange.amount_to_precision('BTC/USDT', buyamountinusdt)
    # formatted_price = float(exchange.price_to_precision('BTC/USDT', buyamountinusdt))
    amount = buyamountinusdt+20
    amount =   exchange.amount_to_precision("BTC/USDT",float(amount)/float(marketprice))
    
    
    logger("Decided to buy %", MAXBUYPERCENTOFCAPITAL, " of USDT balance. |USDT balance: ", usdtbalance,
           " | BTC TSCN QTY: ", buyamountinbtc, "USDT TSCN QTY:", amount)
    tp,sl = calculate_prices(None)

    # Check if the transaction amount is greater than the minimum transaction size
    if float(amount)>0 and (float(amount)*float(marketprice))<usdtbalance:
        logger("Enough USDT to cover purchase of ", "USDT", " balance is:", usdtbalance)
        
        # Calculate the quantity to buy
        # qty = (capitalpercent / 100) * usdtbalance
        # qty_rounded = decimal.Decimal(qty).quantize(decimal.Decimal('.000001'), rounding=decimal.ROUND_DOWN) 
        
        # Place the buy order
        # response = place_order(TEST, "BTCUSDT", "USDT",TAKEPROFIT,STOPLOSS, qty_rounded)
        tp,sl = calculate_prices(None)
        response = place_order(TEST,"market", "BTCUSDT","buy",tp,sl,  amount)

        print(response)
    else:
        logger("Not enough ", "USDT", " balance is:", usdtbalance)

def getminimumtransactionamountUSDT():
    return get_min_qty_binance("BTC/USDT")*get_market_ask_price("BTC/USDT")
def getminimumtransactionamountBTC():
    return decimal.Decimal(get_min_qty_binance("BTC/USDT"))

