
import datetime
import sqlite3
from config import TRADINGPAIR
from db.dbinit import conn

def log_order(buyresponse, fee, symbol, side, usdtbalance, btcbalance, tp, sl):
    """ log order to the SQLite database """
    try:
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO orders (
                clientOrderId,
                datetime,
                symbol,
                side,
                usdtbalance,
                btcbalance,
                totalbalance,
                filled,
                price,
                tp,
                sl,
                profit,
                exitprice,
                column3
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            buyresponse['clientOrderId'],
            datetime.datetime.now(),
            symbol,
            side,
            usdtbalance,
            btcbalance,
            usdtbalance + btcbalance*buyresponse['price'],
            buyresponse['filled']-fee,
            buyresponse['price'],
            tp,
            sl,
            "",
            "",
            ""
        ))
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print(e)

def save_closed_order( order):
    """ Save a closed order to the database """
    try:
        
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO closed_orders (
                clientOrderId,
                datetime,
                symbol,
                side,
                usdtbalance,
                btcbalance,
                totalbalance,
                filled,
                price,
                tp,
                sl,
                profit,
                exitprice,
                column3
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            order['clientOrderId'],
            order['datetime'],
            order['symbol'],
            order['side'],
            order['usdt'],
            order['btc'],
            order['total'],
            order['filled'],
            order['exitprice'],
            order['tp'],
            order['sl'],
            order['profit'],
            order['exitprice'],
            order['column3']
        ))
        conn.commit()
        conn.close
    except sqlite3.Error as e:
        print(e)


def save_updated_prices( orders):
    """ Save updated prices to the SQLite database """
    try:
        cur = conn.cursor()
        for order in orders:
            cur.execute('''
                UPDATE orders SET
                datetime = ?,
                symbol = ?,
                side = ?,
                usdtbalance = ?,
                btcbalance = ?,
                totalbalance = ?,
                filled = ?,
                price = ?,
                tp = ?,
                sl = ?,
                profit = ?,
                exitprice = ?,
                column3 = ?
                WHERE clientOrderId = ?
            ''', (
                order['datetime'],
                order['symbol'],
                order['side'],
                order['usdtbalance'],
                order['btcbalance'],
                order['totalbalance'],
                order['filled'],
                order['price'],
                order['tp'],
                order['sl'],
                order['profit'],
                order['exitprice'],
                order['column3'],
                order['clientOrderId']
            ))
        conn.commit()
    except sqlite3.Error as e:
        print(e)

def fetchAllOrders():
    cur = conn.cursor()
    cur.execute("SELECT * FROM orders")
    rows = cur.fetchall()
    orders = [dict(zip([column[0] for column in cur.description], row)) for row in rows]

    return orders