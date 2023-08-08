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
    

    

    return tp, sl

min_movement = calculate_smallest_movement(20,"BTC/USDT")

def get_tp_sl_from_ATR(atr,entry_price):
    entry_price = float(entry_price)
    #the atr is the whole range, so we should divide by two to find the centre
    atr = atr/2
    # Calculate take profit and stop loss prices
    tp = float(entry_price) + TAKEPROFIT * atr
    sl = float(entry_price) - STOPLOSS * atr

    min_profit_price = min_movement + entry_price
    if(min_profit_price>tp):
        tp = min_profit_price
    

    # Make sure stop loss is lower than market price
    if sl >= entry_price:
        sl = entry_price - atr.iloc[-1]

    # Make sure take profit is higher than market price
    if tp <= entry_price:
        tp = entry_price + atr.iloc[-1]
    # print("MP:"+str(entry_price)+"TP:"+str(tp)+"SL:"+str(sl))

    return tp,sl


