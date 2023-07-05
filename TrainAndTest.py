# %%
import datetime
import decimal
import os
import time
import pandas as pd
import numpy as np


import joblib
from functions.map_range import map_range
from get_latest_model_file import get_latest_model_filename, get_model_filename
from logic.buylogic import buylogic
from bybitapi import fetch_bybit_data_v5, get_market_ask_price, get_market_bid_price, get_wallet_balance

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

    predictionup = data.shift(-LOOKAHEADVALUE)["close"] >= data["close"]
    predictionup = predictionup.iloc[:-LOOKAHEADVALUE]
    data["pred"] = predictionup.astype(int)

    predictiondec = data.shift(-LOOKAHEADVALUE)["close"] <= data["close"]
    predictiondec = predictiondec.iloc[:-LOOKAHEADVALUE]
    data["preddec"] = predictiondec.astype(int)

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
    
    # trainingdata.tail()
    validator = TrainingAndValidation()
    #retrain the data
    logger("retraining...")
    #get the simulated ledger


    validator.train_and_cross_validate(trainingdata,symbol,start_date,end_date,INTERVAL)
    logger(f"Ensemble Accuracy inc = {sum(validator.get_ensemble_resultsinc()) / len(validator.get_ensemble_resultsinc())}")
    logger(f"Ensemble Accuracy dec = {sum(validator.get_ensemble_resultsdec()) / len(validator.get_ensemble_resultsdec())}")

   

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
    data = data.drop('preddec', axis=1)

    # Use the loaded model to make predictions

    prediction = model.predict(data)
    # logger("prediction",prediction)
    # Calculate the mean of the binary values
    confidence_score = np.mean(prediction)
    print("The decicision value is ",confidence_score)

    return confidence_score

def trade_loop():
    logger("Starting loop")

    end_date = datetime.now()
    start_date = end_date -timedelta(DATALENGTHFORTRAININGINDAYS)
    category = 'spot'
    if(ALWAYSRETRAIN or  is_file_older_than_n_minutes(get_latest_model_filename(symbol,INTERVAL,start_date,end_date,"ensembleinc"),60)):
        #retrain the data
        retrain()
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
    confidence_scoreinc = getconfidencescore(data,start_date,end_date,"ensembleinc")
    confidence_scoredec = map_range(getconfidencescore(data,start_date,end_date,"ensembledec"),0,1,1,0)

    usdtbalance = decimal.Decimal(get_wallet_balance(TEST,"USDT"))
    btcbalance = decimal.Decimal(get_wallet_balance(TEST,"BTC"))
    bid_price = decimal.Decimal(get_market_bid_price(TEST,"BTCUSDT"))
    ask_price = decimal.Decimal(get_market_ask_price(TEST,"BTCUSDT"))

    portfolio_balance = (decimal.Decimal(usdtbalance) + (btcbalance *   bid_price))
    logger("Portfolio: ",portfolio_balance,"BTC:",btcbalance,"USDT:",usdtbalance)
    # Print the final output
    logger("buy signal:", confidence_scoreinc,"sell signal:",confidence_scoredec)

    if(confidence_scoreinc==1 or confidence_scoreinc ==0 or confidence_scoreinc ==0.5): # if its 1 or 0 or 0.5 something went wrong, retrain.
        retrain() 
    else:
        if(confidence_scoreinc>BUYTHRESHOLD and confidence_scoredec>SELLTHRESHOLD):
            buylogic(confidence_scoreinc,usdtbalance)
        elif(confidence_scoreinc<BUYTHRESHOLD and confidence_scoredec<SELLTHRESHOLD):
            selllogic(confidence_scoredec,btcbalance,bid_price)
        else:
            logger(str("Didnt act"))
    plot_graph(bid_price, confidence_scoreinc,confidence_scoredec, portfolio_balance,usdtbalance,btcbalance*bid_price,"performance.png","performance.csv",GRAPHVIEWWINDOW)


if (FORCERETRAINATSTART):
    logger("Force retrain at start set to true, retraining.")
    retrain()

call_decide_every_n_seconds(300, trade_loop)









