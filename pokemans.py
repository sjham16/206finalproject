import requests
import json
import os
import unittest
import pokebase as pb
import sqlite3
import pokepy




#Project Members: SoJung Ham, Dylan Yono
#Information: 

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
                #need to find a way to append these into one dictinoary....
                
            
        # pp = pprint.PrettyPrinter(indent=4)
        # pp.pprint(myDict)
        #getting stats is 
    except:
        print("error when reading from url")
        myDict = {}

    return myDict 
    



#Fun table stuff
def setUpPokemonBaseStatsTable(pokemon_data, cur, conn):
    
    cur.execute("DROP TABLE IF EXISTS Pokemon")
    cur.execute('''CREATE TABLE Pokemon (pokemon_id INTEGER, 
                                        speed INTEGER, special_defense INTEGER, special_attack INTEGER, 
                                        defense INTEGER, attack INTEGER, hp INTEGER)''')
    info = pokemon_data.values() #why isnT IT WORKING HERE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    for _ in info:
         

        _pokemon_id = info['id']
        _speed = info['stats'][0]['base_stat']
        _special_defense = info['stats'][1]['base_stat']
        _special_attack = info['stats'][2]['base_stat']
        _defense = info['stats'][3]['base_stat']  
        _attack = info['stats'][4]['base_stat'] 
        _hp = info['stats'][5]['base_stat'] 

        cur.execute('INSERT INTO Pokemon (pokemon_id, speed, special_defense, special_attack, defense, attack, hp) VALUES (?, ?, ?, ?, ?, ?, ?)', (_pokemon_id, _speed, _special_defense, _special_attack, _defense, _attack, _hp))
    conn.commit()
# create a cache of the first 151 pokemon
# get all of their stats in a nice table
# calculate the average of each typing 

pokemon_data = get_pokemon_data()
cur, conn = setUpDatabase('Pokemon.db')
setUpPokemonBaseStatsTable(pokemon_data, cur, conn)


