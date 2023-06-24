import glob
import os


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