from bybitapi import place_sell_order
from config import *
from logger import logger
from map_range import map_range


def selllogic(confidence_score,sellthreshold,btcbalance,btcmarketvalue):
    capitalsymbol = "BTC"
    marketsymbol = "BTCUSDT"
    minsellamount = 0.2 #dont wanna sell too low an amount.
    capitalpercent = map_range(confidence_score,0,sellthreshold,minsellamount,MAXSELLPERCENTOFCAPITAL)
        
    transactionamount = (capitalpercent * btcbalance)*btcmarketvalue
    if(transactionamount>MINIMUMTRANSACTIONSIZE):
        logger("Decided to sell %", capitalpercent , " of BTC balance. |BTC balance: ",btcbalance," | Market value: ",btcmarketvalue , "transaction amount:" , transactionamount)
        response = place_sell_order(TEST, capitalsymbol, marketsymbol, 1)
        print(response)
    else:
        logger("Not enough ",capitalsymbol," balance is:" ,btcmarketvalue)