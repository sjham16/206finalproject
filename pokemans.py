import requests
import json
import os
import unittest
import pokebase as pb




#Project Members: SoJung Ham, Dylan Yono
#Information: 

def get_pokemon_data():
    """
    This function takes a country code (e.g. USA, BRA) and year (e.g. 2004).
    Call the World Bank API to get population data searched by country and year.
    Return the data from API after converting to a python list
    that has population related information.
    Once you receive data from the API, paste the data to 
    JSON Online Editor and look at the contents.

    params = str(lat)
     """
    try:
        url = "https://pokeapi.co/api/v2/pokemon/1/"
        r = requests.get(url)
        myDict = json.loads(r.text)
        # pp = pprint.PrettyPrinter(indent=4)
        # pp.pprint(myDict)
        #getting stats is 
    except:
        print("error when reading from url")
        myDict = {}

    return myDict 

shirt = get_pokemon_data()['stats']
print(shirt)

#Fun table stuff
conn = sqlite3.connect('pokemon.sqlite')
cur = conn.cursor()

cur.execute('''CREATE TABLE IF NOT EXISTS Pokemon (id INTEGER PRIMARY KEY, 
                                                    speed INTEGER, special-defense INTEGER, special-attack INTEGER, 
                                                    attack INTEGER, hp INTEGER, , type STRING))''')

#create a cache of the first 151 pokemon
#get all of their stats in a nice table
# calculate the average of each typing 