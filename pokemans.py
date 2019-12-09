import requests
import json
import os
import sqlite3

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
               
    except:
        print("error when reading from url")
        myDict = {}

    return myDict 
    
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
        
            print("Using cache")
            #add them to a dictionary, where key = request_url and value = results
            #uhhhhhhhhhhhhhhhhhhh
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
    info = pokemon_data.items()#why isnT IT WORKING HERE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

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
    conn.commit()

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

    cur.execute("SELECT speed FROM PokemonStats WHERE type_1 =? OR type_2 =?", (type_id, type_id,   ))

    average = 0
    total = 0
    resu = cur.fetchall()

    for pokemon in resu:
        total = pokemon[0] + total

    average = total / len(resu)

     
    return ("The average base speed stat for type " + pokemon_type + " is " + str(average))

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

     
    return ("The average base special defense stat for type " + pokemon_type + " is " + str(average))

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

     
    return ("The average base special attack stat for type " + str(pokemon_type) + " is " + str(average))

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

     
    return ("The average base defense for type " + pokemon_type + " is " + str(average))

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

     
    return ("The average base attack for type " + pokemon_type + " is " + str(average))

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

     
    return ("The average base hp for type " + str(pokemon_type)+ " is " + str(average))

#----------------visualization-------------------------------------
#work in progress
def createAverageSpeedGraph():
    speedStats = {}
    cur.execute('SELECT speed, type_1, type_2 FROM PokemonStats')

    for pokemon in cur:
        
        if len(pokemon) == 2:
            speedStats[pokemon[-1]] = pokemon[0] + speedStats.get(pokemon[-1], 0)

        if len(pokemon) > 2:
            speedStats[pokemon[-2]] = pokemon[0] + speedStats.get(pokemon[-2], 0)
            speedStats[pokemon[-1]] = pokemon[0] + speedStats.get(pokemon[-1], 0)

     #calculatiing averages
     # 

    cur.execute('SELECT type_1 FROM PokemonStats')
    resu = cur.fetchall()

    for pokemon_type in speedStats:
         

         speedStats[pokemon_type] = speedStats[pokemon_type] / len(resu)

    # plt.bar(speedStats.keys(), speedStats.values())

    # plt.ylabel('Points of Pokemon')
    # plt.xlabel('Types')
    # plt.title("Average Base Speed Stats v.s. Types of Pokemon")
    # plt.show()
    print(speedStats)



#----- testing area-----
pokemon_data = get_data_with_caching()
cur, conn = setUpDatabase('Pokemon.db')

setUpTypeCategories(pokemon_data, cur, conn)
setUpPokemonBaseStatsTable(pokemon_data, cur, conn)
setUpPokemonTypeTable(pokemon_data, cur, conn)

getPokemonTypeAndStats(cur, conn)

print(getAverageSpeedStats("fire", cur, conn))
print(getAverageSpecialDefenseStats("fire", cur, conn))
print(getAverageSpecialAttackStats("fire", cur, conn))
print(getAverageDefenseStats("fire", cur, conn))
print(getAverageAttackStats("fire", cur, conn))
print(getAverageHPStats("fire", cur, conn))

# createAverageSpeedGraph()
print("-------------------")
print(getAverageSpeedStats("water", cur, conn))
print(getAverageSpecialDefenseStats("water", cur, conn))
print(getAverageSpecialAttackStats("water", cur, conn))
print(getAverageDefenseStats("water", cur, conn))
print(getAverageAttackStats("water", cur, conn))
print(getAverageHPStats("water", cur, conn))
print("-------------------")
print(getAverageSpeedStats("grass", cur, conn))
print(getAverageSpecialDefenseStats("grass", cur, conn))
print(getAverageSpecialAttackStats("grass", cur, conn))
print(getAverageDefenseStats("grass", cur, conn))
print(getAverageAttackStats("grass", cur, conn))
print(getAverageHPStats("grass", cur, conn))
print("-------------------")
print(getAverageSpeedStats("normal", cur, conn))
print(getAverageSpecialDefenseStats("normal", cur, conn))
print(getAverageSpecialAttackStats("normal", cur, conn))
print(getAverageDefenseStats("normal", cur, conn))
print(getAverageAttackStats("normal", cur, conn))
print(getAverageHPStats("normal", cur, conn))






conn.close()



