import requests
import json
import os
import sqlite3
import time
import csv
import matplotlib
import matplotlib.pyplot as plt

def setUpDatabase(db_name):
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()

    return cur, conn
    
def get_mario_data():
    d={}
    pages=[1,2,3,4,5,6,7,8]
    for x in pages:
        try:
            url = "https://api.rawg.io/api/games?page={}&page_size=20&search=mario&publishers=nintendo".format(x)
            r = requests.get(url)
            d[x] = json.loads(r.text)
        except:
            print("error when reading from url")
            d = {}
    return d

def make_mario_database(mario, cur, conn):
    cur.execute("DROP TABLE IF EXISTS MarioRatings")
    cur.execute('''CREATE TABLE MarioRatings 
    (id INTEGER PRIMARY KEY, game_name STRING, rating STRING)''')
    pages=[1,2,3,4,5,6,7,8]
    for page in pages:
        for x in mario[page]["results"]:
            _id = x["id"]
            _game_name = x["name"]
            _rating = x["rating"]
            cur.execute('INSERT INTO MarioRatings (id, game_name, rating) VALUES(?, ?, ?)', (_id, _game_name, _rating))
    conn.commit()
    
    cur.execute("DROP TABLE IF EXISTS MarioReleaseDates")
    cur.execute('''CREATE TABLE MarioReleaseDates 
    (id INTEGER PRIMARY KEY, game_name STRING, release_date STRING)''')
    pages=[1,2,3,4,5,6,7,8]
    for page in pages:
        for x in mario[page]["results"]:
            _id = x["id"]
            _game_name = x["name"]
            _release_date = x["released"]
            cur.execute('INSERT INTO MarioReleaseDates (id, game_name, release_date) VALUES(?, ?, ?)', (_id, _game_name, _release_date))
    conn.commit() 



mario = get_mario_data()
cur, conn = setUpDatabase('Mario.db')
make_mario_database(mario, cur, conn)

# pages=[1,2,3,4,5,6,7,8]
# for page in pages:
#     for x in mario[page]["results"]:
#         print("Title: " + x["name"])
#         print("Rating: " + str(x["rating"]))
#         print("Release Date: " + str(x["released"]))
#         print("ID: " + str(x["id"]))
#         print("---")