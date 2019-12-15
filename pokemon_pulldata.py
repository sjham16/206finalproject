import requests
import json
import os
import sqlite3
import time
import csv

import matplotlib
import matplotlib.pyplot as plt




#Project Members: SoJung Ham, Dylan Yono
#Information:  This program creates a database of stats of all Gen 1 Pokemon, which includes base speed, special defense, special attack
#               defense, attack, and HP. We will calculate the average base stats for typings of Pokemon (fire, water, grass).
                #example: Which Pokemon type has the highest attack stat on average?


def setUpDatabase(db_name):
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()

    cur.execute('''CREATE TABLE IF NOT EXISTS PokemonStats (pokemon_id INTEGER PRIMARY KEY, pokemon_name TEXT,
                                        speed INTEGER, special_defense INTEGER, special_attack INTEGER, 
                                        defense INTEGER, attack INTEGER, hp INTEGER, type_1 INTEGER, type_2 INTEGER)''')

    return cur, conn
    
def read_cache(CACHE_FNAME):
    """
    This function reads from the JSON cache file and returns a dictionary from the cache data. 
    If the file doesn’t exist, it returns an empty dictionary.
    """

    try:
        cache_file = open(CACHE_FNAME, 'r', encoding="utf-8") # Try to read the data from the file
        cache_contents = cache_file.read()  # If it's there, get it into a string
        CACHE_DICTION = json.loads(cache_contents) # And then load it into a dictionary
        cache_file.close() # Close the file, we're good, we got the data in a dictionary.
    except:
        CACHE_DICTION = {}
    
    return CACHE_DICTION

def write_cache(cache_file, cache_dict):
    """
    This function encodes the cache dictionary (cache_dict) into JSON format and
    writes the contents in the cache file (cache_file) to save the search results.
    """
    dumped_json_cache = json.dumps(cache_dict) 
    fw = open(cache_file, "w") 
    fw.write(dumped_json_cache) 
    fw.close() 
    
def get_data_with_caching():
    """
    This function first extracts data from the supplied URL with the requests module --> json.
    The file is a key-value pair of the pokemon name, and the url leading to its data. 
    Within a for loop, if the url exists in the CACHE_DICTION (cache dictionary), it prints out the data 
    and adds it to an empty dictionary. 
    If the url does not exist within CACHE_DICTION, it proceeds to get the data and add to the cache. 
    It only extracts 20 items at a time, so this program must be rerun to gain sufficient data.
    Finally, it returns data in the form of a dictionary. 
    
    """
    
    myDict = {}
    dir_path = os.path.dirname(os.path.realpath(__file__))
    CACHE_FNAME = dir_path + '/' + "pokemon_cache.json"
    CACHE_DICTION  = read_cache(CACHE_FNAME)
    try:
        pass

    try:
        base_url = "https://pokeapi.co/api/v2/pokemon/?page={}".format(page)
        
    
    # try:
    #     ugh = requests.get(request_url)
    #     all_pokemon = json.loads(ugh.text)
    # except:
    #     print("Error when reading from URL")
    #     return myDict
    
    # number = 1
    # index = 0
    # for x in all_pokemon['results']:
    #     url = x["url"]
    #     if url in CACHE_DICTION:
    #         print("Getting data from the cache")
    #         myDict[number] = CACHE_DICTION[url]
    #         number +=1
    #     else:
    #         print("Getting data from the api")
    #         r = requests.get(url)
    #         info = json.loads(r.text)
    #         myDict[number] =  info
    #         CACHE_DICTION[url] = myDict[number]
    #         write_cache(CACHE_FNAME, CACHE_DICTION)
    #         number += 1
    #         index +=1
    #         if index == 20:
    #             break
            
    # return myDict