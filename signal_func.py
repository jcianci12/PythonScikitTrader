from getHighs import getHighs
from getLows import getLows
from get_tp_sl import get_tp_sl


import pandas as pd


def signal_func(row, data, window_position):
    # define constants for readability
    current_price = row["close"]
    row_position = data.index.get_loc(row.name)

    # calculate the takeprofit and stoploss thresholds from the average true range and the current price
    tp, sl = get_tp_sl(data,row_position)
    # get the integer location of the row in the data index

    # shift and roll the data to get the highest high and lowest low in a lookahead window
    highs = getHighs(data,row_position)
    lows = getLows(data,row_position)



    # get the values of highest high and lowest low at the row position
    highesthigh = highs.max()
    lowestlow = lows.min()

           


    tp = highesthigh
    sl = lowestlow

    tp,sl= check_tp_sl(tp,sl,current_price,40,30)
    # get the index labels of the minimum and maximum values in lows and highs respectively
    lowestindex= lows.idxmin()
    highestindex = highs.idxmax()


    # create a bool which is true if the hightest index was reached before the lowest index
    highestfirst = (highestindex < lowestindex)
    reachestp = (highesthigh >= tp)
    reachessl = (lowestlow <= sl)
    # check if the price hits the tp first or sl first and assign signals accordingly
    HitsTPandBeforeLow = int(reachestp and highestfirst)
    HitsSL = int(reachessl and not highestfirst)

    # print some information to the console
    print(f"entry:{current_price}|tp:{tp}|sl:{sl}|UpSignal:{HitsTPandBeforeLow}|DownSignal:{HitsSL}")


#it looks like this is just returning the same values for the whole series
# return a Series object with HitsTPandBeforeLow and HitsSL as values
    return pd.Series([HitsTPandBeforeLow, HitsSL])


def check_tp_sl(tp, sl, current_price, min_tp,  min_sl):
    if tp < current_price + min_tp:
        tp = current_price + min_tp

    if sl > current_price - min_sl:
        sl = current_price - min_sl

    return tp, sl
