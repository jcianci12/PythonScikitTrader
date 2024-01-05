
import datetime
import sqlite3

_conn = 0

def create_connection():
    db_file = "orders.db"
    """ create a database connection to an SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(f"SQLite version: {sqlite3.version}")
        return conn
    except sqlite3.Error as e:
        print(e)
    return conn
def getConnection():
    global _conn
    if  _conn ==0:
        _conn=create_connection()
        return _conn
    



def create_tables(conn):
    """ create a table in the SQLite database """
    try:
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                clientOrderId TEXT,
                datetime TEXT,
                symbol TEXT,
                side TEXT,
                usdtbalance REAL,
                btcbalance REAL,
                totalbalance REAL,
                filled REAL,
                price REAL,
                tp REAL,
                sl REAL,
                profit TEXT,
                exitprice TEXT,
                column3 TEXT
            )
        ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS closed_orders (
                clientOrderId TEXT,
                datetime TEXT,
                symbol TEXT,
                side TEXT,
                usdtbalance REAL,
                btcbalance REAL,
                totalbalance REAL,
                filled REAL,
                price REAL,
                tp REAL,
                sl REAL,
                profit TEXT,
                exitprice TEXT,
                column3 TEXT
            )
        ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS state (
                rowid INTEGER PRIMARY KEY,
                pendingorder BIT(1)
            )
        ''')
        cur.execute('''
            INSERT INTO state (rowid, pendingorder) VALUES (?, ?)
        ''', (1, 0))  # or whatever initial value you want for 'pendingorder'
    except sqlite3.Error as e:
        print(e)

def initDB():
    global conn
    conn = getConnection()
    if conn is not None:
        create_tables(conn)
    else:
        print("Error! cannot create the database connection.")


    

initDB()