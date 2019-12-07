import requests
import json
import os
import sqlite3

def get_game_data():
    try:
        url = "https://api.rawg.io/api/games?page_size=5&search=pokemon"
        r = requests.get(url)
        myDict = json.loads(r.text)
    except:
        print("error when reading from url")
        myDict = {}
    return myDict
    
pants = get_game_data()
print(pants)