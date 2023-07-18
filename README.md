# PythonScikitTrader
Thanks for checking out my project!
TLDR:
This bot trains itsellf every 60 minutes and checks the market every 5 minutes. It only buys (no shorting...yet!).
Once it chooses to buy, it places an order at market price and logs the order in orders.csv
If the market price reaches the tp or sl, it will log orders to 'close' off those trades and updates the profit column in the orders.csv

What this project does:
- Demonstrates how to interface with the bybit exchange (sometimes the bybit documentation was a bit sparse - there is some trial and error in here)
- Demonstrates in a not so elegant way how RN, KNN, and Ensemble model classifiers can be trained
- Auto trades the BTCUSDT spot pair on bybit unified exchange
- Produces signals based on training data for a +5 price increase or a -5 increase
- Generates the TP and SL using the ATR index
- Uses the buy and sell signals to know when to buy
- Produces a performance graph showing the btc close price, the signals, and the portfoio balance
- Includes some python unit tests for checking connection to the exchange (these tests could really be improved quite a bit)
- Logs the order in orders.csv and then watches the market price to check if we are hitting the TP or SL. If we do, it creates the sell order and updates the orders.csv with the profit/loss 😎

What this project probably doesnt do:
- Make money 🤣 - although lately it seems to be working well
- It doesnt really give great indicators, but because we are selling at our take profit and stop losses, we are ok there.

What I would love this project to do:
- Update the models more efficiently - currently it is fetching all historic data and training on all the data every 60 minutes instead of just updating the models with the newest data
- Incorporate backtest.py so that I can, well... backtest!

Startup guide (how im doing it on a windows machine)
- Get vscode
- Clone this project from vscode
- You should get an option pop up after cloning - something to the effect - would you like to open this in a container?
- Click reopen in container
- Once that is done, add a KEYS.py file and use the KEYS Template.py as a starting guide.
- Open train and test and top right you should have the option to run/run and debug. Click that
- If all goes to plan, here is what it does:
- Fetches historical data
- Trains on the data
- Every 5 mins, makes a prediction, buy, sell or hold
- Calculates buy and sell percent based on available capital
- Saves the performance data in a csv and plots a graph
- If you want to change any of the settings, as well as switch over to use the bybit test exchange API, just change TEST in config.py to True

If you have any feedback, feel free to get in touch - jon@tekonline.com.au
