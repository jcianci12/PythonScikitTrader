
from api import get_free_balance,exchange, get_market_ask_price
from config import MAXBUYPERCENTOFCAPITAL
from functions.logger import logger

def get_min_notional():
    markets = exchange.load_markets()
    market = markets[TRADINGPAIR]
    min_notional = float(market['info']['filters'][6]['minNotional'])
    return min_notional

def check_amount(amount,market_price,side)->bool:
    amount = float(exchange.amount_to_precision('BTC/USDT', amount*market_price))
    min_notional = get_min_notional()
    if amount <= min_notional:
        errormsg = f"Notional value too low |Amount:{amount}|Min:{min_notional}"  
        return errormsg
# Get the free balance of the relevant currency
    if side == 'buy':
        min_purchase = (get_min_notional()*1.2)
        if(amount<min_purchase):
            amount = min_purchase
        free_balance = float(get_free_balance("USDT"))
    else:
        free_balance = float(get_free_balance("BTC"))
    
    if float(exchange.amount_to_precision(TRADINGPAIR,free_balance*market_price)) <amount:
        errormsg = f"balance too low. Balance:{free_balance*market_price}|amount:{amount}"  
        return errormsg    

    # Check if the quantity is positive and the order value is less than the free balance
    return None

def Adjust_Amount_for_fees(amount,market_price, side): 
    markets = exchange.load_markets()
    symbol = TRADINGPAIR
    market = markets[symbol]
    taker_fee = market['taker']
    maker_fee = market['maker']
    fee_rate = taker_fee if side == 'buy' else maker_fee
    fee = amount * fee_rate
    # Calculate the order value
    # if the side is buy, we need the amount divided by the market price
    if side == 'buy':
        amount = (amount - fee) / market_price
    else:
        amount = amount - fee
    check = check_amount(amount,market_price,side)
    if check==None:
        return float(amount),check
    else: return None,check


def get_investment_amount(side):
    market_price = get_market_ask_price(TRADINGPAIR)
    usdtbalance = get_free_balance("USDT")
# Calculate the percentage of capital to buy based on the confidence score
    buyamountinbtc = usdtbalance*(MAXBUYPERCENTOFCAPITAL/100)/market_price
    buyamountinusdt = usdtbalance*(MAXBUYPERCENTOFCAPITAL/100)

    amount = buyamountinusdt
    amount,error = Adjust_Amount_for_fees(amount,market_price,side)
    return amount,market_price,buyamountinbtc,buyamountinusdt,usdtbalance,error

