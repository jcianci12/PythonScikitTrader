

from getLows import getLows
from getHighs import getHighs
from minimum_movement_to_take_profit import calculate_smallest_movement
from config import TRADINGPAIR


min_movement = calculate_smallest_movement(20,TRADINGPAIR)

def get_tp_sl(data,row_position,latestprice):
    # when we are 
    if(latestprice):
        entry_price = latestprice
    else:
        entry_price = data['open'][row_position]

   # shift and roll the data to get the highest high and lowest low in a lookahead window
    highs = getHighs(data,row_position)
    lows = getLows(data,row_position)

    # get the values of highest high and lowest low at the row position
    highesthigh = highs.max()
    lowestlow = lows.min()
    tp = highesthigh
    sl = lowestlow



    min_tp =(entry_price+80)
    min_sl = (entry_price-80)

    if(min_tp>tp):
        tp = min_tp
    if(min_sl<sl):
        sl = min_sl
    return tp,sl
    