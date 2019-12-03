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
        url = "http://pokeapi.co/api/v2/"
        r = requests.get(url)
        myDict = json.loads(r.text)
        # pp = pprint.PrettyPrinter(indent=4)
        # pp.pprint(myDict)
        
    except:
        print("error when reading from url")
        myDict = {}

    return myDict 

shirt = get_pokemon_data()
print(shirt)