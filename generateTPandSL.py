import csv
import decimal
from finta import TA

import csv

import pandas as pd
from bybitapi import get_market_bid_price
from config import STOPLOSS, SYMBOL, TAKEPROFIT, TEST

from get_last_ohlc_bybit import get_last_ohlc_binance
from minimum_movement_to_take_profit import calculate_smallest_movement

def save_updated_prices(filename, orders):
    # Write updated data to CSV file
    with open(filename, mode='w') as file:
        fieldnames = ['uid', 'symbol', 'side', 'qty', 'entryprice', 'takeprofitprice', 'stoplossprice', 'profit']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(orders)


from finta import TA
def calculate_prices(ohlc):
    if ohlc is None:
        ohlc = get_last_ohlc_binance(SYMBOL, "5m")
        ohlc = ohlc.apply(pd.to_numeric, errors='coerce')

    entry_price = decimal.Decimal( get_market_bid_price( SYMBOL))

    # Update latest OHLC value with current market price
    ohlc.iloc[-1]['close'] = entry_price

    # Calculate ATR using finta
    atr = TA.ATR(ohlc)

    # Calculate take profit and stop loss prices
    tp, sl = get_tp_sl_from_ATR(atr, entry_price)
    tp = decimal.Decimal(tp)

    min_movement = calculate_smallest_movement(20,"BTC/USDT")
    min_profit_price = min_movement + entry_price
    if(min_profit_price>tp):
        tp = min_profit_price
    
    sl = decimal.Decimal(sl)

    # Make sure stop loss is lower than market price
    if sl >= entry_price:
        sl = entry_price - atr.iloc[-1]

    # Make sure take profit is higher than market price
    if tp <= entry_price:
        tp = entry_price + atr.iloc[-1]

    return tp, sl


def get_tp_sl_from_ATR(atr,entry_price):
    entry_price = float(entry_price)
    # Calculate take profit and stop loss prices
    tp = float(entry_price) + TAKEPROFIT * (atr[len(atr)-1])
    sl = float(entry_price) - STOPLOSS * (atr[len(atr)-1])
    return tp,sl
