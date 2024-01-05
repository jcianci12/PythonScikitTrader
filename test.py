


import os

from db.dbinit import initDB


os.mkdir("test123", mode = 0o777)
initDB()