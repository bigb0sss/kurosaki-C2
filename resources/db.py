import os
import pickle

from collections import OrderedDict

listenersDB = "db/storage/listeners.db"
beaconsDB   = "db/storage/beacons.db"

# Creating local storages
def dbLocalStorage():
    if os.path.exists("./db/") == False:
        os.mkdir("./db/")
    if os.path.exists("./db/listener/") == False:
        os.mkdir("./db/listener")
    if os.path.exists("./db/storage/") == False:
        os.mkdir("./db/storage")

# Writing data to DB
def writeToDB(db, data):
    with open(db, "ab") as d:   # ab = appending as binary format
        pickle.dump(data, d, pickle.HIGHEST_PROTOCOL)

# Reading data from DB
def readFromDB(db):
    data = []
    with open(db, 'rb') as d:   # rb = reading file fro ready-only in binary format
        while True:
            try:
                data.append(pickle.load(d))
            except EOFError:
                break
    return data

# Remove data from DB
def removeFromDB(db, data):
    # Reading data from DB
    dbData = readFromDB(db)
    dataToRemove = OrderedDict()

    for i in dbData:
        dataToRemove[i.data] = i
    
    del dataToRemove[data]

    with open(db, "wb") as d:   # wb = write-only in binary format
        for i in dataToRemove:
            pickle.dump(dataToRemove[i], d, pickle.HIGHEST_PROTOCOL)

# Purge DB
def purgeDB(db):
    if os.path.exists(db):
        os.remove(db)
    else:
        pass




