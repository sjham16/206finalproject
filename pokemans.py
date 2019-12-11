import requests
import json
import os
import sqlite3
import time
import csv


import matplotlib
import matplotlib.pyplot as plt




#Project Members: SoJung Ham, Dylan Yono
#Information:  This program creates a database of stats of all Gen 1 Pokemon, which includes base speed, special defense, special attack
#               defense, attack, and HP. We will calculate the average base stats for typings of Pokemon (fire, water, grass).
                #example: Which Pokemon type has the highest attack stat on average?


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

    request_url = "https://pokeapi.co/api/v2/pokemon/?limit=151"

    
    dir_path = os.path.dirname(os.path.realpath(__file__))
    CACHE_FNAME = dir_path + '/' + "pokemon_cache.json"
    CACHE_DICTION  = read_cache(CACHE_FNAME)
    try:
        if request_url in CACHE_DICTION:
        
            print("Using pokemon cache")
            #add them to a dictionary, where key = request_url and value = results
            #uhhhhhhhhhhhhhhhhhhh
            
            
            #pull the last stored pokemon id from the database (max value in id)
            #increment id
            #repeat 20 times:
                #pull corresponding pokemone with id
                #increment id


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

#------------------- setting up table stuff ---------------------

def setUpPokemonBaseStatsTable(pokemon_data, cur, conn):
    
    cur.execute("DROP TABLE IF EXISTS PokemonStats")
    cur.execute('''CREATE TABLE PokemonStats (pokemon_id INTEGER PRIMARY KEY, pokemon_name TEXT,
                                        speed INTEGER, special_defense INTEGER, special_attack INTEGER, 
                                        defense INTEGER, attack INTEGER, hp INTEGER, type_1 INTEGER, type_2 INTEGER)''')
    info = pokemon_data.items()
    count = 0

    for pokemon in info:
         
        _pokemon_id = pokemon[1]['id']
        _pokemon_name = pokemon[1]['species']['name']
        #something here....list indices not string but its a dictionary..??
        _speed = pokemon[1]['stats'][0]['base_stat']
        _special_defense = pokemon[1]['stats'][1]['base_stat']
        _special_attack = pokemon[1]['stats'][2]['base_stat']
        _defense = pokemon[1]['stats'][3]['base_stat']  
        _attack = pokemon[1]['stats'][4]['base_stat'] 
        _hp = pokemon[1]['stats'][5]['base_stat'] 

        category = pokemon[1]['types']

        type1 = category[0]['type']['name']
        cur.execute("SELECT id FROM TypeCategories WHERE title = ? LIMIT 1", (type1, ))
        c = cur.fetchone()[0]
        _type_1 = c
        _type_2 = ""

        if len(category) == 2:
            type2 = category[1]['type']['name']
            cur.execute("SELECT id FROM TypeCategories WHERE title = ? LIMIT 1", (type2, ))
            d = cur.fetchone()[0]
            _type_2 = d



        cur.execute('INSERT INTO PokemonStats (pokemon_id, pokemon_name, speed, special_defense, special_attack, defense, attack, hp, type_1, type_2) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', 
                                                (_pokemon_id, _pokemon_name, _speed, _special_defense, _special_attack, _defense, _attack, _hp, _type_1, _type_2))
        count = count + 1
        conn.commit()

        if count % 10 == 0:
            print("Pausing for a bit....")
            time.sleep(1)

def setUpPokemonTypeTable(pokemon_data, cur, conn):

    cur.execute("DROP TABLE IF EXISTS PokemonTypes")
    cur.execute('''CREATE TABLE PokemonTypes (pokemon_id INTEGER PRIMARY KEY, 
                                        type_1 STRING, type_2 STRING)''')
    info = pokemon_data.items()#why isnT IT WORKING HERE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    for pokemon in info:
         
        _pokemon_id = pokemon[1]['id']
        _type_1 = pokemon[1]['types'][0]['type']['name']
        _type_2 = ""
        if len(pokemon[1]['types']) == 2:
            _type_2 = pokemon[1]['types'][1]['type']['name']

        cur.execute('INSERT INTO PokemonTypes (pokemon_id, type_1, type_2) VALUES(?, ?, ?)', (_pokemon_id, _type_1, _type_2))
    conn.commit()

def setUpTypeCategories(pokemon_data, cur, conn):
    
    cur.execute("DROP TABLE IF EXISTS TypeCategories")
    cur.execute("CREATE TABLE TypeCategories (id INTEGER PRIMARY KEY, title TEXT)")
    category_list = []
    info = pokemon_data.items()
    for pokemon in info:
        pokemon_type = pokemon[1]['types']
        for flavor in pokemon_type:
            if flavor['type']['name'] not in category_list:
                category_list.append(flavor['type']['name'])
    
    for i in range(len(category_list)):
        cur.execute("INSERT INTO TypeCategories (id,title) VALUES (?,?)",(i,category_list[i]))
    conn.commit()
    
#------------------ join tables ---------------------------------

#this is added A pokemon's type ID number to their respective stats. 
def getPokemonTypeAndStats(cur, conn):
    cur.execute('''SELECT PokemonStats.pokemon_name, PokemonTypes.type_1, PokemonTypes.type_2 FROM PokemonStats 
                INNER JOIN PokemonTypes ON PokemonStats.pokemon_id = PokemonTypes.pokemon_id''')
    lst = cur.fetchall()
    return lst

#----------------- average base stats calculations------------------------
def getAverageSpeedStats(pokemon_type, cur, conn):
    
    cur.execute("SELECT id FROM TypeCategories WHERE title =? LIMIT 1", (pokemon_type, ))
    type_id = cur.fetchall()[0][0]

    cur.execute("SELECT speed FROM PokemonStats WHERE type_1 =? OR type_2 =?", (type_id, type_id, ))

    average = 0
    total = 0
    resu = cur.fetchall()

    for pokemon in resu:
        total = pokemon[0] + total

    average = total / len(resu)

     
    return average

def getAverageSpecialDefenseStats(pokemon_type, cur, conn):
    
    cur.execute("SELECT id FROM TypeCategories WHERE title =? LIMIT 1", (pokemon_type, ))
    type_id = cur.fetchall()[0][0]

    cur.execute("SELECT special_defense FROM PokemonStats WHERE type_1 =? OR type_2 =?", (type_id, type_id,   ))

    average = 0
    total = 0
    resu = cur.fetchall()

    for pokemon in resu:
        total = pokemon[0] + total

    average = total / len(resu)

     
    return average

def getAverageSpecialAttackStats(pokemon_type, cur, conn):
    
    cur.execute("SELECT id FROM TypeCategories WHERE title =? LIMIT 1", (pokemon_type, ))
    type_id = cur.fetchall()[0][0]

    cur.execute("SELECT special_attack FROM PokemonStats WHERE type_1 =? OR type_2 =?", (type_id, type_id,   ))

    average = 0
    total = 0
    resu = cur.fetchall()

    for pokemon in resu:
        total = pokemon[0] + total

    average = total / len(resu)

     
    return average

def getAverageDefenseStats(pokemon_type, cur, conn):
    
    cur.execute("SELECT id FROM TypeCategories WHERE title =? LIMIT 1", (pokemon_type, ))
    type_id = cur.fetchall()[0][0]

    cur.execute("SELECT defense FROM PokemonStats WHERE type_1 =? OR type_2 =?", (type_id, type_id,   ))
    average = 0
    total = 0
    resu = cur.fetchall()

    for pokemon in resu:
        total = pokemon[0] + total

    average = total / len(resu)

     
    return average

def getAverageAttackStats(pokemon_type, cur, conn):
    
    cur.execute("SELECT id FROM TypeCategories WHERE title =? LIMIT 1", (pokemon_type, ))
    type_id = cur.fetchall()[0][0]

    cur.execute("SELECT attack FROM PokemonStats WHERE type_1 =? OR type_2 =?", (type_id, type_id,   ))
    average = 0
    total = 0
    resu = cur.fetchall()

    for pokemon in resu:
        total = pokemon[0] + total

    average = total / len(resu)

     
    return average

def getAverageHPStats(pokemon_type, cur, conn):
    
    # a = cur.execute("SELECT id FROM TypeCategories WHERE title >=?", (pokemon_type_name, ))
    # pokemon_type_id = a.value()

    cur.execute("SELECT id FROM TypeCategories WHERE title =? LIMIT 1", (pokemon_type, ))
    type_id = cur.fetchall()[0][0]

    cur.execute("SELECT hp FROM PokemonStats WHERE type_1 =? OR type_2 =?", (type_id, type_id,   ))

    average = 0
    total = 0
    resu = cur.fetchall()

    for pokemon in resu:
        total = pokemon[0] + total

    average = total / len(resu)

     
    return average


#----------------visualization-------------------------------------
#work in progress
def createAverageSpeedGraph():
    speedStats = {}
    pokemon_types = ['poison', 'grass', 'fire', 'flying', 'water', 'bug', 'normal', 'electric', 'ground', 'fairy', 'fighting', 'psychic',
            'rock', 'steel', 'ice', 'ghost', 'dragon']
    for _type in pokemon_types:
        speedStats[_type] = getAverageSpeedStats(_type, cur, conn)


    plt.bar(speedStats.keys(), speedStats.values(), color=['#c300c9', 
    '#33bf00', '#d10816', '#7acdde', '#0f2f91', '#7fff08', '#c9c9c9', '#fff200', '#3d2717', '#ff96dc', 
    '#66412b', '#640485', '#9c8972', '#9c9c9c', '#c2deff', '#240959', '#0007d1'], edgecolor = "gray")

    plt.ylabel('Points of Pokemon')
    plt.xlabel('Types')
    plt.title("Average Base Speed Stats v.s. Types of Pokemon")
    plt.show()

def createAverageSpecialDefenseGraph():
    specialDefenseStats = {}
    pokemon_types = ['poison', 'grass', 'fire', 'flying', 'water', 'bug', 'normal', 'electric', 'ground', 'fairy', 'fighting', 'psychic',
            'rock', 'steel', 'ice', 'ghost', 'dragon']
    for _type in pokemon_types:
        specialDefenseStats[_type] = getAverageSpecialDefenseStats(_type, cur, conn)


    plt.bar(specialDefenseStats.keys(), specialDefenseStats.values())

    plt.ylabel('Points of Pokemon')
    plt.xlabel('Types')
    plt.title("Average Base Special Defense Stats v.s. Types of Pokemon")
    plt.show()

def createAverageSpecialAttackGraph():
    specialAttackStats = {}
    pokemon_types = ['poison', 'grass', 'fire', 'flying', 'water', 'bug', 'normal', 'electric', 'ground', 'fairy', 'fighting', 'psychic',
            'rock', 'steel', 'ice', 'ghost', 'dragon']
    for _type in pokemon_types:
        specialAttackStats[_type] = getAverageSpecialAttackStats(_type, cur, conn)


    plt.bar(specialAttackStats.keys(), specialAttackStats.values())

    plt.ylabel('Points of Pokemon')
    plt.xlabel('Types')
    plt.title("Average Base Special Attack Stats v.s. Types of Pokemon")
    plt.show()

def createAverageDefenseGraph():
    defenseStats = {}
    pokemon_types = ['poison', 'grass', 'fire', 'flying', 'water', 'bug', 'normal', 'electric', 'ground', 'fairy', 'fighting', 'psychic',
            'rock', 'steel', 'ice', 'ghost', 'dragon']
    for _type in pokemon_types:
        defenseStats[_type] = getAverageDefenseStats(_type, cur, conn)


    plt.bar(defenseStats.keys(), defenseStats.values())

    plt.ylabel('Points of Pokemon')
    plt.xlabel('Types')
    plt.title("Average Base Defense Stats v.s. Types of Pokemon")
    plt.show()

def createAverageAttackGraph():
    attackStats = {}
    pokemon_types = ['poison', 'grass', 'fire', 'flying', 'water', 'bug', 'normal', 'electric', 'ground', 'fairy', 'fighting', 'psychic',
            'rock', 'steel', 'ice', 'ghost', 'dragon']
    for _type in pokemon_types:
        attackStats[_type] = getAverageAttackStats(_type, cur, conn)


    plt.bar(attackStats.keys(), attackStats.values())

    plt.ylabel('Points of Pokemon')
    plt.xlabel('Types')
    plt.title("Average Base Attack Stats v.s. Types of Pokemon")
    plt.show()

def createAverageHPGraph():
    HPStats = {}
    pokemon_types = ['poison', 'grass', 'fire', 'flying', 'water', 'bug', 'normal', 'electric', 'ground', 'fairy', 'fighting', 'psychic',
            'rock', 'steel', 'ice', 'ghost', 'dragon']
    for _type in pokemon_types:
        HPStats[_type] = getAverageHPStats(_type, cur, conn)


    plt.bar(HPStats.keys(), HPStats.values())

    plt.ylabel('Points of Pokemon')
    plt.xlabel('Types')
    plt.title("Average Base HP Stats v.s. Types of Pokemon")
    plt.show()

#-----  set up main area -----
pokemon_data = get_data_with_caching()
cur, conn = setUpDatabase('Pokemon.db')

setUpTypeCategories(pokemon_data, cur, conn)
setUpPokemonBaseStatsTable(pokemon_data, cur, conn)
setUpPokemonTypeTable(pokemon_data, cur, conn)

getPokemonTypeAndStats(cur, conn)

#----- program

print("Welcome to the pokemon base stat viewer. Here you can view average base stats of each pokemon typing. Quite insightful!")
print("This program utilizes pokeapi.com, and created for the purpose of SI 206 Fall 2019 semester final project.")
print("What kind of data would you like to view?")
print("----------")

print("(1) HP ")
print("(2) Attack ")
print("(3) Defense ")
print("(4) Special Attack ")
print("(5) Special Defense ")
print("(6) Speed ")

print("----------")

# userInput = input("Insert a number: ")

# if userInput == 1:
#     pass
# elif userInput ==2:
#     pass
# if userInput == 6:
#     print(createAverageSpeedGraph())
# createAverageSpeedGraph()

#-------------------csv stuff-------------------------------------

with open('pokemon_calc.csv', 'w', newline = '') as csvfile:

    fields = ['Pokemon Type', 'Average HP', 'Average Attack', 'Average Defense', 
            'Average Special Attack','Average Special Defense', 'Average Speed']

    csvwriter = csv.writer(csvfile)
    #WRITING THE HEADERS
    csvwriter.writerow(fields)






    cur.execute("SELECT title FROM TypeCategories")
    #adjsut this
    typeNames = []
    for x in cur:
        if x[0] not in typeNames:
            typeNames.append(str(x[0]))

    averageSpeeds = []
    for x in typeNames:
        speed = getAverageSpeedStats(x, cur, conn)
        averageSpeeds.append(speed)
    averageSpecialDefenses = []
    for x in typeNames:
        special_defense = getAverageSpecialDefenseStats(x, cur, conn)
        averageSpecialDefenses.append(special_defense)
    averageSpecialAttacks = []
    for x in typeNames:
        special_attack = getAverageSpecialAttackStats(x, cur, conn)
        averageSpecialAttacks.append(special_attack)
    averageDefenses = []
    for x in typeNames:
        defense = getAverageSpecialDefenseStats(x, cur, conn)
        averageDefenses.append(defense)
    averageAttacks = []
    for x in typeNames:
        attack = getAverageAttackStats(x, cur, conn)
        averageAttacks.append(attack)
    averageHps = []
    for x in typeNames:
        hp = getAverageHPStats(x, cur, conn)
        averageHps.append(hp)

    rows = zip(typeNames, averageSpeeds, averageSpecialDefenses, averageSpecialAttacks,
            averageDefenses, averageAttacks, averageHps)

    for x in rows:
        csvwriter.writerow(x)



conn.close()



