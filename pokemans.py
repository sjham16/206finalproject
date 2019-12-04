import requests
import json
import os
import unittest
import pokebase as pb





#Project Members: SoJung Ham, Dylan Yono
#Information: 

# def setUpDatabase(db_name):
    

    # conn = sqlite3.connect(db_name)
    # cur = conn.cursor()

    # return cur, conn

def get_pokemon_data():

    try:
        url = "https://pokeapi.co/api/v2/pokemon/" #probably need to limit this to 151 pokemon only
        r = requests.get(url)
        myDict = json.loads(r)
        # pp = pprint.PrettyPrinter(indent=4)
        # pp.pprint(myDict)
        #getting stats is 
    except:
        print("error when reading from url")
        myDict = {}

    return myDict 
    



#Fun table stuff
# def setUpPokemonBaseStatsTable(pokemon_data, cur, conn):
    
#     cur.execute("DROP TABLE IF EXISTS Pokemon")
#     cur.execute('''CREATE TABLE Pokemon (pokemon_id INTEGER PRIMARY KEY, 
#                                         speed INTEGER, special_defense INTEGER, special_attack INTEGER, 
#                                         defense INTEGER, attack INTEGER, hp INTEGER)''')
#     info = pokemon_data['stats']

#     for stat in info:
#         _pokemon_id = info['id']
#         _speed = info[0]['base_stat']
#         _special_defense = info[1]['base_stat']
#         _special_attack = info[2]['base_stat']
#         _defense = info[3]['base_stat']  
#         _attack = info[4]['base_stat'] 
#         _hp = info[5]['base_stat'] 

#         cur.execute('INSERT INTO Pokemon (pokemon_id, speed, special_defense, special_attack, defense, attack, hp) VALUES (?, ?, ?, ?, ?, ?, ?)', (_pokemon_id, _speed, _special_defense, _special_attack, _defense, _attack, _hp))
#     conn.commit()
#create a cache of the first 151 pokemon
#get all of their stats in a nice table
# calculate the average of each typing 

def main():
    print(get_pokemon_data())
    # cur, conn = setUpDatabase('Pokemon.sqlite')
