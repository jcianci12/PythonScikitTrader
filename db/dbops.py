
import datetime
import random
import sqlite3
from config import TRADINGPAIR
from db.dbinit import conn
import time


def with_db_lock(func):
    """A decorator to handle SQLite database locks."""
    def wrapper(*args, **kwargs):
        max_backoff_time = 16  # Maximum backoff time
        base_backoff_time = 0.5  # Base backoff time
        attempt = 0  # Number of attempts made

        while True:
            try:
                with sqlite3.connect('orders.db', timeout=5) as conn:
                    print("Not locked, proceeding")
                    return func(conn, *args, **kwargs)
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e):
                    backoff_time = min(max_backoff_time, base_backoff_time * 2 ** attempt)
                    print(f"Locked, waiting {backoff_time} seconds")
                    time.sleep(backoff_time + random.random())  # Add some randomness to avoid thundering herd problem
                    attempt += 1
                else:
                    raise e
    return wrapper

@with_db_lock
def log_order(conn, buyresponse, fee, symbol, side, usdtbalance, btcbalance, tp, sl):
    """ log order to the SQLite database """
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
@with_db_lock
def remove_closed_order_from_open_orders(conn,order):
    """Remove closed order from the SQLite database"""

    cur = conn.cursor()
    # Prepare the DELETE statement
    delete_stmt = "DELETE FROM orders WHERE clientOrderId = ?"
    # Execute the DELETE statement
    cur.execute(delete_stmt, (order['clientOrderId'],))

   


@with_db_lock
def setpending(conn,pendingorder):
    """ log order to the SQLite database """
    cur = conn.cursor()
    cur.execute('''
        INSERT OR REPLACE INTO state (
            rowid,
            pendingorder
        ) VALUES (?, ?)
    ''', (
        1,  # constant PRIMARY KEY
        pendingorder
    ))

@with_db_lock
def getpending(con):
    """ Retrieve pending order from the SQLite database """
    
    cur = con.cursor()
    cur.execute('''
        SELECT pendingorder FROM state WHERE rowid = ?
    ''', (1,))  # we use 1 because we know we only have one row with rowid = 1
    result = cur.fetchone()
    if result is not None:
        return result[0]
    else:
        return None  # or some default value

@with_db_lock
def save_closed_order(conn, order):
    """ Save a closed order to the database """
        
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
        

@with_db_lock
def save_updated_prices(conn, orders):
    """ Save updated prices to the SQLite database """

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
      
@with_db_lock
def fetchAllOrders(conn):
   
    cur = conn.cursor()
    cur.execute("SELECT * FROM orders")
    rows = cur.fetchall()
    orders = [dict(zip([column[0] for column in cur.description], row)) for row in rows]
    return orders