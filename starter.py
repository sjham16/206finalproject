import requests
import json
import os
import unittest
from jikanpy import Jikan



#Project Members: SoJung Ham, Dylan Yono
#Information: 

def get_jikan_data():
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
        url = "http://api.jikan.moe/v3/anime/1/stats"
        r = requests.get(url)
        myDict = json.loads(r.text)
        # pp = pprint.PrettyPrinter(indent=4)
        # pp.pprint(myDict)
        
    except:
        print("error when reading from url")
        myDict = {}

    return myDict 

shirt = get_jikan_data()
print(shirt)


def get_kitsu_data():
    try:
        url = "https://kitsu.io/api/edge/anime/1/"
        r = requests.get(url)
        myDict = json.loads(r.text)
    except:
        print("error when reading from url")
        myDict = {}
    return myDict
    
pants = get_kitsu_data()
print(pants)



# def read_cache(CACHE_FNAME):
#     """
#     This function reads from the JSON cache file and returns a dictionary from the cache data. 
#     If the file doesn’t exist, it returns an empty dictionary.
#     """

#     try:
#         cache_file = open(CACHE_FNAME, 'r', encoding="utf-8") # Try to read the data from the file
#         cache_contents = cache_file.read()  # If it's there, get it into a string
#         CACHE_DICTION = json.loads(cache_contents) # And then load it into a dictionary
#         cache_file.close() # Close the file, we're good, we got the data in a dictionary.
#     except:
#         CACHE_DICTION = {}
    
#     return CACHE_DICTION

# def get_data_with_caching(country_code, year, per_page=50):
#     """
#     This function uses the passed country_code and year to generate a
#     request_url and then checks if this url is in the dictionary
#     returned by read_cache.  If the request_url exists as a key in the dictionary, 
#     it should print 'Using cache for ' followed by the country_code and
#     return the results for that request_url.
#     If the request_url does not exist in the dictionary, the function should 
#     print "Fetching for " followed by the country_code and make a call to the
#     World Bank API to get and return the CO2 emission data list searched by country 
#     (or countries) and year.
#     The documentation of the API is at
#     https://datahelpdesk.worldbank.org/knowledgebase/articles/889392-about-the-indicators-api-documentation
#     If there were results, it should add them to a dictionary
#     (key is the request_url, and value is the results)
#     and write out the dictionary to a file using write_cache. If there was an exception 
#     during the search, it should print out "Exception" and return None.
#     """
#     info = "stats"
#     base_url    = "https://api.jikan.moe/v3/anime/1/stats"
    
#     dir_path = os.path.dirname(os.path.realpath(__file__))
#     CACHE_FNAME = dir_path + '/' + "cache_climate.json"
#     CACHE_DICTION  = read_cache(CACHE_FNAME)
#     try:
#         if request_url in CACHE_DICTION:
        
#             print("Using cache for" + str(country_code))
#             #add them to a dictionary, where key = request_url and value = results
#             #uhhhhhhhhhhhhhhhhhhh
#             return CACHE_DICTION[request_url]
        

#         #exception
        
#         else: #if request_url does not exist in CACHE_DICTION
        
#             print("Fetching for " + str(country_code))
#             r = requests.get(request_url)
#             myDict = json.loads(r.text)
            
#             CACHE_DICTION[request_url] = myDict
                
#                 #write out the dictionary to a file using the function write_cache   
#             write_cache(CACHE_FNAME, CACHE_DICTION)
#             return myDict
#     except:
#         print("Exception")
#         return None
        