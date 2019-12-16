import requests
import json
import os
import unittest
import sqlite3
import time
import matplotlib
import matplotlib.pyplot as plt

"""
Project Members: SoJung Ham, Dylan Yono
About: This program collects data from the Jikan API utilizing data from MyAnimeList.net.
It searches for anime that aired during the fall 2019 season.
Then, it collects the anime's rating (from MAL users) and the source material the anime is adapted from.
The information is put into a database and the average rating of each source material is calculated.
The program may visualize the average rating of each source material.
The program may also write the data to a text file.
"""

############################
# Setting up the functions #
############################

def setUpDatabase(db_name):
    """
    This function sets up a database.
    It takes a filename to name the database and returns a cursor and connection.
    """
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS AnimeScores 
    (id, title, score)''')
    cur.execute('''CREATE TABLE IF NOT EXISTS AnimeSources 
    (id, title, source)''')
    return cur, conn
    
def read_cache(CACHE_FNAME):
    """
    This function reads from the JSON cache file and returns a dictionary from the cache data. 
    If the file doesn’t exist, it returns an empty dictionary.
    """
    try:
        cache_file = open(CACHE_FNAME, 'r', encoding="utf-8")
        cache_contents = cache_file.read()
        CACHE_DICTION = json.loads(cache_contents)
        cache_file.close()
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
    
def get_anime_data(cur, conn):
    """
    This function loads up to 20 items from the cache or API into the database.
    It takes a cursor and connection as input.
    """
    dir_path = os.path.dirname(os.path.realpath(__file__))
    CACHE_FNAME = dir_path + '/' + "jikan_cache.json"
    CACHE_DICTION  = read_cache(CACHE_FNAME)
    
    url = "https://api.jikan.moe/v3/season/2019/fall"
    try:
        if url in CACHE_DICTION:
            print("Getting fall 2019 anime data from the cache...")
            search_data = CACHE_DICTION[url]
            fa19 = search_data["anime"]
        else:
            print("Getting fall 2019 anime data from the API...")
            r = requests.get(url)
            search_data = json.loads(r.text)
            fa19 = search_data["anime"]
            CACHE_DICTION[url] = search_data
            write_cache(CACHE_FNAME, CACHE_DICTION)
    except:
        print("error when reading from URL")
        return None

    try:
        cur.execute('SELECT * FROM AnimeScores')
        current = len(cur.fetchall())
    except:
        current = 0
    if current == 192:
        print("All fall 2019 anime are in the database.")
        return None
    for x in fa19[current:current+20]:
        _id = x["mal_id"]
        _title =x["title"]
        _score =x["score"]
        _source =x["source"]
        cur.execute('INSERT INTO AnimeScores (id, title, score) VALUES(?, ?, ?)', (_id, _title, _score))
        cur.execute('INSERT INTO AnimeSources (id, title, source) VALUES(?, ?, ?)', (_id, _title, _source))
        print("Added {}, with id {}, scoring {}, from source {} to the database.".format(_title,_id,_score,_source))
        cur.execute('SELECT * FROM AnimeScores')
        current = len(cur.fetchall())
        conn.commit()
    if current == 192:
        print("All fall 2019 anime are in the database.")
        return None
    else:
        print("Need to add more anime to the database. The program will quit for now. Please run it again.")
        quit()

def best_source(cur, conn):
    """
    This function does all the data calculation. It takes a cursor and connection as input.
    It cleans all the data and inputs the clean data into new tables.
    Using the anime id, a database join selects the anime title, score, and source material.
    It returns a list of tuples with each source and the average rating.
    """
    # First, clean the data
    # Clean the AnimeScores table
    cur.execute('DROP TABLE IF EXISTS CleanAnimeScores')
    cur.execute('''CREATE TABLE CleanAnimeScores 
    (id, title, score)''')
    cur.execute('SELECT * FROM AnimeScores')
    scores_raw = cur.fetchall()
    scores_clean = []
    for a,b,c in scores_raw:
        if type(c) == float:
            scores_clean.append((a,b,c))
    cur.executemany("INSERT INTO CleanAnimeScores (id, title, score) VALUES(?, ?, ?)", scores_clean)
    conn.commit()
    # Clean the AnimeSources table
    cur.execute('DROP TABLE IF EXISTS CleanAnimeSources')
    cur.execute('''CREATE TABLE CleanAnimeSources 
    (id, title, source)''')
    cur.execute('SELECT * FROM AnimeSources')
    sources_raw = cur.fetchall()
    sources_clean = []
    for a,b,c in sources_raw:
        if c != "-":
            sources_clean.append((a,b,c))
    cur.executemany("INSERT INTO CleanAnimeSources (id, title, source) VALUES(?, ?, ?)", sources_clean)
    conn.commit()
    # Next, calculate the average score for each source using database join
    cur.execute("SELECT * FROM CleanAnimeSources")
    cur.execute("""SELECT CleanAnimeScores.title, CleanAnimeScores.score, CleanAnimeSources.source FROM CleanAnimeScores
    INNER JOIN CleanAnimeSources ON CleanAnimeScores.id = CleanAnimeSources.id""")
    data = cur.fetchall()
    source_list =[]
    source_scores = {}
    source_counts = {}
    for a,b,c in data:
        if c not in source_list:
            source_list.append(c)
        if c not in source_scores:
            source_scores[c] = b
        else:
            source_scores[c] += b
        if c not in source_counts:
            source_counts[c] = 1
        else:
            source_counts[c] += 1
    score_by_source = []
    for source in source_list:
        avg = source_scores[source] / source_counts[source]
        score_by_source.append((source,avg))
    score_by_source = sorted(score_by_source, key=lambda x: x[1], reverse=True)
    return score_by_source

def make_chart(data):
    """
    This function makes a bar chart showing the average rating of anime by source material.
    It takes the data from best_source as input and shows a graph of the data using MatPlotLib.
    """
    names=[]
    values=[]
    for a,b in data:
        names.append(a)
        values.append(b)
    plt.bar(names,values, color=["#016122","#392f90","#fed1b4","#9f98e6","#0aecc9","#ec4c02","#7bfc88","#3c9883","#c404ef","#df7f2b","#cd128d","#268ab6"],edgecolor="gray")
    axes = plt.gca()
    axes.set_ylim([5,8])
    plt.ylabel('Average Rating (out of 10)')
    plt.xlabel('Source Material')
    plt.suptitle('Average rating of fall 2019 anime by source material')
    plt.show()

def write_to_txt(data):
    """
    This function takes the data from best_source as input.
    It creates a text file of the data with each item on a new line.
    """
    lst = []
    for x in data:
        lst.append(str(x[0]))
        lst.append(str(x[1]))
    with open('anime_data.txt', 'w',) as txtfile:
        for x in lst:
            txtfile.write(x)
            txtfile.write('\n')
    txtfile.close()

###############
# The program #
###############

cur, conn = setUpDatabase('videogames.db')
get_anime_data(cur, conn)
data = best_source(cur, conn)

print("""Welcome to the anime source material rater.
This program will visualize the average rating of fall 2019 anime by source material.""")
print("This program utilizes Jikan API, and created for the purpose of SI 206 Fall 2019 semester final project.")
print("What would you like to do?")
print("----------")

print("(1) show the graph")
print("(2) write the data to a text file")
print("(q) quit the program")

print("----------")

userInput = input("Enter a number or 'q' to quit: ")

while userInput != 'q':
    if userInput == '1':
        make_chart(data)
        print("Cool chart, right?")
        print("Anything else you want to do?")
        userInput = input("Enter a number or 'q' to quit: ")
        continue
    elif userInput =='2':
        write_to_txt(data)
        print("Just wrote the data to a text file for you.")
        print("Anything else you want to do?")
        userInput = input("Enter a number or 'q' to quit: ")
        continue
    else:
        print("That's not a valid input....Please try again")
        userInput = input("Enter a number or 'q' to quit: ")
        continue

cur.close()
conn.close()
print("Bye!")
