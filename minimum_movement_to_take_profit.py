from api import exchange
from config import TRADINGPAIR

def calculate_smallest_movement(amount: float, symbol: str) -> float:
  
    ticker = exchange.fetch_ticker(symbol)
    bid = ticker['bid']
    ask = ticker['ask']
    spread = ask - bid

    # Fetch trading fees
    maker_fee = exchange.fees['trading']['maker']
    taker_fee = exchange.fees['trading']['taker']

    # Calculate the smallest price movement required to make a profit
    # considering the fees for both the buy and sell transactions
    smallest_movement = (amount * (taker_fee + maker_fee) + spread) / amount
    return smallest_movement


def tpsl_smallest_movement():
    sm = calculate_smallest_movement(20,TRADINGPAIR)
    return sm*2,sm
