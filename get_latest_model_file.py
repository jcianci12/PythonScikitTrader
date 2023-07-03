import glob
import os

import pandas as pd

def get_model_filename(symbol,interval,startdate,enddate,modelname):
    return f"{symbol}_{interval}_{str(startdate)}_{str(enddate)}_{modelname}.joblib"

def get_latest_model_filename(symbol, interval,startdate,enddate,modelname):
    # Get a list of all model files that match the symbol and interval

    model_files = glob.glob(f"models/{symbol}_{interval}_*_*_ensemble.joblib")


    # Check if there are any matching model files
    if model_files:
        # Get the latest model file
        latest_model_file = max(model_files, key=os.path.getctime)
        return latest_model_file
    else:
        # No matching model files were found
        return None
    
def compare_dates(file_name, df):
    # Extract the start and end dates from the file name
    parts = file_name.split("_")
    start = parts[-3]
    end = parts[-2]

    # Convert the start and end dates to datetime objects
    start_date = pd.to_datetime(start)
    end_date = pd.to_datetime(end)

    # Get the latest date in the DataFrame
    latest_date = df.index[-1]

    # Compare the dates
    if latest_date > end_date:
        print(f"The latest date in the DataFrame ({latest_date}) is after the end date in the file name ({end_date}).")
    elif latest_date < start_date:
        print(f"The latest date in the DataFrame ({latest_date}) is before the start date in the file name ({start_date}).")
    else:
        print(f"The latest date in the DataFrame ({latest_date}) is between the start and end dates in the file name ({start_date} to {end_date}).")
