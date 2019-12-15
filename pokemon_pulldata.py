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

    cur.execute('''CREATE TABLE IF NOT EXISTS PokemonStats (pokemon_id INTEGER, pokemon_name TEXT,
                                        speed INTEGER, special_defense INTEGER, special_attack INTEGER, 
                                        defense INTEGER, attack INTEGER, hp INTEGER, type_1 INTEGER, type_2 INTEGER)''')

    cur.execute('''CREATE TABLE IF NOT EXISTS TypeCategories (id INTEGER, title TEXT)''')

    try:
        cur.execute('SELECT * FROM PokemonStats')
        test = len(cur.fetchall())
        if test == 151:
            return cur, conn
        else: 
            error
    except:
        cur.execute('INSERT OR IGNORE INTO PokemonStats (pokemon_id, pokemon_name, speed, special_defense, special_attack, defense, attack, hp, type_1, type_2) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (1,'placeholder','_', '_', '_', '_', '_', '_', '_', '_'))
        print("anna oop")
        conn.commit()

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
    
def get_data_with_caching(cur, conn):
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
        cur.execute('''SELECT pokemon_id FROM PokemonStats WHERE pokemon_name = "placeholder"''')
        page = cur.fetchone()[0]
        print("pulling data from page below:")
        print(page)
        cur.execute('''DELETE From PokemonStats WHERE pokemon_name = "placeholder"''')
        conn.commit()
    except:
        return None

    if page == 9:
        return None

    try:
        url = "https://pokeapi.co/api/v2/pokemon/?page={}".format(page)
        if url in CACHE_DICTION:
            print("Getting data from the pokemon cache...")
            myDict[page] = CACHE_DICTION[url]

            for x in myDict[page]['results']:
                individual_url = x['url']
                r = requests.get(individual_url)
                
                info = json.loads(r.text)

                for pokemon in info:

                    _pokemon_id = pokemon[1]['id']
                    _pokemon_name = pokemon[1]['species']['name']
                    #something here....list indices not string but its a dictionary..??
                    _speed = pokemon[1]['stats'][0]['base_stat']
                    _special_defense = pokemon[1]['stats'][1]['base_stat']
                    _special_attack = pokemon[1]['stats'][2]['base_stat']
                    _defense = pokemon[1]['stats'][3]['base_stat']  
                    _attack = pokemon[1]['stats'][4]['base_stat'] 
                    _hp = pokemon[1]['stats'][5]['base_stat'] 

                    category = pokemon[1]['types']

                    type1 = category[0]['type']['name']
                    cur.execute("SELECT id FROM TypeCategories WHERE title = ? LIMIT 1", (type1, ))
                    c = cur.fetchone()[0]
                    _type_1 = c
                    _type_2 = ""

                    if len(category) == 2:
                        type2 = category[1]['type']['name']
                        cur.execute("SELECT id FROM TypeCategories WHERE title = ? LIMIT 1", (type2, ))
                        d = cur.fetchone()[0]
                        _type_2 = d
                    cur.execute('INSERT INTO PokemonStats (pokemon_id, pokemon_name, speed, special_defense, special_attack, defense, attack, hp, type_1, type_2) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', 
                                                    (_pokemon_id, _pokemon_name, _speed, _special_defense, _special_attack, _defense, _attack, _hp, _type_1, _type_2))
                    conn.commit()
                    print("wrote the items to the database from the cache")
        else:
            print("Requesting data from the Pokemon APi....")
            r = requests.get(url)
            myDict[page] = json.loads(r.text)
            CACHE_DICTION[url] = myDict[page]
            write_cache(CACHE_FNAME, CACHE_DICTION)

            for x in myDict.items():
                _pokemon_id = pokemon[1]['id']
                _pokemon_name = pokemon[1]['species']['name']
                #something here....list indices not string but its a dictionary..??
                _speed = pokemon[1]['stats'][0]['base_stat']
                _special_defense = pokemon[1]['stats'][1]['base_stat']
                _special_attack = pokemon[1]['stats'][2]['base_stat']
                _defense = pokemon[1]['stats'][3]['base_stat']  
                _attack = pokemon[1]['stats'][4]['base_stat'] 
                _hp = pokemon[1]['stats'][5]['base_stat'] 

                category = pokemon[1]['types']

                type1 = category[0]['type']['name']
                cur.execute("SELECT id FROM TypeCategories WHERE title = ? LIMIT 1", (type1, ))
                c = cur.fetchone()[0]
                _type_1 = c
                _type_2 = ""

                if len(category) == 2:
                    type2 = category[1]['type']['name']
                    cur.execute("SELECT id FROM TypeCategories WHERE title = ? LIMIT 1", (type2, ))
                    d = cur.fetchone()[0]
                    _type_2 = d
                cur.execute('INSERT INTO PokemonStats (pokemon_id, pokemon_name, speed, special_defense, special_attack, defense, attack, hp, type_1, type_2) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', 
                                                (_pokemon_id, _pokemon_name, _speed, _special_defense, _special_attack, _defense, _attack, _hp, _type_1, _type_2))
                conn.commit()
                print("wrote the items to the database from the API")
    except: 
            print("error when reading from the URL")
            d = {}
            


#--------------we setting up here-----------------
cur, conn = setUpDatabase('videogames.db')

pokemon = get_data_with_caching(cur, conn)
                
cur.execute('SELECT * FROM PokemonStats')
tester = len(cur.fetchall())
if tester == 151:
    cur.execute('''DELETE FROM PokemonStats WHERE pokemon_name = "placeholder"''')
elif tester != 150:
    print("""The program has saved some data to the database.
    We haven't caught all the Pokemon yet though. 
    You'll have to run the program again to collect more data.
    When every Pokemon we need  is in the database, we can set up the program.
    For now, the program will exit. Keep running it until it works!!""")
    quit()

conn.close()

        
    
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