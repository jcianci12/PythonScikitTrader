# %%
import datetime
import os
import time
import pandas as pd
import numpy as np


import joblib
from get_latest_model_file import get_latest_model_filename, get_model_filename
from logic.buylogic import buylogic
from bybitapi import fetch_bybit_data_v5, get_market_bid_price, get_wallet_balance

from TrainingandValidation import TrainingAndValidation
from datetime import datetime, timedelta

from functions.clock import call_decide_every_n_seconds
from config import *
from functions.logger import logger, plot_graph
from logic.selllogic import selllogic

import multiprocessing as mp


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
# %%
def _produce_movement_indicators(data):
    """
    Function that produces the 'truth' values
    At a given row, it looks 'window' rows ahead to see if the price increased (1) or decreased (0)
    :param window: number of days, or rows to look ahead to see what the price did
    """

    prediction = data.shift(-LOOKAHEADVALUE)["close"] >= data["close"]
    prediction = prediction.iloc[:-LOOKAHEADVALUE]
    data["pred"] = prediction.astype(int)

    return data
#%%

# # Retrain the model using the latest data
def retrain():
    validator = TrainingAndValidation()
    category = 'spot'
    end_date = datetime.now()
    start_date = end_date -timedelta(DATALENGTHFORTRAININGINDAYS)
    #fetch the kline (historical data)
    trainingdata = fetch_bybit_data_v5(True,start_date,end_date,"BTCUSDT",INTERVAL,category)
    #smooth the data
    trainingdata = _exponential_smooth(trainingdata,0.65)
    #produce indicators
    trainingdata = _produce_movement_indicators(trainingdata)
    #drop na data
    trainingdata = (
        trainingdata.dropna()
    )  # Some indicators produce NaN values for the first few rows, we just remove them here
    
    trainingdata.tail()
    validator = TrainingAndValidation()
    #retrain the data
    logger("retraining...")
    #get the simulated ledger


    validator.train_and_cross_validate(trainingdata,symbol,start_date,end_date,INTERVAL)
    print(f"RF Accuracy = {sum(validator.get_rf_results()) / len(validator.get_rf_results())}")
    print(f"KNN Accuracy = {sum(validator.get_knn_results()) / len(validator.get_knn_results())}")
    print(f"Ensemble Accuracy = {sum(validator.get_ensemble_results()) / len(validator.get_ensemble_results())}")

    print(validator.get_ledger())
    ledger = validator.get_ledger()
    validator.save_dataframe(ledger)

def is_file_older_than_n_minutes(file_path, n):
    if ((file_path==None) or not os.path.exists(file_path)  ):
        logger("File doesnt exist")

        return True
    logger("time is ",time.time(),"|file time is",os.path.getmtime(file_path))
    return time.time() - os.path.getmtime(file_path) > n * 60

def getconfidencescore(data,start_date,end_date,modelname):
    filename = get_latest_model_filename(symbol,INTERVAL,start_date,end_date,modelname)
    logger("Loading model from ", filename)
    model = joblib.load(filename)

    data = data.drop('pred', axis=1)
    # Use the loaded model to make predictions

    prediction = model.predict(data)
    # logger("prediction",prediction)
    # Calculate the mean of the binary values
    confidence_score = np.mean(prediction)
    print("The decicision value is ",confidence_score)

    return confidence_score

def trade_loop():
    logger("Starting loop")
    category = 'spot'
    end_date = datetime.now()
    start_date = end_date -timedelta(DATALENGTHFORTRADINGINDAYS)
    #fetch the kline (historical data)
    data = fetch_bybit_data_v5(TEST,start_date,end_date,"BTCUSDT",INTERVAL,category)
    # data = old_fetch_bybit_data_v5(True,start_date,end_date,"BTCUSDT",interval,category)
    #smooth the data
    data = _exponential_smooth(data,0.65)
    #produce indicators
    data = _produce_movement_indicators(data)
    #drop na data
    data = (
        data.dropna()
    )  # Some indicators produce NaN values for the first few rows, we just remove them here
    data.tail()

    if(ALWAYSRETRAIN or  is_file_older_than_n_minutes(get_latest_model_filename(symbol,INTERVAL,start_date,end_date,"ensemble"),60)):
            
        
        #retrain the data
        retrain()

    #get the simulated ledger
        # print(validator.get_ledger())

    #call the trade decider.
        
    confidence_score = getconfidencescore(data,start_date,end_date,"ensemble")
    usdtbalance = float(get_wallet_balance(TEST,"USDT"))
    btcbalance = float(get_wallet_balance(TEST,"BTC"))
    btcmarketvalue = float(get_market_bid_price(TEST,"BTCUSDT"))
    portfolio_balance = (float(usdtbalance) + (btcbalance *   btcmarketvalue))
    logger("Portfolio: ",portfolio_balance,"BTC:",btcbalance,"USDT:",usdtbalance)
    # Print the final output
    logger("Recieved confidence signal of:", confidence_score)
    if(confidence_score==1 or confidence_score ==0 or confidence_score ==0.5): # if its 1 or 0 or 0.5 something went wrong, retrain.
        retrain() 
    else:
        if(confidence_score>BUYTHRESHOLD):
            buylogic(confidence_score,BUYTHRESHOLD,usdtbalance)
        elif(confidence_score<SELLTHRESHOLD):
            selllogic(confidence_score,SELLTHRESHOLD,btcbalance,btcmarketvalue)
        else:
            logger(str("Didnt act"))

    plot_graph(btcmarketvalue, confidence_score, portfolio_balance,usdtbalance,btcbalance,"performance.png","performance.csv",30)


if (FORCERETRAINATSTART):
    logger("Force retrain at start set to true, retraining.")
    retrain()

call_decide_every_n_seconds(300, trade_loop)









