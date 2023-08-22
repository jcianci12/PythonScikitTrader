import pandas as pd
from finta import TA

from signal_func import signal_func


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

    # data = removecols(data)

    return data

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
# def removecols(data):
#     del (data['open'])
#     del (data['high'])
#     del (data['low'])
#     del (data['volume'])
#     return data

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

