
from bybitapi import get_free_balance,exchange


def check_amount(amount,market_price,side)->bool:
    amount = get_amount(amount,side,market_price)
    # Get the free balance of the relevant currency
    if side == 'buy':
        free_balance = float(get_free_balance("USDT"))/market_price
    else:
        free_balance = float(get_free_balance("BTC"))

    # Calculate the order value
    if side == 'buy':
        order_value = amount
    else:
        order_value = amount
    
    

    # Check if the quantity is positive and the order value is less than the free balance
    return amount > 0 and order_value < free_balance

def get_amount(amount,side,market_price):
    market_price = float(market_price)
        # Calculate the order value
    #if the side is buy, we need the amount divided by the market price
    if(side =='buy'):
        amount = amount/market_price

    
    return float(amount)


        
    