import datetime
from backtesting import Backtest, Strategy
from backtesting.lib import crossover

from backtesting.test import SMA, GOOG
from bokeh.plotting import figure, output_file, save
from matplotlib import category
from TrainAndTest import _exponential_smooth, _produce_movement_indicators

from bybitapi import fetch_bybit_data_v5
from config import INTERVAL


class SmaCross(Strategy):
    n1 = 10
    n2 = 20

    def init(self):
        close = self.data.Close
        self.sma1 = self.I(SMA, close, self.n1)
        self.sma2 = self.I(SMA, close, self.n2)

    def next(self):
        if crossover(self.sma1, self.sma2):
            self.buy()
        elif crossover(self.sma2, self.sma1):
            self.sell()



class Train():
    def init(self):
        end_date = datetime.datetime.now()
        start_date = end_date -datetime.timedelta(2)
        #fetch the data
        trainingdata = fetch_bybit_data_v5(True,start_date,end_date,"BTCUSDT",INTERVAL,'spot')
        #smooth the data
        trainingdata = _exponential_smooth(trainingdata,0.65)
        #produce indicators
        trainingdata = _produce_movement_indicators(trainingdata)

bt = Backtest(GOOG, SmaCross,
              cash=100000, commission=.002,
              exclusive_orders=True)
output = bt.run()
bt.plot()

     
