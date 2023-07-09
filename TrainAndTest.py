# %%
import datetime
import decimal
import os
import time
import pandas as pd
import numpy as np


import joblib
from functions.map_range import map_range
from functions.modelmanagement import ModelManagement
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

from prep_data import prep_data


# %%
"""
Defining some constants for data mining
"""
pd.set_option("display.max_rows", 5)

# DATE_RANGE = datetime.timedelta(days=11)  # The number of days of historical data to retrieve
# TIMEFRAME = TimeFrame(1, TimeFrameUnit.Hour)  # Sample rate of historical data
# symbol = "BTC/USD"  # Symbol of the desired stock





symbol = "BTCUSD"
test = True
days = 2

previousaction = None



# %%
# %%

#%%

# # Retrain the model using the latest data
def retrain(start_date,end_date):
    validator = TrainingAndValidation()
    category = 'spot'
 
    #fetch the kline (historical data)
    trainingdata = fetch_bybit_data_v5(True,start_date,end_date,"BTCUSDT",INTERVAL,category)
    logger("Training data sample before prep:",trainingdata.tail(1).to_string())

    #smooth the data
    trainingdata = prep_data(trainingdata)
    logger("Training data sample after prep:",trainingdata.tail(1).to_string())
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

def getconfidencescore(data,modelname):
    
    filename = get_latest_model_filename(symbol,INTERVAL,modelname)
    logger("Loading model from ", filename)
    model = joblib.load(filename)


#we only want the last row to predict on
    
    data = data.drop('pred', axis=1) 
    data = data.drop('preddec',axis=1)
    prediction = model.predict(data)
    # logger("prediction",prediction)
    # Calculate the mean of the binary values
    print("The decicision value is ",prediction)

    return prediction[0]

def trade_loop():
    logger("Starting loop")

    end_date = datetime.now()
    start_date = end_date -timedelta(DATALENGTHFORTRAININGINDAYS)
    category = 'spot'
    if(ALWAYSRETRAIN or  is_file_older_than_n_minutes(get_latest_model_filename(symbol,INTERVAL,"ensembleinc"),60)):
        #retrain the data
        retrain(start_date,end_date)
    start_date = end_date -timedelta(DATALENGTHFORTRADINGINDAYS)

    #fetch the kline (historical data)
    data = fetch_bybit_data_v5(TEST,start_date,end_date,"BTCUSDT",INTERVAL,category)
    # data = old_fetch_bybit_data_v5(True,start_date,end_date,"BTCUSDT",interval,category)
    #smooth the data
    data = prep_data(data)
    data = data.tail(1)
    logger("making decision based on ",data.to_string())
    confinc = getconfidencescore(data,"ensembleinc")
    confdec = getconfidencescore(data,"ensembledec")

    confidence_scoreinc = confinc
    confidence_scoredec = confdec

    confidence_scoreinc = confinc
    confidence_scoredec = confdec

    usdtbalance = decimal.Decimal(get_wallet_balance(TEST,"USDT"))
    btcbalance = decimal.Decimal(get_wallet_balance(TEST,"BTC"))
    bid_price = decimal.Decimal(get_market_bid_price(TEST,"BTCUSDT"))
    ask_price = decimal.Decimal(get_market_ask_price(TEST,"BTCUSDT"))

    portfolio_balance = (decimal.Decimal(usdtbalance) + (btcbalance *   bid_price))
    logger("Portfolio: ",portfolio_balance,"BTC:",btcbalance,"USDT:",usdtbalance)
    # Print the final output
    logger("buy signal:", confidence_scoreinc,"sell signal:",confidence_scoredec)
    global previousaction 
    newaction = None
    if(confidence_scoreinc==1 and confidence_scoredec==0):
        newaction = 1
        if(newaction!=previousaction):
            logger("State is different, acting.")
            buylogic(1,usdtbalance)
    elif(confidence_scoreinc==0 and confidence_scoredec==1):
        if(newaction!=previousaction):            
            newaction = -1
            selllogic(1,btcbalance,bid_price)
    else:
        newaction = 0
        logger(str("Didnt act"))
    previousaction = newaction

    plot_graph(bid_price, confidence_scoreinc,confidence_scoredec, portfolio_balance,usdtbalance,btcbalance*bid_price,"performance.png","performance.csv",GRAPHVIEWWINDOW)
if (TESTRETRAINATSTART):
    logger("Testing retrain function.")
    end_date = datetime.now()
    start_date = end_date-timedelta(1)
    retrain(end_date=datetime.now(),start_date=start_date)
    logger("Testing prediction")
    data = fetch_bybit_data_v5(TEST,start_date,end_date,"BTCUSDT",INTERVAL,'spot')
    confinc = getconfidencescore(data,"ensembleinc")
    confdec = getconfidencescore(data,"ensembledec")
    logger("prediction is:",confinc,confdec)

    logger("Done. Claning up models...")
    mm = ModelManagement()
    mm.clean_up_models("models")
    logger("Done.")


call_decide_every_n_seconds(300, trade_loop)









