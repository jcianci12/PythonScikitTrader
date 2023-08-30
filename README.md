# PythonScikitTrader
Thanks for checking out my project!

What this project does:
- Demonstrates how to interface with the binance exchange
- Creates indicator data including take profit and stop loss
- Demonstrates in a not so elegant way how RN, KNN, and Ensemble model classifiers can be trained
- Auto trades the BTCUSDT spot pair on binance unified exchange
- Produces signals that indicate wether the dynamic tp or sl will be hit
- Uses those signals to buy or sell
- Produces a performance graph showing the btc close price, the signals, and the portfoio balance
- Includes some python unit tests for checking connection to the exchange (these tests could really be improved quite a bit)

What this project probably doesnt do:
- Make money 🤣
- Give good indicators (seems like training phase seems to give about a 60% success rate)
- Time the market very well... 

What I would love this project to do:
- Update the models more efficiently - this is currently in testing phase
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
