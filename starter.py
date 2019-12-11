import requests
import json
import os
import unittest
import sqlite3
import time


from jikanpy import Jikan



#Project Members: SoJung Ham, Dylan Yono
#Information: 

def setUpDatabase(db_name):
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()

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
    dumped_json_cache = json.dumps(cache_dict) #seriailze a dictionary to JSON
    fw = open(cache_file, "w") #open cache file 
    fw.write(dumped_json_cache) #write the json into the cache 
    fw.close() #close the filw 
    
def get_data_with_caching():

    api_anime_code = 1

    for anime in range(5):

        base_url = "https://api.jikan.moe/v3/search/anime?q=2013-2018&limit=101"
        #FIX this url
        request_url = base_url.format(api_anime_code)
    
        dir_path = os.path.dirname(os.path.realpath(__file__))
        CACHE_FNAME = dir_path + '/' + "jikan_cache.json"
        CACHE_DICTION  = read_cache(CACHE_FNAME)

        try:
            if request_url in CACHE_DICTION:
        
                print("Using jikan anime_list cache")
            

                return CACHE_DICTION[request_url]
        
        
        
            else: 
                #if request_url does not exist in CACHE_DICTION, CREATE THE CACHE
                print("Fetching")
                ugh = requests.get(request_url)
                all_anime = json.loads(ugh.text)

            # myDict = {}
                     
            # number = 1
            # for x in all_anime['results']:
            #     url = x["url"]
            #     r = requests.get(url)
            #     info = json.loads(r.text)
            #     myDict[number] =  info
            #     number += 1
            
            
            
                CACHE_DICTION[request_url] = all_anime
                #write out the dictionary to a file using the function write_cache   
                write_cache(CACHE_FNAME, CACHE_DICTION)

                api_anime_code += 1

                
        except:
            print("Exception")
            return None
    
    return all_anime
    
    #need to find a way to get 50 animes
    
#---------- database setup --------

def setUpAnimeInfoTable(anime_data, cur, conn):
    cur.execute("DROP TABLE IF EXISTS Anime")
    cur.execute('''CREATE TABLE Anime (anime_id INTEGER PRIMARY KEY, name TEXT,
                                        score INTEGER, rated TEXT, rated_id INTEGER)''')
    info = anime_data['results']
    
    #something is fucked up here
    count = 0

    for anime in info:
        _anime_id = anime["mal_id"]
        _name = anime["title"]
        _score = anime["score"]
        _rated = anime['rated']
        
        cur.execute("SELECT id FROM Rated WHERE rated = ? LIMIT 1", (_rated, ))
        c = cur.fetchone()[0]
        _rated_id = c


        cur.execute('INSERT INTO Anime (anime_id, name, score, rated, rated_id) VALUES (?, ?, ?, ?, ?)',
        (_anime_id, _name, _score, _rated, _rated_id))

        count = count + 1
        conn.commit()

        if count % 10 == 0:
            print("Pausing for a bit....")
            time.sleep(1)

def setUpRatedTable(anime_data, cur, conn):

    cur.execute("DROP TABLE IF EXISTS Rated")
    cur.execute("CREATE TABLE Rated (id INTEGER PRIMARY KEY, rated TEXT)")

    genre_list = []
    info = anime_data['results']

    for x in info:
        genre = x['rated']
        if genre not in genre_list:
            genre_list.append(genre)
    
    for i in range(len(genre_list)):
        cur.execute("INSERT INTO Rated (id, rated) VALUES (?,?)", (i, genre_list[i]))
    conn.commit()

            

anime_data = get_data_with_caching()
cur, conn = setUpDatabase('Anime.db')

setUpRatedTable(anime_data, cur, conn)
setUpAnimeInfoTable(anime_data, cur, conn)




