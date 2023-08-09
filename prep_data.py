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
    data["pred"], data["preddec"] = data.apply(signal_func, args=(data, data.index), axis=1, result_type='expand')
    print(data.loc[data['preddec'] == 0])
    print(data.loc[data['preddec'] == 1])
    return data

def signal_func(row, data, index):
    # define constants for readability
    ATR_PERIOD = 14
    LOOKAHEAD_VALUE = 20
    current_price = row["close"]
    # calculate the takeprofit and stoploss thresholds from the average true range and the current price
    tp,sl = get_tp_sl_from_ATR(row[f"{ATR_PERIOD} period ATR"], current_price)

    index = data.index.get_loc(row.name)


    #lookahead value
    futurecloseprice = data["close"].shift(-LOOKAHEAD_VALUE+index).iloc[:1].iloc[0]
    # check if the price increases or decreases by more than the thresholds in the next 'window' rows
    up_signal = 1 if random.random()>=0.5 else 0
    down_signal = int(futurecloseprice<=sl)

    print(f"MP:{current_price}|TP:{tp}|SL:{sl}|UpSignal:{up_signal}|DownSignal:{down_signal}")   
   
#it looks like this is just returning the same values for the whole series
    return pd.Series([up_signal, down_signal])




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
        ind_data = eval('TA.' + indicator + '(data)')
        if not isinstance(ind_data, pd.DataFrame):
            ind_data = ind_data.to_frame()
        data = data.merge(ind_data, left_index=True, right_index=True)
    data.rename(columns={"14 period EMV.": '14 period EMV'}, inplace=True)

    # Also calculate moving averages for features
    data['ema50'] = data['close'] / data['close'].ewm(50).mean()
    data['ema21'] = data['close'] / data['close'].ewm(21).mean()
    data['ema15'] = data['close'] / data['close'].ewm(14).mean()
    data['ema5'] = data['close'] / data['close'].ewm(5).mean()

    # Instead of using the actual volume value (which changes over time), we normalize it with a moving volume average
    data['normVol'] = data['volume'] / data['volume'].ewm(5).mean()

    # Remove columns that won't be used as features
    del (data['open'])
    del (data['high'])
    del (data['low'])
    del (data['volume'])
    
    return data
    

def prep_data(data):
     #smooth the data
    data = _exponential_smooth(data,0.65)
    data= _get_indicator_data(data)
    #produce indicators
    data = _produce_movement_indicators(data)
    #drop na data
    data = (
        data.dropna()
    )  # Some indicators produce NaN values for the first few rows, we just remove them here
    return data

