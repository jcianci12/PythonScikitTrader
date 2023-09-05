import glob
import os
import shutil

import joblib

from functions.logger import plot_graph, logger

import os
import joblib
from parse_file_name import parse_file_name
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

class ModelManagement:
    def save_models(self, models, symbol, interval, start, end):
        # Create a models directory if it doesn't exist
        if not os.path.exists("models"):
            os.makedirs("models")

        # Save the models with the specified naming convention
        filename = get_model_filename(symbol,interval,start,end)
        logger("saving model file as ",filename)
        joblib.dump(models, f"models/{filename}" )


    def clean_up_models(self,directory):
        if os.path.isdir(directory):
            for filename in os.listdir(directory):
                file_path = os.path.join(directory, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print('Failed to delete %s. Reason: %s' % (file_path, e))
        else:
            print(f"{directory} does not exist")



def load_latest_model():
    result = parse_file_name()
    if result is None:
        print(f'No .joblib files exist in the models folder.')
        return None
    start_date, end_date, symbol, interval = result
    file_name = f"{symbol}_{interval}_{str(start_date)}_{str(end_date)}.joblib"
    model = joblib.load(os.path.join('models', file_name))
    return model


def get_new_model():
            # Models which will be used
        rfinc = RandomForestClassifier()
        knninc = KNeighborsClassifier()


        # Create a tuple list of our models
        estimatorsinc = [("knninc", knninc), ("rfinc", rfinc)]

        ensembleinc = VotingClassifier(estimatorsinc, voting="soft")

        return rfinc,knninc,ensembleinc



def get_model_filename(symbol,interval,startdate,enddate):
    return f"{symbol}_{interval}_{str(startdate)}_{str(enddate)}.joblib"

def get_latest_model_filename(symbol, interval):
    # Get a list of all model files that match the symbol and interval

    model_files = glob.glob(f"models/{symbol}_{interval}_*_*.joblib")


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
