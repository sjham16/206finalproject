import requests
import json
import os
import sqlite3
import time
import csv
import matplotlib
import matplotlib.pyplot as plt

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
    
def get_mario_data():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    CACHE_FNAME = dir_path + '/' + "mario_cache.json"
    CACHE_DICTION  = read_cache(CACHE_FNAME)
    d={}
    pages=[1,2,3,4,5,6,7,8]
    for x in pages:
        try:
            url = "https://api.rawg.io/api/games?page={}&page_size=20&search=mario&publishers=nintendo".format(x)
            if url in CACHE_DICTION:
                print("Getting data from the cache...")
                d[x] = CACHE_DICTION[url]
            else:
                print("Requesting the data from the API...")
                r = requests.get(url)
                d[x] = json.loads(r.text)
                CACHE_DICTION[url] = d[x]
                write_cache(CACHE_FNAME, CACHE_DICTION)
        except:
            print("error when reading from url")
            d = {}
    return d

def make_mario_database(mario, cur, conn):
    cur.execute("DROP TABLE IF EXISTS MarioRatings")
    cur.execute('''CREATE TABLE MarioRatings 
    (id INTEGER PRIMARY KEY, game_name STRING, rating STRING)''')
    pages=[1,2,3,4,5,6,7,8]
    for page in pages:
        for x in mario[page]["results"]:
            _id = x["id"]
            _game_name = x["name"]
            _rating = x["rating"]
            cur.execute('INSERT INTO MarioRatings (id, game_name, rating) VALUES(?, ?, ?)', (_id, _game_name, _rating))
    conn.commit()
    
    cur.execute("DROP TABLE IF EXISTS MarioReleaseDates")
    cur.execute('''CREATE TABLE MarioReleaseDates 
    (id INTEGER PRIMARY KEY, game_name STRING, release_date STRING)''')
    pages=[1,2,3,4,5,6,7,8]
    for page in pages:
        for x in mario[page]["results"]:
            _id = x["id"]
            _game_name = x["name"]
            _release_date = x["released"]
            cur.execute('INSERT INTO MarioReleaseDates (id, game_name, release_date) VALUES(?, ?, ?)', (_id, _game_name, _release_date))
    conn.commit() 

def decade_rate(mario, cur, conn):
    # First, convert release date data into a decade, then create a new table of decades
    cur.execute("SELECT id, game_name, release_date FROM MarioReleaseDates")
    original_release_tuples = cur.fetchall()
    year_tuples=[]
    decade_tuples=[]
    for a,b,c in original_release_tuples:
        try:
            year_tuples.append((a,b,c[:4]))
        except:
            continue
    # The try/except block removes any data from the dataset that is missing a release date
    for a,b,c in year_tuples:
        if 1979 < int(c) < 1990:
            decade_tuples.append((a,b,"1980s"))
        elif 1989 < int(c) < 2000:
            decade_tuples.append((a,b,"1990s"))
        elif 1999 < int(c) < 2001:
            decade_tuples.append((a,b,"2000s"))
        elif 2009 < int(c) < 2020:
            decade_tuples.append((a,b,"2010s"))
    cur.execute("DROP TABLE IF EXISTS MarioDecades")
    cur.execute('''CREATE TABLE MarioDecades 
    (id INTEGER PRIMARY KEY, game_name STRING, release_decade STRING)''')
    cur.executemany("INSERT INTO MarioDecades (id, game_name, release_decade) VALUES(?, ?, ?)", decade_tuples)
    conn.commit()
    # Next, calculate the average rating for each decade using database join
    avg_80s = 0
    avg_80s_counter = 0
    avg_90s = 0
    avg_90s_counter = 0
    avg_00s = 0
    avg_00s_counter = 0
    avg_10s = 0
    avg_10s_counter = 0
    cur.execute("""SELECT MarioRatings.game_name, MarioRatings.rating, MarioDecades.release_decade FROM MarioRatings
    INNER JOIN MarioDecades ON MarioRatings.id = MarioDecades.id""")
    gdr_tups = cur.fetchall()
    for a,b,c in gdr_tups:
        if b == 0:
            continue
        else:
            if c == "1980s":
                avg_80s += float(b)
                avg_80s_counter += 1
            elif c == "1990s":
                avg_90s += float(b)
                avg_90s_counter += 1
            elif c == "2000s":
                avg_00s += float(b)
                avg_00s_counter += 1
            elif c == "2010s":
                avg_10s += float(b)
                avg_10s_counter += 1
    avg_80s = avg_80s/avg_80s_counter
    avg_90s = avg_90s/avg_90s_counter
    avg_00s = avg_00s/avg_00s_counter
    avg_10s = avg_10s/avg_10s_counter
    avg_by_decade = [("1980s",avg_80s),("1990s",avg_90s),("2000s",avg_00s),("2010s",avg_10s)]
    return avg_by_decade

def decade_rating_chart(data):
    names=[]
    values=[]
    for a,b in data:
        names.append(a)
        values.append(b)
    plt.plot(names,values)
    axes = plt.gca()
    axes.set_ylim([3.75,4.25])
    plt.ylabel('Rating (out of 5)')
    plt.xlabel('Decade')
    plt.suptitle('Average rating of Mario games by decade of release')
    plt.grid()
    plt.show()

def write_to_txt(data):
    lst = []
    for x in data:
        lst.append(str(x[0]))
        lst.append(str(x[1]))
    with open('mario_data.txt', 'w',) as txtfile:
        for x in lst:
            txtfile.write(x)
            txtfile.write('\n')
    txtfile.close()

print("Doing some program setup...")
mario = get_mario_data()
cur, conn = setUpDatabase('videogames.db')
make_mario_database(mario, cur, conn)
data = decade_rate(mario, cur, conn)
# decade_rating_chart(data)
# write_to_txt(data)


print("""Welcome to the Mario video game decade rater.
This program will visualize the average rating for each decade of Mario games.""")
print("This program utilizes RAWG Video Games Database API, and created for the purpose of SI 206 Fall 2019 semester final project.")
print("What would you like to do?")
print("----------")

print("(1) show the graph")
print("(2) write the data to a text file")
print("(q) quit the program")

print("----------")

userInput = input("Enter a number or 'q' to quit: ")

while userInput != 'q':
    if userInput == '1':
        decade_rating_chart(data)
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