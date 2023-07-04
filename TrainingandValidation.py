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
from get_latest_model_file import compare_dates, get_latest_model_filename, get_model_filename

class TrainingAndValidation:


    def __init__(self):

        self.stock_name = "BTCUSDT"
        self.ledger = []


        self.item = AssetTracker()
        self.capital_tracker = CapitalTracker(10000)

    def train_and_cross_validate(self, data, symbol, start, end, interval):
        i = 0
        self.num_train = 10
        self.len_train = 40

        # Lists to store the results from each model
        self.knn_results = []
        self.rf_results = []
        self.ensemble_results = []

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

            X_train, X_test, y_train, y_test = train_test_split(
                X, y, train_size=7 * len(X) // 10, shuffle=False
            )

            # fit models
            rfinc.fit(X_train, y_train)
            knninc.fit(X_train, y_train)
            ensembleinc.fit(X_train, y_train)

            # # get predictions
            # rf_prediction = rfinc.predict(X_test)
            # knn_prediction = knninc.predict(X_test)
            # ensemble_prediction = ensembleinc.predict(X_test)


#decrease
            y = df["preddec"]
            features = [x for x in df.columns if x not in ["pred","preddec"]]
            X = df[features]

            X_train, X_test, y_train, y_test = train_test_split(
                X, y, train_size=7 * len(X) // 10, shuffle=False
            )

            # fit models
            rfdec.fit(X_train, y_train)
            knndec.fit(X_train, y_train)
            ensembledec.fit(X_train, y_train)

            # # get predictions
            # rf_prediction = rfdec.predict(X_test)
            # knn_prediction = knndec.predict(X_test)
            # ensemble_prediction = ensembledec.predict(X_test)
            print(X_train.index[0])            


         

                 
       
        self.models = {"rfinc": rfinc, "knninc": knninc, "ensembleinc": ensembleinc,"rf":rfdec,"knninc":knndec,"ensembledec":ensembledec}
        self.clean_up_models("models")

        self.save_models(self.models, symbol, interval, start, end)

        logger("Finished training")



    def save_models(self, models, symbol, interval, start, end):
        # Create a models directory if it doesn't exist
        if not os.path.exists("models"):
            os.makedirs("models")

        # Save the models with the specified naming convention
        for model_name, model in models.items():
            filename = get_model_filename(symbol,interval,start,end,model_name)
            logger("saving model file as ",filename)
            joblib.dump(model, f"models/{filename}" )

    def clean_up_models(self,directory):
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))


    def get_results_df(self):
        return self.results_df
    def get_ledger(self):
        return  pd.DataFrame( self.ledger)
    def get_rf_results(self):
        return self.rf_results

    def get_knn_results(self):
        return self.knn_results

    def get_ensemble_results(self):
        return self.ensemble_results
    

    # def calculate_kelly_investment(  risk_fraction,minimumfraction):
    # kelly_fraction = item.getSuccessRatio() - (1 - item.getSuccessRatio() ) / risk_fraction
    # if kelly_fraction<minimumfraction:
    #     kelly_fraction = minimumfraction
    # return capital_tracker.capital * kelly_fraction

    
    def simulate_trade(self,data, row: pd.Series):
    
        date: pd.Timestamp = row["Date"]
        rf_prediction: int = row["RF Prediction"]
        knn_prediction: int = row["KNN Prediction"]
        ensemble_prediction: int = row["Ensemble Prediction"]
        actual_value: int = row["Actual"]
        # Win_Probability: int = row['Risk Score']

        # Get the value of the stock at the buy date
        current_price = data.loc[date, "close"]
        portfolio_value = self.capital_tracker.capital + (self.item.get_total_asset_quantity() * current_price)

        entry = {}
        triggered_assets = self.item.monitor_prices(current_price)


            # return triggered_assets
        for asset in triggered_assets:
        # Sell the assets
            result = self.item.sell(asset.quantity, current_price)
            if not result:
                print(result)
            else:
                spend_result = self.capital_tracker.earn(asset.quantity*current_price)
                entry = {
                            "Date": date,
                            "Action": "Sell",
                            "Stock": self.stock_name,
                            "Transaction Amount": asset.quantity*current_price,
                            "Portfolio Value": portfolio_value,

                            "Quantity": asset.quantity,
                            "Sell_Price": current_price,
                            "Balance": self.capital_tracker.capital,
                            "Stock_Balance": self.item.get_total_asset_quantity(),
                            "Avg profit": self.item.average_profit,
                        }
                        # Update the ledger with the trade details
                self.ledger.append(entry)



        if ensemble_prediction == 1:
            # Calculate the investment amount based on available balance, risk percentage, and trade confidence
            # investment_amount =calculate_kelly_investment(risk_percentage,0.01)  # Use a portion of the balance based on the risk percentage
            investment_amount =self.capital_tracker.capital*0.02  # Use a portion of the balance based on the risk percentage

            spend_result = self.capital_tracker.spend(investment_amount)

            if not spend_result:
                print(spend_result)
                return
            else:
                    # Calculate the quantity of stock purchased based on the investment amount and buy price
                quantity = investment_amount / current_price
                result = self.item.purchase(quantity, current_price,current_price*TAKEPROFIT,current_price*STOPLOSS)
                entry = {
                    "Date": date,
                    "Action": "Buy",
                    "Stock": self.stock_name,
                    "Transaction Amount": investment_amount,
                    "Portfolio Value": portfolio_value,
                    "Quantity": quantity,
                    "Buy_Price": current_price,
                    "Balance": self.capital_tracker.capital,
                    "Stock_Balance": self.item.get_total_asset_quantity(),
                    "Avg profit": self.item.average_profit,
                }
                # Update the ledger with the trade details
                self.ledger.append(entry)
        if(PLOTBACKTEST==True):
            plot_graph(current_price,ensemble_prediction,portfolio_value,0,0,'backtest.png','backtest.csv',GRAPHVIEWWINDOW)
       

        # ledger_df = pd.DataFrame(
        #     columns=["Date", "Action", "Stock", "Quantity", "Price", "Balance"]
        # )
        # Convert the ledger list to a DataFrame
        # ledger_df = pd.DataFrame(self.ledger)

        # print(ledger_df)
        # self.write_backtest_data(ledger_df)
        # self.ledger_df.append(ledger_df)
        # self.plot_data(ledger_df)

    def getLedgerdf(self):
        return  pd.DataFrame( self.ledger)

    def save_dataframe(self,dataframe):
        dataframe.to_csv('backtest.csv', index=False)
    










