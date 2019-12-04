import requests
import json
import os
import unittest
import pokebase as pb
import sqlite3
import pokepy




#Project Members: SoJung Ham, Dylan Yono
#Information:  This program creates a database of stats of all Gen 1 Pokemon, which includes base speed, special defense, special attack
#               defense, attack, and HP. We will calculate the average base stats for typings of Pokemon (fire, water, grass).
                #example: Which Pokemon type has the highest attack stat on average?


def setUpDatabase(db_name):
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()

    return cur, conn

def get_pokemon_data():
    #SOMETHING TO FIX HERE 
    try:

        base_url = "https://pokeapi.co/api/v2/pokemon/?limit=10" #probably need to limit this to 151 pokemon only
        myDict = {}
        
            #getting each pokemon's unique URL 
        ugh = requests.get(base_url)
        all_pokemon = json.loads(ugh.text)

        number = 1
        for x in all_pokemon['results']:
            url = x["url"]
            r = requests.get(url)
            info = json.loads(r.text)
            myDict[number] =  info
            number += 1
               
    except:
        print("error when reading from url")
        myDict = {}

    return myDict 
    
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
    dumped_json_cache = json.dumps(cache_dict) #seriailze a dictionary to JSON
    fw = open(cache_file, "w") #open cache file 
    fw.write(dumped_json_cache) #write the json into the cache 
    fw.close() #close the filw 
    
def get_data_with_caching():

    request_url = "https://pokeapi.co/api/v2/pokemon/?limit=10"
    
    dir_path = os.path.dirname(os.path.realpath(__file__))
    CACHE_FNAME = dir_path + '/' + "pokemon_cache.json"
    CACHE_DICTION  = read_cache(CACHE_FNAME)
    try:
        if request_url in CACHE_DICTION:
        
            print("Using cache")
            #add them to a dictionary, where key = request_url and value = results
            #uhhhhhhhhhhhhhhhhhhh
            return CACHE_DICTION[request_url]
        
        #exception
        
        else: #if request_url does not exist in CACHE_DICTION, CREATE THE CACHE
        
            print("Fetching")
            ugh = requests.get(request_url)
            all_pokemon = json.loads(ugh.text)

            myDict = {}
                     
            number = 1
            for x in all_pokemon['results']:
                url = x["url"]
                r = requests.get(url)
                info = json.loads(r.text)
                myDict[number] =  info
                number += 1
            
            
            
            CACHE_DICTION[request_url] = myDict
                #write out the dictionary to a file using the function write_cache   
            write_cache(CACHE_FNAME, CACHE_DICTION)
            return myDict
    except:
        print("Exception")
        return None

#Fun table stuff
def setUpPokemonBaseStatsTable(pokemon_data, cur, conn):
    
    cur.execute("DROP TABLE IF EXISTS Pokemon")
    cur.execute('''CREATE TABLE Pokemon (pokemon_id INTEGER, 
                                        speed INTEGER, special_defense INTEGER, special_attack INTEGER, 
                                        defense INTEGER, attack INTEGER, hp INTEGER)''')
    info = pokemon_data.items()#why isnT IT WORKING HERE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    for pokemon in info:
         
        _pokemon_id = pokemon[1]['id']
        #something here....list indices not string but its a dictionary..??
        _speed = pokemon[1]['stats'][0]['base_stat']
        _special_defense = pokemon[1]['stats'][1]['base_stat']
        _special_attack = pokemon[1]['stats'][2]['base_stat']
        _defense = pokemon[1]['stats'][3]['base_stat']  
        _attack = pokemon[1]['stats'][4]['base_stat'] 
        _hp = pokemon[1]['stats'][5]['base_stat'] 

        cur.execute('INSERT INTO Pokemon (pokemon_id, speed, special_defense, special_attack, defense, attack, hp) VALUES (?, ?, ?, ?, ?, ?, ?)', (_pokemon_id, _speed, _special_defense, _special_attack, _defense, _attack, _hp))
    conn.commit()

def main():

    pokemon_data = get_data_with_caching()
    cur, conn = setUpDatabase('Pokemon.db')
    setUpPokemonBaseStatsTable(pokemon_data, cur, conn)



