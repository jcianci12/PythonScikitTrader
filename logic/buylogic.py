from bybitapi import place_buy_order
from config import *
from functions.logger import logger
from functions.map_range import map_range


def buylogic(confidence_score,buythreshold,usdtbalance):
    
    minbuyamount = 0.2 #dont wanna buy too low an amount.
    capitalpercent = map_range(confidence_score,buythreshold,1,minbuyamount,MAXBUYPERCENTOFCAPITAL)
    transactionamount = ((capitalpercent/100) * usdtbalance)
    logger("Decided to buy %", capitalpercent , " of USDT balance. |USDT balance: ",usdtbalance," | Market value: ",transactionamount , "transaction amount:",  transactionamount)

    if(transactionamount>MINIMUMTRANSACTIONSIZE):
        logger("Enough USDT to cover purchase of ","USDT"," balance is:" ,usdtbalance) 
        response = place_buy_order(TEST,"BTCUSDT","USDT",10,5,capitalpercent)
        print(response)
    else:
        logger("Not enough ","USDT"," balance is:" ,usdtbalance)