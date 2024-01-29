



from dbfuncs.dbops import with_db_lock


@with_db_lock
def create_tables(conn):
    """ create a table in the SQLite database """

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

def initDB():
    create_tables()
   
initDB()