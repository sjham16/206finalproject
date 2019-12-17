import requests
import json
import os
import sqlite3
import time
import csv
import matplotlib
import matplotlib.pyplot as plt

"""
Project Members: SoJung Ham, Dylan Yono
About: This program creates a database of stats of all Gen 1 Pokemon, which includes base speed, special defense, special attack,
defense, attack, and HP. We will calculate the average base stats for typings of Pokemon (fire, water, grass).
Example: Which Pokemon type has the highest attack stat on average?
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
    cur.execute('''CREATE TABLE IF NOT EXISTS PokemonStats (pokemon_id INTEGER, pokemon_name TEXT,
                speed INTEGER, special_defense INTEGER, special_attack INTEGER, 
                defense INTEGER, attack INTEGER, hp INTEGER, type_1 INTEGER, type_2 INTEGER)''')
    cur.execute('''CREATE TABLE IF NOT EXISTS PokemonTypes (pokemon_id INTEGER, 
                type_1 STRING, type_2 STRING)''')
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
    
def get_data_with_caching(cur,conn):
    """
    This function loads up to 20 items from the cache or API into the database.
    It takes a cursor and connection as input. 
    """
    myDictList = []
    dir_path = os.path.dirname(os.path.realpath(__file__))
    CACHE_FNAME = dir_path + '/' + "pokemon_cache.json"
    CACHE_DICTION  = read_cache(CACHE_FNAME)        
    
    search_url = "https://pokeapi.co/api/v2/pokemon/?limit=151"
    
    try:
        r = requests.get(search_url)
        search_data = json.loads(r.text)
    except:
        print("Error when reading from URL")
        return myDict
    
    number = 1
    for x in search_data['results']:
        url = x["url"]
        if url in CACHE_DICTION:
            print("Getting data from the cache")
            myDictList.append(CACHE_DICTION[url])
        else:
            print("Getting data from the api")
            r = requests.get(url)
            info = json.loads(r.text)
            myDictList.append(info)
            CACHE_DICTION[url] = info
            write_cache(CACHE_FNAME, CACHE_DICTION)
            print("Sleeping for one second because only 100 API requests are allowed per minute")
            time.sleep(1)

    try:
        cur.execute('SELECT * FROM PokemonStats')
        current = len(cur.fetchall())
    except:
        current = 0
    if current == 151:
        print("All original 151 Pokemon are in the database.")
        return None

    for pokemon in myDictList[current:current+20]:
            
        _pokemon_id = pokemon['id']
        _pokemon_name = pokemon['species']['name']
        _speed = pokemon['stats'][0]['base_stat']
        _special_defense = pokemon['stats'][1]['base_stat']
        _special_attack = pokemon['stats'][2]['base_stat']
        _defense = pokemon['stats'][3]['base_stat']  
        _attack = pokemon['stats'][4]['base_stat'] 
        _hp = pokemon['stats'][5]['base_stat'] 

        category = pokemon['types']
        _type_1 = category[0]['type']['name']
        _type_2 = ""
        if len(category) == 2:
            _type_2 = category[1]['type']['name']

        cur.execute('INSERT INTO PokemonStats (pokemon_id, pokemon_name, speed, special_defense, special_attack, defense, attack, hp) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', 
                                                (_pokemon_id, _pokemon_name, _speed, _special_defense, _special_attack, _defense, _attack, _hp))
        cur.execute('INSERT INTO PokemonTypes (pokemon_id, type_1, type_2) VALUES(?, ?, ?)', (_pokemon_id, _type_1, _type_2))

        print("Added #{}, {} to the Database".format(_pokemon_id,_pokemon_name))
        cur.execute('SELECT * FROM PokemonStats')
        current=len(cur.fetchall())
        conn.commit()
    if current == 151:
        print("All original 151 Pokemon are in the database.")
        return None
    else:
        print("Need to add more Pokemon to the database. The program will quit for now. Please run it again.")
        quit()

def calculate_stats(cur, conn):
    """
    This function's selects all the relevant data from the tables using a database join.
    It takes a cursor and connection as input.
    It returns the data it selects to be used in the stat calculation functions.
    """
    # Select the relevant data using database join
    cur.execute("""SELECT 
    PokemonStats.speed,
    PokemonStats.special_defense,
    PokemonStats.special_attack,
    PokemonStats.defense,
    PokemonStats.attack,
    PokemonStats.hp,
    PokemonTypes.type_1,
    PokemonTypes.type_2 
    FROM PokemonStats INNER JOIN PokemonTypes
    ON PokemonStats.pokemon_id = PokemonTypes.pokemon_id""")
    data = cur.fetchall()
    return data

# Calculate average base stats

def getAverageSpeedStats(data, pokemon_type):
    """
    This function calculates the average speed stat for a type.
    It takes the table data and a pokemon type as input.
    It returns the average speed stat for pokemon of that type.
    """
    total = 0
    count = 0
    for row in data:
        if pokemon_type in row:
            total += row[0]
            count +=1
    average = total/count
    return average

def getAverageSpecialDefenseStats(data, pokemon_type):
    """
    This function calculates the average special defense stat for a type.
    It takes the table data and a pokemon type as input.
    It returns the average special defense stat for pokemon of that type.
    """
    total = 0
    count = 0
    for row in data:
        if pokemon_type in row:
            total += row[1]
            count +=1
    average = total/count
    return average

def getAverageSpecialAttackStats(data, pokemon_type):
    """
    This function calculates the average special attack stat for a type.
    It takes the table data and a pokemon type as input.
    It returns the average special attack stat for pokemon of that type.
    """
    total = 0
    count = 0
    for row in data:
        if pokemon_type in row:
            total += row[2]
            count +=1
    average = total/count
    return average

def getAverageDefenseStats(data, pokemon_type):
    """
    This function calculates the average defense stat for a type.
    It takes the table data and a pokemon type as input.
    It returns the average defense stat for pokemon of that type.
    """
    total = 0
    count = 0
    for row in data:
        if pokemon_type in row:
            total += row[3]
            count +=1
    average = total/count
    return average

def getAverageAttackStats(data, pokemon_type):
    """
    This function calculates the average attack stat for a type.
    It takes the table data and a pokemon type as input.
    It returns the average attack stat for pokemon of that type.
    """
    total = 0
    count = 0
    for row in data:
        if pokemon_type in row:
            total += row[4]
            count +=1
    average = total/count
    return average

def getAverageHPStats(data, pokemon_type):
    """
    This function calculates the average hp stat for a type.
    It takes the table data and a pokemon type as input.
    It returns the average hp stat for pokemon of that type.
    """
    total = 0
    count = 0
    for row in data:
        if pokemon_type in row:
            total += row[5]
            count +=1
    average = total/count
    return average


# Visualize data

def createAverageSpeedGraph():
    """
    This function shows a graph of the average base speed stat for all pokemon types.
    It calls the getAverageSpeedStats function on every type.
    It visualizes that data using matplotlib.
    """
    data = calculate_stats(cur, conn)
    speedStats = {}
    pokemon_types = ['poison', 'grass', 'fire', 'flying', 'water', 'bug', 'normal', 'electric', 'ground', 'fairy', 'fighting', 'psychic',
            'rock', 'steel', 'ice', 'ghost', 'dragon']
    for _type in pokemon_types:
        speedStats[_type] = getAverageSpeedStats(data, _type)
    plt.bar(speedStats.keys(), speedStats.values(), color=['#c300c9', 
    '#33bf00', '#d10816', '#7acdde', '#0f2f91', '#7fff08', '#c9c9c9', '#fff200', '#3d2717', '#ff96dc', 
    '#66412b', '#640485', '#9c8972', '#9c9c9c', '#c2deff', '#240959', '#0007d1'], edgecolor = "gray")
    plt.ylabel('Points of Pokemon')
    plt.xlabel('Types')
    plt.title("Average Base Speed Stats v.s. Types of Pokemon")
    plt.show()

def createAverageSpecialDefenseGraph():
    """
    This function shows a graph of the average base special defense stat for all pokemon types.
    It calls the getAverageSpecialDefenseStats function on every type.
    It visualizes that data using matplotlib.
    """
    data = calculate_stats(cur, conn)
    specialDefenseStats = {}
    pokemon_types = ['poison', 'grass', 'fire', 'flying', 'water', 'bug', 'normal', 'electric', 'ground', 'fairy', 'fighting', 'psychic',
            'rock', 'steel', 'ice', 'ghost', 'dragon']
    for _type in pokemon_types:
        specialDefenseStats[_type] = getAverageSpecialDefenseStats(data, _type)
    plt.bar(specialDefenseStats.keys(), specialDefenseStats.values(), color=['#c300c9', 
    '#33bf00', '#d10816', '#7acdde', '#0f2f91', '#7fff08', '#c9c9c9', '#fff200', '#3d2717', '#ff96dc', 
    '#66412b', '#640485', '#9c8972', '#9c9c9c', '#c2deff', '#240959', '#0007d1'], edgecolor = "gray")
    plt.ylabel('Points of Pokemon')
    plt.xlabel('Types')
    plt.title("Average Base Special Defense Stats v.s. Types of Pokemon")
    plt.show()

def createAverageSpecialAttackGraph():
    """
    This function shows a graph of the average base special attack stat for all pokemon types.
    It calls the getAverageSpecialAttackStats function on every type.
    It visualizes that data using matplotlib.
    """
    data = calculate_stats(cur, conn)
    specialAttackStats = {}
    pokemon_types = ['poison', 'grass', 'fire', 'flying', 'water', 'bug', 'normal', 'electric', 'ground', 'fairy', 'fighting', 'psychic',
            'rock', 'steel', 'ice', 'ghost', 'dragon']
    for _type in pokemon_types:
        specialAttackStats[_type] = getAverageSpecialAttackStats(data, _type)
    plt.bar(specialAttackStats.keys(), specialAttackStats.values(), color=['#c300c9', 
    '#33bf00', '#d10816', '#7acdde', '#0f2f91', '#7fff08', '#c9c9c9', '#fff200', '#3d2717', '#ff96dc', 
    '#66412b', '#640485', '#9c8972', '#9c9c9c', '#c2deff', '#240959', '#0007d1'], edgecolor = "gray")
    plt.ylabel('Points of Pokemon')
    plt.xlabel('Types')
    plt.title("Average Base Special Attack Stats v.s. Types of Pokemon")
    plt.show()

def createAverageDefenseGraph():
    """
    This function shows a graph of the average base defense stat for all pokemon types.
    It calls the getAverageDefenseStats function on every type.
    It visualizes that data using matplotlib.
    """
    data = calculate_stats(cur, conn)
    defenseStats = {}
    pokemon_types = ['poison', 'grass', 'fire', 'flying', 'water', 'bug', 'normal', 'electric', 'ground', 'fairy', 'fighting', 'psychic',
            'rock', 'steel', 'ice', 'ghost', 'dragon']
    for _type in pokemon_types:
        defenseStats[_type] = getAverageDefenseStats(data, _type)
    plt.bar(defenseStats.keys(), defenseStats.values(), color=['#c300c9', 
    '#33bf00', '#d10816', '#7acdde', '#0f2f91', '#7fff08', '#c9c9c9', '#fff200', '#3d2717', '#ff96dc', 
    '#66412b', '#640485', '#9c8972', '#9c9c9c', '#c2deff', '#240959', '#0007d1'], edgecolor = "gray")
    plt.ylabel('Points of Pokemon')
    plt.xlabel('Types')
    plt.title("Average Base Defense Stats v.s. Types of Pokemon")
    plt.show()

def createAverageAttackGraph():
    """
    This function shows a graph of the average base attack stat for all pokemon types.
    It calls the getAverageAttackStats function on every type.
    It visualizes that data using matplotlib.
    """
    data = calculate_stats(cur, conn)
    attackStats = {}
    pokemon_types = ['poison', 'grass', 'fire', 'flying', 'water', 'bug', 'normal', 'electric', 'ground', 'fairy', 'fighting', 'psychic',
            'rock', 'steel', 'ice', 'ghost', 'dragon']
    for _type in pokemon_types:
        attackStats[_type] = getAverageAttackStats(data, _type)
    plt.bar(attackStats.keys(), attackStats.values(), color=['#c300c9', 
    '#33bf00', '#d10816', '#7acdde', '#0f2f91', '#7fff08', '#c9c9c9', '#fff200', '#3d2717', '#ff96dc', 
    '#66412b', '#640485', '#9c8972', '#9c9c9c', '#c2deff', '#240959', '#0007d1'], edgecolor = "gray")
    plt.ylabel('Points of Pokemon')
    plt.xlabel('Types')
    plt.title("Average Base Attack Stats v.s. Types of Pokemon")
    plt.show()

def createAverageHPGraph():
    """
    This function shows a graph of the average base HP stat for all pokemon types.
    It calls the getAverageHPStats function on every type.
    It visualizes that data using matplotlib.
    """
    data = calculate_stats(cur, conn)
    HPStats = {}
    pokemon_types = ['poison', 'grass', 'fire', 'flying', 'water', 'bug', 'normal', 'electric', 'ground', 'fairy', 'fighting', 'psychic',
            'rock', 'steel', 'ice', 'ghost', 'dragon']
    for _type in pokemon_types:
        HPStats[_type] = getAverageHPStats(data, _type)
    plt.bar(HPStats.keys(), HPStats.values(), color=['#c300c9', 
    '#33bf00', '#d10816', '#7acdde', '#0f2f91', '#7fff08', '#c9c9c9', '#fff200', '#3d2717', '#ff96dc', 
    '#66412b', '#640485', '#9c8972', '#9c9c9c', '#c2deff', '#240959', '#0007d1'], edgecolor = "gray")
    plt.ylabel('Points of Pokemon')
    plt.xlabel('Types')
    plt.title("Average Base HP Stats v.s. Types of Pokemon")
    plt.show()

def write_to_csv():
    """
    This function creates a csv file with the average base stat calculations for each type.
    """
    with open('pokemon_calc.csv', 'w', newline = '') as csvfile:
        fields = ['Pokemon Type', 'Average HP', 'Average Attack', 'Average Defense', 
                'Average Special Attack','Average Special Defense', 'Average Speed']

        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(fields)

        data = calculate_stats(cur, conn)
        typeNames = ['poison', 'grass', 'fire', 'flying', 'water', 'bug', 'normal', 'electric', 'ground', 'fairy', 'fighting', 'psychic',
                'rock', 'steel', 'ice', 'ghost', 'dragon']

        averageSpeeds = []
        for x in typeNames:
            speed = getAverageSpeedStats(data, x, cur, conn)
            averageSpeeds.append(speed)
        averageSpecialDefenses = []
        for x in typeNames:
            special_defense = getAverageSpecialDefenseStats(data, x, cur, conn)
            averageSpecialDefenses.append(special_defense)
        averageSpecialAttacks = []
        for x in typeNames:
            special_attack = getAverageSpecialAttackStats(data, x, cur, conn)
            averageSpecialAttacks.append(special_attack)
        averageDefenses = []
        for x in typeNames:
            defense = getAverageSpecialDefenseStats(data, x, cur, conn)
            averageDefenses.append(defense)
        averageAttacks = []
        for x in typeNames:
            attack = getAverageAttackStats(data, x, cur, conn)
            averageAttacks.append(attack)
        averageHps = []
        for x in typeNames:
            hp = getAverageHPStats(data, x, cur, conn)
            averageHps.append(hp)

        rows = zip(typeNames, averageSpeeds, averageSpecialDefenses, averageSpecialAttacks,
                averageDefenses, averageAttacks, averageHps)

        for x in rows:
            csvwriter.writerow(x)

        csvfile.close()

###############
# The program #
###############

print("Doing some program setup...")
cur, conn = setUpDatabase('videogames.db')
get_data_with_caching(cur, conn)

print("Welcome to the pokemon base stat viewer. Here you can view average base stats of each Pokemon typing for the original 151 Pokemon. Quite insightful!")
print("This program utilizes pokeapi.com, and created for the purpose of SI 206 Fall 2019 semester final project.")
print("What kind of data would you like to visualize?")
print("----------")

print("(1) Average HP")
print("(2) Average Attack")
print("(3) Average Defense")
print("(4) Average Special Attack")
print("(5) Average Special Defense")
print("(6) Average Speed")
print("(7) Write data to csv file")
print("'q' to quit the program")

print("----------")

userInput = input("Enter a number or 'q' to quit: ")

while userInput != 'q':
    if userInput == '1':
        createAverageHPGraph()
        print("Cool chart, right?")
        print("Anything else you want to do?")
        userInput = input("Enter a number or 'q' to quit: ")
        continue
    elif userInput =='2':
        print(createAverageAttackGraph())
        print("Cool chart, right?")
        print("Anything else you want to do?")
        userInput = input("Enter a number or 'q' to quit: ")
        continue
    elif userInput == '3':
        print(createAverageDefenseGraph())
        print("Cool chart, right?")
        print("Anything else you want to do?")
        userInput = input("Enter a number or 'q' to quit: ")
        continue
    elif userInput == '4':
        print(createAverageSpecialAttackGraph())
        print("Cool chart, right?")
        print("Anything else you want to do?")
        userInput = input("Enter a number or 'q' to quit: ")
        continue
    elif userInput == '5':
        print(createAverageSpecialDefenseGraph())
        print("Cool chart, right?")
        print("Anything else you want to do?")
        userInput = input("Enter a number or 'q' to quit: ")
        continue
    elif userInput == '6':
        print(createAverageSpeedGraph())
        print("Cool chart, right?")
        print("Anything else you want to do?")
        userInput = input("Enter a number or 'q' to quit: ")
        continue
    elif userInput == '7':
        write_to_csv()
        print("Wrote that to a csv file for you.")
        print("Anything else you want to do?")
        userInput = input("Enter a number or 'q' to quit: ")
        continue
    else:
        print("That's not a valid input....Please try again")
        userInput = input("Enter a number or 'q' to quit: ")
        continue

print("Bye!")
conn.close()