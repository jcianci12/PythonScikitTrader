# %%
import datetime
import glob
import os
import time
import pandas as pd
import numpy as np


import joblib
from logic.buylogic import buylogic
from bybitapi import fetch_bybit_data_v5, get_market_bid_price, get_wallet_balance

from TrainingandValidation import TrainingAndValidation
from datetime import datetime, timedelta

from functions.clock import call_decide_every_n_seconds
from config import *
from functions.logger import logger
from logic.selllogic import selllogic


# %%
"""
Defining some constants for data mining
"""
pd.set_option("display.max_rows", 50)

# DATE_RANGE = datetime.timedelta(days=11)  # The number of days of historical data to retrieve
# TIMEFRAME = TimeFrame(1, TimeFrameUnit.Hour)  # Sample rate of historical data
# symbol = "BTC/USD"  # Symbol of the desired stock





symbol = "BTCUSD"
test = True
days = 2

def _exponential_smooth(data, alpha):
    """
    Function that exponentially smooths dataset so values are less 'rigid'
    :param alpha: weight factor to weight recent values more
    """

    return data.ewm(alpha=alpha).mean()



# %%
def _produce_movement_indicators(data, window):
    """
    Function that produces the 'truth' values
    At a given row, it looks 'window' rows ahead to see if the price increased (1) or decreased (0)
    :param window: number of days, or rows to look ahead to see what the price did
    """

    prediction = data.shift(-window)["close"] >= data["close"]
    prediction = prediction.iloc[:-window]
    data["pred"] = prediction.astype(int)

    return data

#%%

# # Retrain the model using the latest data
def retrain():
    category = 'spot'
    end_date = datetime.now()
    start_date = end_date -timedelta(DATALENGTHFORTRAININGINDAYS)
    #fetch the kline (historical data)
    trainingdata = fetch_bybit_data_v5(True,start_date,end_date,"BTCUSDT",INTERVAL,category)
    #smooth the data
    trainingdata = _exponential_smooth(trainingdata,0.65)
    #produce indicators
    trainingdata = _produce_movement_indicators(trainingdata,window=15)
    #drop na data
    trainingdata = (
        trainingdata.dropna()
    )  # Some indicators produce NaN values for the first few rows, we just remove them here
    
    trainingdata.tail()
    validator = TrainingAndValidation(symbol)
    #retrain the data
    logger("retraining...")
    #get the simulated ledger
    print(validator.get_ledger())

    validator.train_and_cross_validate(trainingdata,symbol,start_date,end_date,INTERVAL)
    print(f"RF Accuracy = {sum(validator.get_rf_results()) / len(validator.get_rf_results())}")
    print(f"KNN Accuracy = {sum(validator.get_knn_results()) / len(validator.get_knn_results())}")
    print(f"Ensemble Accuracy = {sum(validator.get_ensemble_results()) / len(validator.get_ensemble_results())}")

def is_file_older_than_n_minutes(file_path, n):
    if not os.path.exists(file_path):
        logger("File doesnt exist")

        return True
    logger("time is ",time.time(),"|file time is",os.path.getmtime(file_path))
    return time.time() - os.path.getmtime(file_path) > n * 60
def get_latest_model_file(symbol, interval):
    # Get a list of all model files that match the symbol and interval
    model_files = glob.glob(f"models/{symbol}_{interval}_*_*_rf.joblib")

    # Check if there are any matching model files
    if model_files:
        # Get the latest model file
        latest_model_file = max(model_files, key=os.path.getctime)
        return latest_model_file
    else:
        # No matching model files were found
        return None
def getconfidencescore(data):
    model = joblib.load(get_latest_model_file(symbol,INTERVAL))

    data = data.drop('pred', axis=1)
    # Use the loaded model to make predictions
    prediction = model.predict(data)
    # Calculate the mean of the binary values
    confidence_score = np.mean(prediction)
    print("The decicision value is ",confidence_score)

    return confidence_score

def trade_loop():
    logger("the time is:",datetime.now())
    category = 'spot'
    end_date = datetime.now()
    start_date = end_date -timedelta(DATALENGTHFORTRADINGINDAYS)
    category = 'spot'
    #fetch the kline (historical data)
    data = fetch_bybit_data_v5(True,start_date,end_date,"BTCUSDT",INTERVAL,category)
    # data = old_fetch_bybit_data_v5(True,start_date,end_date,"BTCUSDT",interval,category)
    #smooth the data
    data = _exponential_smooth(data,0.65)
    #produce indicators
    data = _produce_movement_indicators(data,window=15)
    #drop na data
    data = (
        data.dropna()
    )  # Some indicators produce NaN values for the first few rows, we just remove them here
    data.tail()
    if(is_file_older_than_n_minutes(get_latest_model_file(symbol,INTERVAL),60)):
            
        validator = TrainingAndValidation(symbol)
        #retrain the data
        retrain()
    #get the simulated ledger
        print(validator.get_ledger())

    #call the trade decider.
        
    confidence_score = getconfidencescore(data)
    usdtbalance = float(get_wallet_balance(TEST,"USDT"))
    btcbalance = float(get_wallet_balance(TEST,"BTC"))
    btcmarketvalue = float(get_market_bid_price(TEST,"BTCUSDT"))

    # Print the final output
    logger("Recieved confidence signal of:", confidence_score)
    if(confidence_score>BUYTHRESHOLD):
        buylogic(confidence_score,BUYTHRESHOLD,usdtbalance)
    elif(confidence_score<SELLTHRESHOLD):
        selllogic(confidence_score,SELLTHRESHOLD,btcbalance,btcmarketvalue)
    else:
        logger(str("Didnt act"))
    logger("Balance is ",(float(usdtbalance) + (btcbalance *   btcmarketvalue)))

call_decide_every_n_seconds(300, trade_loop)









