import glob
import os
import shutil
import joblib
from matplotlib import pyplot as plt
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from Simulation.assettracker import AssetTracker

from Simulation.capitaltracker import CapitalTracker
from config import *
from functions.logger import plot_graph, logger
from functions.modelmanagement import ModelManagement
from get_latest_model_file import compare_dates, get_latest_model_filename, get_model_filename
from prep_data import prep_data

class TrainingAndValidation:


    def __init__(self):

        self.stock_name = "BTCUSDT"
        self.ledger = []


        self.item = AssetTracker()
        self.capital_tracker = CapitalTracker(10000)

    def train_and_cross_validate(self, data, symbol, start, end, interval):
        data = prep_data(data)
        i = 0
        self.num_train = 10
        self.len_train = 40

        # Lists to store the results from each model
        self.knn_resultsinc = []
        self.rf_resultsinc = []
        self.ensemble_resultsinc = []

        self.knn_resultsdec = []
        self.rf_resultsdec = []
        self.ensemble_resultsdec = []

        # Models which will be used
        rfinc = RandomForestClassifier()
        knninc = KNeighborsClassifier()

        rfdec = RandomForestClassifier()
        knndec = KNeighborsClassifier()

        # Create a tuple list of our models
        estimatorsinc = [("knninc", knninc), ("rfinc", rfinc)]
        estimatorsdec = [("rfdec",rfdec),("knndec",knndec)]

        ensembleinc = VotingClassifier(estimatorsinc, voting="soft")
        ensembledec = VotingClassifier(estimatorsdec, voting="soft")

        logger("Starting training")
        while True:
            # Partition the data into chunks of size len_train every num_train days
            df = data.iloc[i * self.num_train : (i * self.num_train) + self.len_train]
            i += 1

            if len(df) < 40:
                break
#increase

            y = df["pred"]
            features = [x for x in df.columns if x not in ["pred","preddec"]]
            X = df[features]

            X_train, X_test, y_train, y_testinc = train_test_split(
                X, y, train_size=7 * len(X) // 10, shuffle=False
            )

            # fit models
            rfinc.fit(X_train, y_train)
            knninc.fit(X_train, y_train)
            ensembleinc.fit(X_train, y_train)

            # get predictions
            rf_predictioninc = rfinc.predict(X_test)
            knn_predictioninc = knninc.predict(X_test)
            ensemble_predictioninc = ensembleinc.predict(X_test)
            rf_accuracyinc = accuracy_score(y_testinc.values, rf_predictioninc)
            knn_accuracyinc = accuracy_score(y_testinc.values, knn_predictioninc)
            ensemble_accuracyinc = accuracy_score(y_testinc.values, ensemble_predictioninc)

            
            self.rf_resultsinc.append(rf_accuracyinc)
            self.knn_resultsinc.append(knn_accuracyinc)
            self.ensemble_resultsinc.append(ensemble_accuracyinc)

#decrease
            y = df["preddec"]
            features = [x for x in df.columns if x not in ["pred","preddec"]]
            X = df[features]

            X_train, X_test, y_train, y_testdec = train_test_split(
                X, y, train_size=7 * len(X) // 10, shuffle=False
            )

            # fit models
            rfdec.fit(X_train, y_train)
            knndec.fit(X_train, y_train)
            ensembledec.fit(X_train, y_train)

            # # get predictions
            rf_predictiondec = rfdec.predict(X_test)
            knn_predictiondec = knndec.predict(X_test)
            ensemble_predictiondec = ensembledec.predict(X_test)
# determine accuracy and append to results
            rf_accuracydec = accuracy_score(y_testdec.values, rf_predictiondec)
            knn_accuracydec = accuracy_score(y_testdec.values, knn_predictiondec)
            ensemble_accuracydec = accuracy_score(y_testdec.values, ensemble_predictiondec)

            
            self.rf_resultsdec.append(rf_accuracydec)
            self.knn_resultsdec.append(knn_accuracydec)
            self.ensemble_resultsdec.append(ensemble_accuracydec)
        
       


            print(X_train.index[0])            

        logger(f"Ensemble Accuracy Inc = {sum(self.get_ensemble_resultsinc()) / len(self.get_ensemble_resultsinc())}")
        logger(f"Ensemble Accuracy Dec = {sum(self.get_ensemble_resultsdec()) / len(self.get_ensemble_resultsdec())}")
         
       
        self.models = {"rfinc": rfinc, "knninc": knninc, "ensembleinc": ensembleinc,"rf":rfdec,"knninc":knndec,"ensembledec":ensembledec}
        mm = ModelManagement()
        mm.clean_up_models("models")
        mm.save_models(self.models, symbol, interval, start, end)

        logger("Finished training")



    


    def get_results_df(self):
        return self.results_df
    def get_ledger(self):
        return  pd.DataFrame( self.ledger)
    def get_rf_results(self):
        return self.rf_results

    def get_knn_results(self):
        return self.knn_results

    def get_ensemble_resultsinc(self):
        return self.ensemble_resultsinc

    def get_ensemble_resultsdec(self):
        return self.ensemble_resultsdec

    # def calculate_kelly_investment(  risk_fraction,minimumfraction):
    # kelly_fraction = item.getSuccessRatio() - (1 - item.getSuccessRatio() ) / risk_fraction
    # if kelly_fraction<minimumfraction:
    #     kelly_fraction = minimumfraction
    # return capital_tracker.capital * kelly_fraction

    


    def getLedgerdf(self):
        return  pd.DataFrame( self.ledger)

    def save_dataframe(self,dataframe):
        dataframe.to_csv('backtest.csv', index=False)
    










