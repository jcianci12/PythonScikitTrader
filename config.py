
import decimal


TEST=False

BASE_URL = "https://api-testnet.bybit.com" if TEST else "https://api.bybit.com"

WEBSOCKET_BASE_URL = "wss://stream.bybit.com/realtime"

ACCOUNT_TYPE = "SPOT" if TEST else "UNIFIED"

SYMBOL = "BTCUSDT"

MAXBUYPERCENTOFCAPITAL = 10
MAXSELLPERCENTOFCAPITAL = 20

MINIMUMBTCTRANSACTIONSIZE = 0.000048

TAKEPROFIT = 1
STOPLOSS = 5

BUYTHRESHOLD = 0.8
SELLTHRESHOLD = 0.4

DATALENGTHFORTRAININGINDAYS = 7
DATALENGTHFORTRADINGINDAYS = 1

INTERVAL = '5m'

ALWAYSRETRAIN = False
TESTRETRAINATSTART = False


PERCENTCHANGEINDICATOR = 0.005
LOOKAHEADVALUE = 60

PLOTBACKTEST = False
PLOTPROGRESS = True
SIMULATETRADE = False

GRAPHVIEWWINDOW = 30
ALLOWEDTOSELL = False

ORDERCOLUMNS = ['uid', 'date','symbol', 'side',"usdt","btc","total", 'qty', 'entryprice', 'takeprofitprice', 'stoplossprice', 'takeprofitid', 'stoplossid', 'profit', 'completedtime','exitprice']
EXCLUDECOLUMNS = ['opentime', 'open', 'high', 'low', 'close', 
                  'volume', 
                  '14 period RSI',
                                                           #'MACD', 
                                                           'SIGNAL', '14 period STOCH K', 'MFV', '14 period ATR', 'MOM',
                                                           '14 period MFI', 
                                                           #'ROC', 
                                                           'OBV',
                                                        '20 period CCI',
                                                           #'14 period EMV.',
                                                           'VIm',
                                                           'VIp', 'ema50', 
                                                           #'ema21', 
                                                           #'ema15', 
                                                           #'ema5', 
                                                           'normVol']
PREDCOLUMNS = ['pred', 'preddec']

TRAINONLY = True
TRADINGPAIR = "BTC/USDT"