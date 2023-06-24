import os
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

class TrainingAndValidation:


    def __init__(self):

        self.stock_name = "BTCUSDT"
        self.ledger = []

        self.item = AssetTracker()
        self.capital_tracker = CapitalTracker(10000)

    def train_and_cross_validate(self,data,symbol,start,end,interval):
        i = 0
        self.num_train = 10
        self.len_train = 40

       # Lists to store the results from each model\n",
        self.knn_results = []
        self.rf_results = []
        self.ensemble_results = []

        # Models which will be used
        rf = RandomForestClassifier()
        knn = KNeighborsClassifier()

        # Create a tuple list of our models
        estimators = [("knn", knn), ("rf", rf)]
        ensemble = VotingClassifier(estimators, voting="soft")

        while True:
            # Partition the data into chunks of size len_train every num_train days
            df = data.iloc[i * self.num_train : (i * self.num_train) + self.len_train]
            i += 1

            if len(df) < 40:
                break
            y = df["pred"]
            features = [x for x in df.columns if x not in ["pred"]]
            X = df[features]

            X_train, X_test, y_train, y_test = train_test_split(
                X, y, train_size=7 * len(X) // 10, shuffle=False
            )

            # fit models
            rf.fit(X_train, y_train)
            knn.fit(X_train, y_train)
            ensemble.fit(X_train, y_train)

            # Create a models directory if it doesn't exist
            if not os.path.exists("models"):
                os.makedirs("models")
            name = f"{symbol}_{interval}_{start}_{end}"
            # Save the models with the specified naming convention
            joblib.dump(rf, f"models/{name}_rf.joblib")
            joblib.dump(knn, f"models/{name}_knn.joblib")
            joblib.dump(ensemble, f"models/{name}_ensemble.joblib")
            
            self.models = {"rf":rf,"knn":knn ,"ensemble":ensemble}

            # get predictions
            rf_prediction = rf.predict(X_test)
            knn_prediction = knn.predict(X_test)
            ensemble_prediction = ensemble.predict(X_test)

            # determine accuracy and append to results
            rf_accuracy = accuracy_score(y_test.values, rf_prediction)
            knn_accuracy = accuracy_score(y_test.values, knn_prediction)
            ensemble_accuracy = accuracy_score(y_test.values, ensemble_prediction)

            # Create a DataFrame to store the results
            rv = {
                "Date": pd.to_datetime(X_test.index),
                "RF Prediction": rf_prediction.astype(int),
                "KNN Prediction": knn_prediction.astype(int),
                "Ensemble Prediction": ensemble_prediction.astype(int),
                "Actual": y_test.values.astype(int),
            }

            self.results_df = pd.DataFrame(rv)
            
                    # Iterate over the rows of the results DataFrame
            for index, row in self.results_df.iterrows():
                print("simulating for row: ",row)
                self.simulate_trade(data, row)
                
            # Set the 'Date' column as the index
            self.results_df.set_index("Date", inplace=True)

        
            self.rf_results.append(rf_accuracy)
            self.knn_results.append(knn_accuracy)
            self.ensemble_results.append(ensemble_accuracy)
            



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
                            "Portfolio Value": self.capital_tracker.capital + (self.item.get_total_asset_quantity() * current_price),

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
                result = self.item.purchase(quantity, current_price,current_price*SIMTAKEPROFIT,current_price*SIMSTOPLOSS)

                entry = {
                    "Date": date,
                    "Action": "Buy",
                    "Stock": self.stock_name,
                    "Transaction Amount": investment_amount,
                    "Portfolio Value": self.capital_tracker.capital + (self.item.get_total_asset_quantity() * current_price),
                    "Quantity": quantity,
                    "Buy_Price": current_price,
                    "Balance": self.capital_tracker.capital,
                    "Stock_Balance": self.item.get_total_asset_quantity(),
                    "Avg profit": self.item.average_profit,
                }
                # Update the ledger with the trade details
                self.ledger.append(entry)

        ledger_df = pd.DataFrame(
            columns=["Date", "Action", "Stock", "Quantity", "Price", "Balance"]
        )
        # Convert the ledger list to a DataFrame
        ledger_df = pd.DataFrame(self.ledger)

        # print(ledger_df)
        # self.append_to_csv(ledger_df)
        # self.ledger_df.append(ledger_df)
        # self.plot_data(ledger_df)

    def getLedgerdf(self):
        return  pd.DataFrame( self.ledger)

    def append_to_csv(self,data):
        file_exists = os.path.isfile('ledger.csv')
        df = pd.DataFrame(data)
        with open('ledger.csv', 'a', newline='') as file:
            if not file_exists:
                df.to_csv(file, index=False)
            else:
                df.to_csv(file, index=False, header=False)





    def plot_data(self,data):
        df = pd.DataFrame(data, columns=['Date', 'Action', 'Stock', 'Transaction Amount', 'Portfolio Value'])
        df['Date'] = pd.to_datetime(df['Date'])
        df_buy = df[df['Action'] == 'Buy']
        df_sell = df[df['Action'] == 'Sell']
        plt.plot(df_buy['Date'], df_buy['Portfolio Value'], 'go', label='Buy')
        plt.plot(df_sell['Date'], df_sell['Portfolio Value'], 'ro', label='Sell')
        plt.legend()
        plt.show()
        plt.savefig('ledger.png')








