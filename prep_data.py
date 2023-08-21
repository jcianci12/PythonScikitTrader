import random
from config import LOOKAHEADVALUE, PERCENTCHANGEINDICATOR
from minimum_movement_to_take_profit import calculate_smallest_movement,tpsl_smallest_movement
import pandas as pd
from finta import TA

from generateTPandSL import calculate_prices, get_tp_sl_from_ATR

def _exponential_smooth(data, alpha):
    """
    Function that exponentially smooths dataset so values are less 'rigid'
    :param alpha: weight factor to weight recent values more
    """

    return data.ewm(alpha=alpha).mean()

def _produce_movement_indicators(data):
    """
    Function that produces the 'truth' values
    At a given row, it looks 'window' rows ahead to see if the price increased (1) or decreased (0)
    :param window: number of days, or rows to look ahead to see what the price did
    """
    # get the takeprofit and stoploss prices from the average true range and the current price
    # data["pred"], data["preddec"] = data.apply(signal_func, args=(data, data.index), axis=1, result_type='expand')
    # print(data.loc[data['preddec'] == 0])
    # print(data.loc[data['preddec'] == 1])
    pred = []
    preddec = []
    for index, row in data.iterrows():
        result = signal_func(row, data, index)
        pred.append(result[0])
        preddec.append(result[1])
    data["pred"] = pred
    data["preddec"] = preddec

    data = removecols(data)

    return data

def signal_func(row, data, window_position):
    # define constants for readability
    ATR_PERIOD = 14
    LOOKAHEAD_PERIOD = 14
    current_price = row["close"]
    
    # calculate the takeprofit and stoploss thresholds from the average true range and the current price
    tp, sl = get_tp_sl_from_ATR(row[f"{ATR_PERIOD} period ATR"], current_price)

    # get the integer location of the row in the data index
    row_position = data.index.get_loc(row.name)

    # shift and roll the data to get the highest high and lowest low in a lookahead window
    highs = data.shift(-LOOKAHEAD_PERIOD + row_position).rolling(LOOKAHEAD_PERIOD)['high'].max()
    lows = data.shift(-LOOKAHEAD_PERIOD + row_position).rolling(LOOKAHEAD_PERIOD)['low'].min()

    # get the values of highest high and lowest low at the row position
    highesthigh = highs.iloc[row_position]
    lowestlow = lows.iloc[row_position]
    
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
    print(f"UpSignal:{HitsTPandBeforeLow}|DownSignal:{HitsSL}")   

    
#it looks like this is just returning the same values for the whole series
# return a Series object with HitsTPandBeforeLow and HitsSL as values
    return pd.Series([HitsTPandBeforeLow, HitsSL])





INDICATORS = [
    "RSI",
    "MACD",
    "STOCH",
    "ADL",
    "ATR",
    "MOM",
    "MFI",
    "ROC",
    "OBV",
    "CCI",
    "EMV",
    "VORTEX",
]

# %%
"""
Next we pull the historical data using yfinance
Rename the column names because finta uses the lowercase names
"""

def _get_indicator_data(data):
    """
    Function that uses the finta API to calculate technical indicators used as the features
    :return:
    """

    for indicator in INDICATORS:
        ind_data = getattr(TA, indicator)(data)
        if not isinstance(ind_data, pd.DataFrame):
            ind_data = ind_data.to_frame()
        data = data.join(ind_data, rsuffix='_' + indicator)
    data.columns = data.columns.str.replace('[^a-zA-Z0-9 ]', '')

    # Also calculate moving averages for features
    data['ema50'] = data['close'] / data['close'].ewm(50).mean()
    data['ema21'] = data['close'] / data['close'].ewm(21).mean()
    data['ema15'] = data['close'] / data['close'].ewm(14).mean()
    data['ema5'] = data['close'] / data['close'].ewm(5).mean()

    # Instead of using the actual volume value (which changes over time), we normalize it with a moving volume average
    data['normVol'] = data['volume'] / data['volume'].ewm(5).mean()

    # Remove columns that won't be used as features
    
    return data
def removecols(data):
    del (data['open'])
    del (data['high'])
    del (data['low'])
    del (data['volume'])
    return data

def prep_data(data):
     #smooth the data
    data = _exponential_smooth(data,0.65)

    data= _get_indicator_data(data)
    data = _produce_movement_indicators(data)

    #produce indicators
    #drop na data
    data = (
        data.dropna()
    )  # Some indicators produce NaN values for the first few rows, we just remove them here
    return data

