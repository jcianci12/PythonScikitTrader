import os
import shutil

import joblib

from get_latest_model_file import get_model_filename
from functions.logger import plot_graph, logger


class ModelManagement:
    def save_models(self, models, symbol, interval, start, end):
        # Create a models directory if it doesn't exist
        if not os.path.exists("models"):
            os.makedirs("models")

        # Save the models with the specified naming convention
        for model_name, model in models.items():
            filename = get_model_filename(symbol,interval,start,end,model_name)
            logger("saving model file as ",filename)
            joblib.dump(model, f"models/{filename}" )
    def load_models(self, model_names, symbol, interval, start, end):
        models = {}
        for model_name in model_names:
            filename = get_model_filename(symbol,interval,start,end,model_name)
            filepath = f"models/{filename}"
            if os.path.exists(filepath):
                logger("loading model file ",filename)
                model = joblib.load(filepath)
                models[model_name] = model
            else:
                logger(f"model file {filename} not found")
        return models

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
