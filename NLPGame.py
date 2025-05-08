import spacy
from collections import Counter
import random
import math
import re
import operator
import difflib
import copy

load_model = spacy.load('en_core_web_sm')

file = 'textGeneratorData.txt'
text = open(file, encoding = "utf8").read()
nlp = load_model(text)

list_of_tokens = [token for token in nlp]

list_of_tokens_strings = [token.text for token in nlp]
list_of_tokens_strings2 = []
m = -1
for n in range(0, len(list_of_tokens_strings) - 1):
    if list_of_tokens_strings[n] != '\n' and list_of_tokens_strings[n] != '\n\n':
        if list_of_tokens_strings[n] == ',' or list_of_tokens_strings[n].__contains__("'") or list_of_tokens_strings[n].__contains__("?") or list_of_tokens_strings[n].__contains__("!") or list_of_tokens_strings[n].__contains__(".") or list_of_tokens_strings[n] == '_' or list_of_tokens_strings[n].__contains__(":") or list_of_tokens_strings[n].__contains__(";"):
            list_of_tokens_strings2[m] = list_of_tokens_strings2[m] + list_of_tokens_strings[n]
        elif list_of_tokens_strings[n] == '-':
            list_of_tokens_strings2[m] = list_of_tokens_strings2[m] + list_of_tokens_strings[n] + list_of_tokens_strings[n+1]
        elif n == 0 or n > 0 and list_of_tokens_strings[n-1] != '-':
            list_of_tokens_strings2.append(list_of_tokens_strings[n])
            m = m + 1  
            
unigrams_dict = {}
for token in list_of_tokens_strings2:
    if token in unigrams_dict:
        unigrams_dict[token] = unigrams_dict.get(token) + 1
    else:
        unigrams_dict[token] = 1
        
bigrams_dict = {}

for n in range(0, len(list_of_tokens_strings2) - 1):
    current_bigram = list_of_tokens_strings2[n] + "|" + list_of_tokens_strings2[n+1]
    if current_bigram in bigrams_dict:
        bigrams_dict[current_bigram] = bigrams_dict.get(current_bigram) + 1
    else:
        bigrams_dict[current_bigram] = 1

trigrams_dict = {}

for n in range(0, len(list_of_tokens_strings2) - 2):
    current_trigram = list_of_tokens_strings2[n] + "|" + list_of_tokens_strings2[n+1] + "|" + list_of_tokens_strings2[n+2]
    if current_trigram in trigrams_dict:
        trigrams_dict[current_trigram] = trigrams_dict.get(current_trigram) + 1
    else:
        trigrams_dict[current_trigram] = 1

fourgrams_dict = {}

for n in range(0, len(list_of_tokens_strings2) - 3):
    current_fourgram = list_of_tokens_strings2[n] + "|" + list_of_tokens_strings2[n+1] + "|" + list_of_tokens_strings2[n+2] + "|" + list_of_tokens_strings2[n+3]
    if current_fourgram in fourgrams_dict:
        fourgrams_dict[current_fourgram] = fourgrams_dict.get(current_fourgram) + 1
    else:
        fourgrams_dict[current_fourgram] = 1
        
fivegrams_dict = {}

for n in range(0, len(list_of_tokens_strings2) - 4):
    current_fivegram = list_of_tokens_strings2[n] + "|" + list_of_tokens_strings2[n+1] + "|" + list_of_tokens_strings2[n+2] + "|" + list_of_tokens_strings2[n+3] + "|" + list_of_tokens_strings2[n+4]
    if current_fivegram in fivegrams_dict:
        fivegrams_dict[current_fivegram] = fivegrams_dict.get(current_fivegram) + 1
    else:
        fivegrams_dict[current_fivegram] = 1

sixgrams_dict = {}

for n in range(0, len(list_of_tokens_strings2) - 5):
    current_sixgram = list_of_tokens_strings2[n] + "|" + list_of_tokens_strings2[n+1] + "|" + list_of_tokens_strings2[n+2] + "|" + list_of_tokens_strings2[n+3] + "|" + list_of_tokens_strings2[n+4] + "|" + list_of_tokens_strings2[n+5]
    if current_sixgram in sixgrams_dict:
        sixgrams_dict[current_sixgram] = sixgrams_dict.get(current_sixgram) + 1
    else:
        sixgrams_dict[current_sixgram] = 1
        
N = len(list_of_tokens_strings2)
V = len(unigrams_dict)

class Player:
    def __init__(self):
        #(Name, Min Damage, Max Damage, Critical Chance, Critical Damage, Condition)
        self.weapon = Weapon("Sword", 10, 15, 0.4, 1.25)
        self.shield = None
        self.health = 250
        self.strength = 0
        self.maxHealth = 250
        self.inventory = []
        self.dodge = 0.25
        self.abilities = [Ability("stun", 1, 5, 0.75, 2, 0),
                          Ability("fireball", 30, 50, 0.4, 5, 0)]
        self.encounteredHealthPotion = False
        self.encounteredStrengthPotion = False
        
class Ability:
    def __init__(self, name, minDamage, maxDamage, chance, refreshRate, cooldown):
        self.name = name
        self.minDamage = minDamage
        self.maxDamage = maxDamage
        self.chance = chance
        self.refreshRate = refreshRate
        self.cooldown = cooldown

class Room:
    def __init__(self, walls, room=None):
        if room != None:
            self.type = room
        else:
            self.type = random.choice(['Empty', 'Chest', 'Monster'])
            
        self.description = self.generate_room_description()
        self.walls = walls
        self.contents = self.generate_contents()
        self.visited = False
        
        """
        walls in the maze are depicted by 4 binary units, 1111
        If a cell has a northern wall, 1000
        If a cell has a eastern wall, 0100
        If a cell has a southern wall, 0010
        If a cell has a western wall, 0001
        This means that if a cell is 12 = 1100,
        it has a northern and eastern wall
        max number is 15, meaning a boxed in cell
        """
        
    def generate_contents(self):
        if self.type == 'Empty':
            return None
        elif self.type == 'Chest':
            return Chest()
        elif self.type == 'Monster':
            return Monster()
        elif self.type == 'Start':
            return None
        elif self.type == 'End':
            return Monster()
        
    def generate_room_description(self):
        if self.type == 'Empty':
            return "This is an empty room. Nothing of interest here."
        elif self.type == 'Chest':
            return "This room contains a chest. It might be hiding something valuable."
        elif self.type == 'Monster':
            return "A fearsome monster lurks in the corner of this room!"
        elif self.type == 'Start':
            return "The room where you start in"
        elif self.type == 'End':
            return "The room where you exit from"
        
    def wall(self, direction):
        if direction == "n" and self.walls >= 8:
            return True
        elif direction == "e" and 3 < self.walls % 8:
            return True
        elif direction == "s" and 1 < self.walls % 4:
            return True
        elif direction == "w" and self.walls % 2 == 1:
            return True
        
        return False


class Chest:
    def __init__(self, items=None):
        if items == None:
            self.items = []
        else:
            self.items = items
        

class Monster:
    def __init__(self,mType=None,weapon=None,armor=None,health=None, dodge=None):
        self.mType = mType
        #(Name, Damage, Critical, Condition)
        self.weapon = weapon
        self.armor = armor
        self.health = health
        self.dodge = dodge
        self.isStuned = False
        
class Weapon:
    def __init__(self,name=None,minDamage=None,maxDamage=None,criticalChance=None,critical=None):
        self.name = name
        self.minDamage = minDamage
        self.maxDamage = maxDamage
        self.criticalChance = criticalChance
        self.critical = critical
        
        
class Potion:
    def __init__(self, potion_type, power):
        self.type = potion_type
        self.power = power 
        
    def use(self, player):
        if self.type == "Health":
            player.health = min(player.maxHealth, player.health + self.power)
        elif self.type == "Strength":
            player.strength += self.power

class Game:
    def __init__(self):
        self.running = True
        self.dungeon = self.generate_dungeon()
        self.currentRoom = (0,0)
        self.lastRoom = None
        self.player = Player()
        self.state = "Start"        
        self.dungeonCopy = copy.deepcopy(self.dungeon)
        self.difficulty = "Normal"
        
        # Actions (verbs)
        self.actions = { "move", "go", "head", "navigate", "advance", "take", "enter",
                        "traverse", "proceed", "step", "walk", "venture", "progress",
                        "veer", "approach", "look", "check", "view", "inspect", "study",
                        "examine", "consult", "browse", "glance", "scan", "observe",
                        "survey", "gaze", "peek", "behold", "glimpse", "eye", "show",
                        "display", "open", "unseal", "pop", "access", "uncover", "reveal", "unveil",
                        "glimpse", "search", "rifle", "dig", "investigate", "explore", "audit",
                        "use", "take", "apply", "activate", "employ", "cast", "utilize",
                        "drink", "consume", "swallow", "guzzle", "down", "imbibe", "ingest", "chug",
                        "attack", "strike", "cut", "damage", "swing", "slash", "slice", "unleash", "hit", "fight",
                        "run", "escape", "retreat", "flee", "dash", "withdraw",
                        "stun", "daze", "hinder", "stagger",
                        "conjure", "summon", "channel", "deploy", "fire", "launch", "release", "unleash", "throw"
        }
        
        # Prepositions that often indicate PRSI
        self.prepositions = { "with", "using", "at", "in", "on", "into", "onto", "from",
                             "to", "towards", "through", "across", "under", "over", "by",
                             "near", "beside", "behind", "around", "past", "within",
                             "inside", "outside", "off", "above", "below", "beneath",
                             "against", "between", "among", "along", "beyond", "before",
                             "after"
        }
        
        self.adjectives = { "up", "upper", "upward", "north", "northern", "down",
                           "lower", "downward", "south", "southern", "left",
                           "leftward", "west", "western", "right", "rightward",
                           "east", "eastern", "next", "adjacent", "following",
                           "neighboring", "ahead", "upcoming", "subsequent",
                           "succeeding", "other", "ensuing", "imminent",
                           "forthcoming", "approaching", "adjoining", "forward",
                           "health", "healing", "restorative", "recovery", "cure", "rejuvenation", "herbal", "renewal",
                           "strength", "might", "power", "brawn", "force", "muscle"
        }
        
        # Objects
        self.objects = { "room", "area", "space", "zone", "region", "section", "chamber",
                        "place", "spot", "location", "sector", 
                        "door", "exit", "entrance", "passage", "threshold", "opening", "doorway", "corridor", "entryway", "gateway", "entranceway",
                        "map", "chart", "layout", "diagram", "guide", "grid", "dungeon", "terrain",
                        "atlas", "scroll", "parchment", "pathfinder", "schematic",
                        "overlay", "chest", "box", "crate", "container", "case", "stash", "strongbox",
                                  "cache", "trove",
                        "potion", "item", "flask", "vial", "tonic", "brew", "tincture", "essence", "elixir",
                        "sword", "blade", "steel", "brand",
                        "monster", "beast", "creature", "abomination", "terror", "aberration", "monstrosity", "warbeast",
                        "enemy", "fiend", "brute", "foe", "adversary", "threat", "assailant", "opponent", "challenger",
                        "inventory", "equipment", "content", "bag", "belongings", "pouch",
                        "fireball"
        }
        
        self.dictionary = {
                "move": ["movement"],
                "go": ["movement"],
                "head": ["movement"],
                "navigate": ["movement"],
                "advance": ["movement"],
                "take": ["movement"],
                "enter": ["movement"],
                "traverse": ["movement"],
                "proceed": ["movement"],
                "step": ["movement"],
                "walk": ["movement"],
                "venture": ["movement"],
                "progress": ["movement"],
                "veer": ["movement"],
                "approach": ["movement"],
                
                "direction": ["up", "down", "left", "right"],
                
                "up": ["up"],
                "upper": ["up"],
                "upward": ["up"],
                "north": ["up"],
                "northern": ["up"],
    
                "down": ["down", "drink"],
                "lower": ["down"],
                "downward": ["down"],
                "south": ["down"],
                "southern": ["down"],

                "left": ["left"],
                "leftward": ["left"],
                "west": ["left"],
                "western": ["left"],
        
                "right": ["right"],
                "rightward": ["right"],
                "east": ["right"],
                "eastern": ["right"],
                
                "room": ["room"],
                "area": ["room"],
                "space": ["room"],
                "zone": ["room"],
                "region": ["room"],
                "section": ["room"],
                "chamber": ["room"],
                "place": ["room"],
                "spot": ["room"],
                "location": ["room"],
                "sector": ["room"],
                
                "door": ["door"],
                "exit": ["door"],
                "entrance": ["door"],
                "passage": ["door"],
                "threshold": ["door"],
                "opening": ["door"],
                "doorway": ["door"],
                "corridor": ["door"],
                "entryway": ["door"],
                "gateway": ["door"],
                "entranceway": ["door"],
                
                "next": ["next"],
                "adjacent": ["next"],
                "following": ["next"],
                "neighboring": ["next"],
                "ahead": ["next"],
                "upcoming": ["next"],
                "subsequent": ["next"],
                "succeeding": ["next"],
                "other": ["next"],
                "ensuing": ["next"],
                "imminent": ["next"],
                "forthcoming": ["next"],
                "approaching": ["next"],
                "adjoining": ["next"],
                "forward": ["next"],
                
                "look": ["look", "show"],
                "check": ["look", "show"],
                "view": ["look", "show"],
                "inspect": ["look"],
                "study": ["look"],
                "examine": ["look", "show"],
                "consult": ["look"],
                "browse": ["look"],
                "glance": ["look"],
                "scan": ["look"],
                "observe": ["look"],
                "survey": ["look"],
                "gaze": ["look"],
                "peek": ["look"],
                "behold": ["look"],
                "glimpse": ["look", "open"],
                "eye": ["look"],
                "show": ["look", "show"],
                "display": ["look", "show"],
                
                "map": ["map"],
                "chart": ["map"],
                "layout": ["map"],
                "diagram": ["map"],
                "guide": ["map"],
                "grid": ["map"],
                "dungeon": ["map"],
                "terrain": ["map"],
                "atlas": ["map"],
                "scroll": ["map"],
                "parchment": ["map"],
                "pathfinder": ["map"],
                "schematic": ["map"],
                "overlay": ["map"],
                
                "open": ["open"],
                "unseal": ["open"],
                "pop": ["open"],
                "access": ["open"],
                "uncover": ["open"],
                "reveal": ["open"],
                "unveil": ["open"],
                "search": ["open"],
                "rifle": ["open"],
                "dig": ["open"],
                "investigate": ["open"],
                "explore": ["open"],
                "audit": ["open"],
                
                "chest": ["chest"],
                "box": ["chest"],
                "crate": ["chest"],
                "container": ["chest"],
                "case": ["chest"],
                "stash": ["chest"],
                "strongbox": ["chest"],
                "cache": ["chest"],
                "trove": ["chest"],
                
                "use": ["use"],
                "take": ["use"],
                "apply": ["use"],
                "employ": ["use"],
                "utilize": ["use"],
                
                "drink": ["drink"],
                "consume": ["drink"],
                "swallow": ["drink"],
                "guzzle": ["drink"],
                "imbibe": ["drink"],
                "ingest": ["drink"],
                "chug": ["drink"],
                
                "health": ["health", "healing"],
                "healing": ["healing"],
                "restorative": ["healing"],
                "recovery": ["healing"],
                "cure": ["healing"],
                "rejuvenation": ["healing"],
                "herbal": ["healing"],
                "renewal": ["healing"],

                "strength": ["strength"],
                "might": ["strength"],
                "power": ["strength"],
                "brawn": ["strength"],
                "force": ["strength"],
                "muscle": ["strength"],

                "potion": ["potion"],
                "item": ["potion", "inventory"],
                "flask": ["potion"],
                "vial": ["potion"],
                "tonic": ["potion"],
                "brew": ["potion"],
                "tincture": ["potion"],
                "essence": ["potion"],
                "elixir": ["potion"],
                
                "attack": ["attack"],
                "strike": ["attack"],
                "cut": ["attack"],
                "damage": ["attack"],
                "swing": ["attack"],
                "slash": ["attack"],
                "slice": ["attack"],
                "unleash": ["attack"],
                "hit": ["attack"],
                "fight": ["attack"],
                
                "weapon": ["sword"],
                
                "sword": ["weapon"],
                "blade": ["weapon"],
                "steel": ["weapon"],
                "brand": ["weapon"],

                "run": ["run"],
                "escape": ["run"],
                "retreat": ["run"],
                "flee": ["run"],
                "dash": ["run"],
                "withdraw": ["run"],
                
                "monster": ["monster"],
                "beast": ["monster"],
                "creature": ["monster"],
                "abomination": ["monster"],
                "terror": ["monster"],
                "aberration": ["monster"],
                "monstrosity": ["monster"],
                "warbeast": ["monster"],
                
                "enemy": ["enemy"],
                "fiend": ["enemy"],
                "brute": ["enemy"],
                "foe": ["enemy"],
                "adversary": ["enemy"],
                "threat": ["enemy"],
                "assailant": ["enemy"],
                "opponent": ["enemy"],
                "challenger": ["enemy"],
                
                "inventory": ["inventory"],
                "equipment": ["inventory"],
                "content": ["inventory"],
                "bag": ["inventory"],
                "belongings": ["inventory"],
                "pouch": ["inventory"],
                
                "stun": ["stun"],
                "daze": ["stun"],
                "hinder": ["stun"],
                "stagger": ["stun"],
                
                "cast": ["cast"],
                "activate": ["cast"],
                "conjure": ["cast"],
                "summon": ["cast"],
                "channel": ["cast"],
                "deploy": ["cast"],
                "fire": ["cast"],
                "launch": ["cast"],
                "release": ["cast"],
                "unleash": ["cast"],
                "throw": ["cast"],
                
                "fireball": ["fireball"]
            }

        # trigrams with start_word as parameter
    def sentence_gen3(self, unigrams, bigrams, trigrams, N, V, start_word):
   
        first_word = start_word
        sentence = ""
          
        # second word
    
        sorted_bigrams = sorted(bigrams, key = bigrams.get, reverse = True)
    
        previous_word = first_word
    
        new_word = ""
    
        most_common_bigrams = []
        
        for i in range(0, len(sorted_bigrams)):
            if bool(re.search(f"{previous_word}\|", sorted_bigrams[i])):
                most_common_bigrams.append(sorted_bigrams[i])
            
        if(len(most_common_bigrams) > 0):
            k = random.randint(0, len(most_common_bigrams) - 1)
            new_word = most_common_bigrams[k].split("|")[1]
            sentence = sentence + new_word
        else:
            k = random.randint(0, len(sorted_bigrams) - 1)
            new_word = sorted_bigrams[k].split("|")[1]
            sentence = sentence + new_word
        
        previous_word2 = new_word
      
        # later words
    
        sorted_trigrams = sorted(trigrams, key = trigrams.get, reverse = True)
    
        while not new_word.__contains__("."):
            most_common_trigrams = []
        
            for i in range(0, len(sorted_trigrams)):
                if bool(re.search(f"{previous_word}\|{previous_word2}\|", sorted_trigrams[i])):
                    most_common_trigrams.append(sorted_trigrams[i])
            
            if(len(most_common_trigrams) > 0):
                k = random.randint(0, len(most_common_trigrams) - 1)
                new_word = most_common_trigrams[k].split("|")[2]
                sentence = sentence + " " + new_word
            else:
                k = random.randint(0, len(sorted_trigrams) - 1)
                new_word = sorted_trigrams[k].split("|")[2]
                sentence = sentence + " " + new_word
        
            previous_word = previous_word2
            previous_word2 = new_word
    
        return sentence
    
    # fourgrams with start word
    def sentence_gen_four(self, unigrams, bigrams, trigrams, fourgrams, N, V, start_word, punctuation_mark, punctuation_limit):
        #first word
        first_word = start_word
        sentence = ""
            
        # second word
    
        sorted_bigrams = sorted(bigrams, key = bigrams.get, reverse = True)
    
        previous_word = first_word
    
        new_word = ""
    
        most_common_bigrams = []
        
        for i in range(0, len(sorted_bigrams)):
            if bool(re.search(f"{previous_word}\|", sorted_bigrams[i])):
                most_common_bigrams.append(sorted_bigrams[i])
            
        if(len(most_common_bigrams) > 0):
            k = random.randint(0, len(most_common_bigrams) - 1)
            new_word = most_common_bigrams[k].split("|")[1]
            sentence = sentence + new_word
        else:
            k = random.randint(0, len(sorted_bigrams) - 1)
            new_word = sorted_bigrams[k].split("|")[1]
            sentence = sentence + new_word
        
        previous_word2 = new_word
    
        # third word
    
        sorted_trigrams = sorted(trigrams, key = trigrams.get, reverse = True)
    
        new_word = ""
    
        most_common_trigrams = []
    
        for i in range(0, len(sorted_trigrams)):
            if bool(re.search(f"{previous_word}\|{previous_word2}\|", sorted_trigrams[i])):
                most_common_trigrams.append(sorted_trigrams[i])
    
        if(len(most_common_trigrams) > 0):
            k = random.randint(0, len(most_common_trigrams) - 1)
            new_word = most_common_trigrams[k].split("|")[2]
            sentence = sentence + " " + new_word
        else:
            k = random.randint(0, len(sorted_trigrams) - 1)
            new_word = sorted_trigrams[k].split("|")[2]
            sentence = sentence + " " + new_word
    
        previous_word3 = new_word
    
        # later words
    
        punctuation_count = 0
    
        sorted_fourgrams = sorted(fourgrams, key = fourgrams.get, reverse = True)
    
        while punctuation_count < punctuation_limit:
            most_common_fourgrams = []
        
            for i in range(0, len(sorted_fourgrams)):
                if bool(re.search(f"{previous_word}\|{previous_word2}\|{previous_word3}\|", sorted_fourgrams[i])):
                    most_common_fourgrams.append(sorted_fourgrams[i])
            
            if(len(most_common_fourgrams) > 0):
                k = random.randint(0, len(most_common_fourgrams) - 1)
                new_word = most_common_fourgrams[k].split("|")[3]
                sentence = sentence + " " + new_word
                if new_word.__contains__(punctuation_mark):
                    punctuation_count = punctuation_count + 1
            else:
                k = random.randint(0, len(sorted_fourgrams) - 1)
                new_word = sorted_fourgrams[k].split("|")[3]
                sentence = sentence + " " + new_word
                if new_word.__contains__(punctuation_mark):
                    punctuation_count = punctuation_count + 1
        
            previous_word = previous_word2
            previous_word2 = previous_word3
            previous_word3 = new_word
    
        return sentence
    
    # fivegrams with start word as parameter
    def sentence_gen_five(self, unigrams, bigrams, trigrams, fourgrams, fivegrams, N, V, start_word, punctuation_mark, punctuation_limit):
    
        first_word = start_word
        sentence = ""
            
        # second word
    
        sorted_bigrams = sorted(bigrams, key = bigrams.get, reverse = True)
    
        previous_word = first_word
    
        new_word = ""
    
        most_common_bigrams = []
        
        for i in range(0, len(sorted_bigrams)):
            if bool(re.search(f"{previous_word}\|", sorted_bigrams[i])):
                most_common_bigrams.append(sorted_bigrams[i])
            
        if(len(most_common_bigrams) > 0):
            k = random.randint(0, len(most_common_bigrams) - 1)
            new_word = most_common_bigrams[k].split("|")[1]
            sentence = sentence + new_word
        else:
            k = random.randint(0, len(sorted_bigrams) - 1)
            new_word = sorted_bigrams[k].split("|")[1]
            sentence = sentence + new_word
        
        previous_word2 = new_word
    
        # third word
    
        sorted_trigrams = sorted(trigrams, key = trigrams.get, reverse = True)
    
        new_word = ""
    
        most_common_trigrams = []
    
        for i in range(0, len(sorted_trigrams)):
            if bool(re.search(f"{previous_word}\|{previous_word2}\|", sorted_trigrams[i])):
                most_common_trigrams.append(sorted_trigrams[i])
    
        if(len(most_common_trigrams) > 0):
            k = random.randint(0, len(most_common_trigrams) - 1)
            new_word = most_common_trigrams[k].split("|")[2]
            sentence = sentence + " " + new_word
        else:
            k = random.randint(0, len(sorted_trigrams) - 1)
            new_word = sorted_trigrams[k].split("|")[2]
            sentence = sentence + " " + new_word
    
        previous_word3 = new_word
    
        # fourth word
        sorted_fourgrams = sorted(fourgrams, key = fourgrams.get, reverse = True)
    
        new_word = ""
    
        most_common_fourgrams = []
        
        for i in range(0, len(sorted_fourgrams)):
            if bool(re.search(f"{previous_word}\|{previous_word2}\|{previous_word3}\|", sorted_fourgrams[i])):
                most_common_fourgrams.append(sorted_fourgrams[i])
            
        if(len(most_common_fourgrams) > 0):
            k = random.randint(0, len(most_common_fourgrams) - 1)
            new_word = most_common_fourgrams[k].split("|")[3]
            sentence = sentence + " " + new_word
        else:
            k = random.randint(0, len(sorted_fourgrams) - 1)
            new_word = sorted_fourgrams[k].split("|")[3]
            sentence = sentence + " " + new_word
        
        previous_word4 = new_word  
    
        # later words
    
        sorted_fivegrams = sorted(fivegrams, key = fivegrams.get, reverse = True)
    
        punctuation_count = 0
    
        while punctuation_count < punctuation_limit:
            most_common_fivegrams = []
        
            for i in range(0, len(sorted_fivegrams)):
                if bool(re.search(f"{previous_word}\|{previous_word2}\|{previous_word3}\|{previous_word4}\|", sorted_fivegrams[i])):
                    most_common_fivegrams.append(sorted_fivegrams[i])
            
            if(len(most_common_fivegrams) > 0):
                k = random.randint(0, len(most_common_fivegrams) - 1)
                new_word = most_common_fivegrams[k].split("|")[4]
                sentence = sentence + " " + new_word
                if new_word.__contains__(punctuation_mark):
                    punctuation_count = punctuation_count + 1
            else:
                k = random.randint(0, len(sorted_fivegrams) - 1)
                new_word = sorted_fivegrams[k].split("|")[4]
                sentence = sentence + " " + new_word
                if new_word.__contains__(punctuation_mark):
                    punctuation_count = punctuation_count + 1
        
            previous_word = previous_word2
            previous_word2 = previous_word3
            previous_word3 = previous_word4
            previous_word4 = new_word
    
        return sentence
    
    # sixgrams with start word as parameter
    def sentence_gen_six(self, unigrams, bigrams, trigrams, fourgrams, fivegrams, sixgrams, N, V, start_word, punctuation_mark, punctuation_limit):
    
        first_word = start_word
        sentence = ""
            
        # second word
    
        sorted_bigrams = sorted(bigrams, key = bigrams.get, reverse = True)
    
        previous_word = first_word
    
        new_word = ""
    
        most_common_bigrams = []
        
        for i in range(0, len(sorted_bigrams)):
            if bool(re.search(f"{previous_word}\|", sorted_bigrams[i])):
                most_common_bigrams.append(sorted_bigrams[i])
            
        if(len(most_common_bigrams) > 0):
            k = random.randint(0, len(most_common_bigrams) - 1)
            new_word = most_common_bigrams[k].split("|")[1]
            sentence = sentence + new_word
        else:
            k = random.randint(0, len(sorted_bigrams) - 1)
            new_word = sorted_bigrams[k].split("|")[1]
            sentence = sentence + new_word
        
        previous_word2 = new_word
    
        # third word
    
        sorted_trigrams = sorted(trigrams, key = trigrams.get, reverse = True)
    
        new_word = ""
    
        most_common_trigrams = []
    
        for i in range(0, len(sorted_trigrams)):
            if bool(re.search(f"{previous_word}\|{previous_word2}\|", sorted_trigrams[i])):
                most_common_trigrams.append(sorted_trigrams[i])
    
        if(len(most_common_trigrams) > 0):
            k = random.randint(0, len(most_common_trigrams) - 1)
            new_word = most_common_trigrams[k].split("|")[2]
            sentence = sentence + " " + new_word
        else:
            k = random.randint(0, len(sorted_trigrams) - 1)
            new_word = sorted_trigrams[k].split("|")[2]
            sentence = sentence + " " + new_word
    
        previous_word3 = new_word
    
        # fourth word
        sorted_fourgrams = sorted(fourgrams, key = fourgrams.get, reverse = True)
    
        new_word = ""
    
        most_common_fourgrams = []
        
        for i in range(0, len(sorted_fourgrams)):
            if bool(re.search(f"{previous_word}\|{previous_word2}\|{previous_word3}\|", sorted_fourgrams[i])):
                most_common_fourgrams.append(sorted_fourgrams[i])
            
        if(len(most_common_fourgrams) > 0):
            k = random.randint(0, len(most_common_fourgrams) - 1)
            new_word = most_common_fourgrams[k].split("|")[3]
            sentence = sentence + " " + new_word
        else:
            k = random.randint(0, len(sorted_fourgrams) - 1)
            new_word = sorted_fourgrams[k].split("|")[3]
            sentence = sentence + " " + new_word
        
        previous_word4 = new_word  
    
        # fifth word
    
        sorted_fivegrams = sorted(fivegrams, key = fivegrams.get, reverse = True)
    
        punctuation_count = 0
       
        most_common_fivegrams = []
        
        for i in range(0, len(sorted_fivegrams)):
            if bool(re.search(f"{previous_word}\|{previous_word2}\|{previous_word3}\|{previous_word4}\|", sorted_fivegrams[i])):
                most_common_fivegrams.append(sorted_fivegrams[i])
            
        if(len(most_common_fivegrams) > 0):
            k = random.randint(0, len(most_common_fivegrams) - 1)
            new_word = most_common_fivegrams[k].split("|")[4]
            sentence = sentence + " " + new_word
        else:
            k = random.randint(0, len(sorted_fivegrams) - 1)
            new_word = sorted_fivegrams[k].split("|")[4]
            sentence = sentence + " " + new_word
    
        if new_word.__contains__(punctuation_mark):
            punctuation_count = punctuation_count + 1
    
        previous_word5 = new_word
    
        # later words
    
        sorted_sixgrams = sorted(sixgrams, key = sixgrams.get, reverse = True)
            
        while punctuation_count < punctuation_limit:
            most_common_sixgrams = []
        
            for i in range(0, len(sorted_sixgrams)):
                if bool(re.search(f"{previous_word}\|{previous_word2}\|{previous_word3}\|{previous_word4}\|{previous_word5}\|", sorted_sixgrams[i])):
                    most_common_sixgrams.append(sorted_sixgrams[i])
            
            if(len(most_common_sixgrams) > 0):
                k = random.randint(0, len(most_common_sixgrams) - 1)
                new_word = most_common_sixgrams[k].split("|")[5]
                sentence = sentence + " " + new_word
                if new_word.__contains__(punctuation_mark):
                    punctuation_count = punctuation_count + 1
            else:
                k = random.randint(0, len(sorted_sixgrams) - 1)
                new_word = sorted_sixgrams[k].split("|")[5]
                sentence = sentence + " " + new_word
                if new_word.__contains__(punctuation_mark):
                    punctuation_count = punctuation_count + 1
        
            previous_word = previous_word2
            previous_word2 = previous_word3
            previous_word3 = previous_word4
            previous_word4 = previous_word5
            previous_word5 = new_word
    
        return sentence
    
    def generate_dungeon(self):
        
        matrix = [
                [Room(9,'Start'), Room(12,'Monster'), Room(9,'Monster'), Room(12,'Chest'), Room(13,'Chest')],
                [Room(5,'Monster'), Room(3,'Chest'), Room(4,'Empty'), Room(5,'Empty'), Room(5,'Monster')],
                [Room(3,'Empty'), Room(10,'Empty'), Room(4,'Empty'), Room(5,'Empty'), Room(5,'Empty')],
                [Room(9,'Empty'), Room(8,'Empty'), Room(6,'Monster'), Room(1,'Monster'), Room(6,'Empty')],
                [Room(7,'Chest'), Room(7,'Chest'), Room(11,'Monster'), Room(2,'Empty'), Room(14,'End')]
            ]
        
        matrix[0][0].visited = True;
               
        #Monsters
        matrix[0][1].contents = Monster("Greenbottleman", Weapon("Fists", 6, 10, 0.25, 1.15), None, 50, 0.2)
        matrix[1][0].contents = Monster("Penguin Zombie", Weapon("Claws", 9, 13, 0.3, 1.15), None, 70, 0.25)
        matrix[3][2].contents = Monster("Fiend of Insatiable Greed", Weapon("Sword", 10, 15, 0.4, 1.25), None, 80, 0.25)
        matrix[0][2].contents = Monster("Troll", Weapon("Axe", 7, 18, 0.4, 1.5), None, 85, 0.25)
        matrix[3][3].contents = Monster("Demon", Weapon("Spear", 13, 20, 0.45, 1.4), None, 90, 0.35)
        matrix[1][4].contents = Monster("Martenoid Guard", Weapon("Long Sword", 15, 20, 0.45, 1.45), None, 100, 0.4)
        matrix[4][2].contents = Monster("Skeletal Giant", Weapon("Mace", 11, 14, 0.5, 1.2), None, 70, 0.5)
        matrix[4][4].contents = Monster("Boss Warbeast", Weapon("Steel Sword", 20, 30, 0.55, 1.5), None, 170, 0.4)
            
        #Chests
        matrix[1][1].contents = Chest([Potion("Health", 100)])
        matrix[4][0].contents = Chest([Weapon("Long Sword", 10, 20, 0.45, 1.25)])
        matrix[4][1].contents = Chest([Potion("Health", 100)])
        matrix[0][3].contents = Chest([Potion("Strength", 7)])
        matrix[0][4].contents = Chest([Weapon("Steel Sword", 15, 25, 0.55, 1.5), Potion("Health", 100)])
        
        """
        matrix = [[0] * 5 for _ in range(5)]
        
        for i in range(len(matrix)):
            for j in range(len(matrix[i])):
                if i == 0 and j == 0:
                    matrix[i][j] = Room('Start')
                elif i == 4 and j == 4:
                    matrix[i][j] = Room('End')
                else:
                    matrix[i][j] = Room()
        """
        
        return matrix
    
    def hard_mode_changes(self):
        self.dungeon[0][1].contents.health = 60
        self.dungeon[1][0].contents.health = 80
        self.dungeon[3][2].contents.health = 90
        self.dungeon[0][2].contents.health = 95
        self.dungeon[3][3].contents.health = 100
        self.dungeon[1][4].contents.health = 110
        self.dungeon[4][2].contents.health = 80
        self.dungeon[4][4].contents.health = 220
    
    def generate_map(self):        
        generated_sentence = self.sentence_gen3(unigrams_dict, bigrams_dict, trigrams_dict, N, V, 'MAP')
        print(generated_sentence)
        print("\n")
        #print("Traveled Map:")
        mapString = ""
        
        def inside(room):
            stuff = " "
            x,y = self.currentRoom
            if self.dungeon[x][y] == room:
                stuff = "P"
            elif room.visited:
                if room.type == "Empty" or room.type == "Start" or room.type == "End":
                    stuff = " "
                elif room.type == "Monster":
                    if room.contents != None:
                        stuff = "M"
                    else:
                        stuff = " "
                elif room.type == "Chest":
                    if room.contents.items:
                        stuff = "C"
                    else:
                        stuff = " "
            
            return stuff
        
        
        for i in range(len(self.dungeon)):
            # Top part of the maze
            for j in range(len(self.dungeon[0])):
                if i == 0:
                    if self.dungeon[i][j].visited:
                        mapString += "+---"
                        #print("+---", end="")
                    elif self.dungeon[i][j-1].visited and not self.dungeon[i][j].visited:
                        mapString += "+   "
                        #print("+   ", end="")
                    else:
                        mapString += "    "
                        #print("    ", end="")
                elif j == 0:
                    if self.dungeon[i][j].visited or self.dungeon[i-1][j].visited:
                        if self.dungeon[i][j].wall("n") and self.dungeon[i-1][j].wall("s"):
                            # Wall detected
                            mapString += "+---"
                            #print("+---", end="")
                        else:
                            # No wall detected
                            mapString += "+   "
                            #print("+   ", end="")
                    else:
                        mapString += "    "
                        #print("    ", end="")
                else:
                    if self.dungeon[i][j].visited or self.dungeon[i-1][j].visited:
                        if self.dungeon[i][j].wall("n") and self.dungeon[i-1][j].wall("s"):
                            # Wall detected
                            mapString += "+---"
                            #print("+---", end="")
                        else:
                            # No wall detected
                            mapString += "+   "
                            #print("+   ", end="")
                    elif (self.dungeon[i][j-1].visited and not self.dungeon[i][j].visited) or (self.dungeon[i-1][j-1].visited and not self.dungeon[i-1][j].visited):
                        mapString += "+   "
                        #print("+   ", end="")
                    else:
                        mapString += "    "
                        #print("    ", end="")
            if self.dungeon[i][len(self.dungeon[0])-1].visited:
                mapString += "+\n"
                #print("+")  # Close the top row of the current row
            else:
                mapString = mapString.rstrip() + "\n"
                #mapString += " \n"
                #print(" ")
                
            # Side walls
            for j in range(len(self.dungeon[0])):
                if j == 0:
                    if self.dungeon[i][j].visited:
                        mapString += "| " + inside(self.dungeon[i][j]) + " "
                        #print("| ", end="")
                        #print(inside(self.dungeon[i][j]), end="")
                        #print(" ", end="")
                    else:
                        mapString += "    "
                        #print("    ", end="")
                else:
                    if self.dungeon[i][j].visited or self.dungeon[i][j-1].visited:
                        if self.dungeon[i][j].wall("w") and self.dungeon[i][j-1].wall("e"):
                            mapString += "| " + inside(self.dungeon[i][j]) + " "
                            #print("| ", end="")
                            #print(inside(self.dungeon[i][j]), end="")
                            #print(" ", end="")
                        else:
                            mapString += "  " + inside(self.dungeon[i][j]) + " "
                            #print("  ", end="")
                            #print(inside(self.dungeon[i][j]), end="")
                            #print(" ", end="")
                    else:
                        mapString += "    "
                        #print("    ", end="")
                        
            if self.dungeon[i][len(self.dungeon[0])-1].visited:
                mapString += "|\n"
                #print("|")  # Close the right part of the maze
            else:
                mapString = mapString.rstrip() + "\n"
                #print(" ") # Newline after printing the row
                
        # Bottom part of the maze
        for j in range(len(self.dungeon[0])):
            if j == 0:
                if self.dungeon[len(self.dungeon)-1][j].visited:
                    mapString += "+---"
                    #print("+---", end="")
                else:
                    mapString += "    "
                    #print("    ", end="")
            else:
                if self.dungeon[i][j].visited:
                    mapString += "+---"
                    #print("+---", end="")
                elif self.dungeon[i][j-1].visited:
                    mapString += "+   "
                    #print("+   ", end="")
                else:
                    mapString += "    "
                    #print("    ", end="")
                    
        if self.dungeon[len(self.dungeon)-1][len(self.dungeon[0])-1].visited:
            # Leave the bottom part of the maze closed
            mapString += "+\n"
            #print("+")
        else:
            mapString = mapString.rstrip() + "\n"
            #print(" ")
            
        #print()
        print(mapString)
    
        generated_sentence = self.sentence_gen_five(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, N, V, 'MAP2', '?', 1)
        print(generated_sentence)
    
    def moving(self, direction, word):
        x = self.currentRoom[0]
        y = self.currentRoom[1]
        
        maxX = len(self.dungeon)-1
        maxY = len(self.dungeon[x])-1
        
        visitedBefore = False
        
        if direction == "up":
            if not self.dungeon[x][y].wall("n"):
                generated_sentence = self.sentence_gen_four(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, N, V, 'MOVE_WORD', '.', 1)
                generated_sentence = generated_sentence.replace("direction___", direction)
                generated_sentence = generated_sentence.replace("word___", word)
                print(generated_sentence)
                print("\n")
                x -= 1
                if self.dungeon[x][y].visited == True:
                    visitedBefore = True
                self.dungeon[x][y].visited = True;
            else:                           
                generated_sentence = self.sentence_gen_five(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, N, V, 'MOVE_FAIL2', '.', 2)
                generated_sentence = generated_sentence.replace("direction___", direction)
                generated_sentence = generated_sentence.replace("word___", word)
                print(generated_sentence)
        elif direction == "down":
            if not self.dungeon[x][y].wall("s"):
                generated_sentence = self.sentence_gen_four(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, N, V, 'MOVE_WORD', '.', 1)
                generated_sentence = generated_sentence.replace("direction___", direction)
                generated_sentence = generated_sentence.replace("word___", word)
                print(generated_sentence)
                print("\n")
                x += 1
                if self.dungeon[x][y].visited == True:
                    visitedBefore = True
                self.dungeon[x][y].visited = True;
            else:                           
                generated_sentence = self.sentence_gen_five(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, N, V, 'MOVE_FAIL2', '.', 2)
                generated_sentence = generated_sentence.replace("direction___", direction)
                generated_sentence = generated_sentence.replace("word___", word)
                print(generated_sentence)
        elif direction == "right":
            if not self.dungeon[x][y].wall("e"):
                generated_sentence = self.sentence_gen_four(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, N, V, 'MOVE_WORD', '.', 1)
                generated_sentence = generated_sentence.replace("direction___", direction)
                generated_sentence = generated_sentence.replace("word___", word)
                print(generated_sentence)
                print("\n")
                y += 1
                if self.dungeon[x][y].visited == True:
                    visitedBefore = True
                self.dungeon[x][y].visited = True;
            else:                           
                generated_sentence = self.sentence_gen_five(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, N, V, 'MOVE_FAIL2', '.', 2)
                generated_sentence = generated_sentence.replace("direction___", direction)
                generated_sentence = generated_sentence.replace("word___", word)
                print(generated_sentence)
        elif direction == "left":
            if not self.dungeon[x][y].wall("w"):
                generated_sentence = self.sentence_gen_four(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, N, V, 'MOVE_WORD', '.', 1)
                generated_sentence = generated_sentence.replace("direction___", direction)
                generated_sentence = generated_sentence.replace("word___", word)
                print(generated_sentence)
                print("\n")
                y -= 1
                if self.dungeon[x][y].visited == True:
                    visitedBefore = True
                self.dungeon[x][y].visited = True;
            else:                           
                generated_sentence = self.sentence_gen_five(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, N, V, 'MOVE_FAIL2', '.', 2)
                generated_sentence = generated_sentence.replace("direction___", direction)
                generated_sentence = generated_sentence.replace("word___", word)
                print(generated_sentence)
                
        #print((x,y))
        if self.currentRoom != (x,y):
            self.lastRoom = self.currentRoom
            self.currentRoom = (x,y)
                                  
            if self.dungeon[x][y].type == "End":                
                generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, sixgrams_dict, N, V, 'ENCOUNTER_MONSTER', '?', 1)
                generated_sentence = generated_sentence.replace("monster_type___", self.dungeon[x][y].contents.mType)
                generated_sentence = generated_sentence.replace("monster_weapon___", self.dungeon[x][y].contents.weapon.name.lower())
                print(generated_sentence)
                self.state = "Endgame"
            elif isinstance(self.dungeon[x][y].contents, Monster):
                #print("This room was visited before: ", visitedBefore)
                if visitedBefore == False:
                    generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, sixgrams_dict, N, V, 'ENCOUNTER_MONSTER', '?', 1)
                    generated_sentence = generated_sentence.replace("monster_type___", self.dungeon[x][y].contents.mType)
                    generated_sentence = generated_sentence.replace("monster_weapon___", self.dungeon[x][y].contents.weapon.name.lower())
                    print(generated_sentence)
                elif visitedBefore == True:
                    generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, sixgrams_dict, N, V, 'ENCOUNTER_MONSTER2', '?', 1)
                    generated_sentence = generated_sentence.replace("monster_type___", self.dungeon[x][y].contents.mType)
                    generated_sentence = generated_sentence.replace("monster_weapon___", self.dungeon[x][y].contents.weapon.name.lower())
                    print(generated_sentence)
                self.state = "Fight"
            elif isinstance(self.dungeon[x][y].contents, Chest) and self.dungeon[x][y].contents.items:
                if visitedBefore == False:
                    generated_sentence = self.sentence_gen_five(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, N, V, 'ENCOUNTER_CHEST', '.', 1)
                    num_items = len(self.dungeon[x][y].contents.items)
                    if num_items > 1:
                        generated_sentence = generated_sentence.replace("a single item", str(num_items) + " items")
                    print(generated_sentence)
                elif visitedBefore == True:
                    generated_sentence = self.sentence_gen_five(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, N, V, 'ENCOUNTER_CHEST2', '.', 1)
                    print(generated_sentence)                
                self.state = "Inspect"
            else:
                if isinstance(self.dungeonCopy[x][y].contents, Monster):
                    generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, sixgrams_dict, N, V, 'DEFEATED_MONSTER_ROOM', '.', 1)
                    generated_sentence = generated_sentence.replace("monster_type___", self.dungeonCopy[x][y].contents.mType)
                    print(generated_sentence)
                    generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, sixgrams_dict, N, V, 'GENERAL_QUESTION', '?', 1)
                    print(generated_sentence)
                elif isinstance(self.dungeonCopy[x][y].contents, Chest):
                    generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, sixgrams_dict, N, V, 'EMPTY_CHEST_ROOM', '.', 1)                    
                    print(generated_sentence)
                    generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, sixgrams_dict, N, V, 'GENERAL_QUESTION', '?', 1)
                    print(generated_sentence)
                else:
                    generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, sixgrams_dict, N, V, 'EMPTY_ROOM', '.', 1)
                    print(generated_sentence)
                    generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, sixgrams_dict, N, V, 'GENERAL_QUESTION', '?', 1)
                    print(generated_sentence)
                if self.dungeon[x][y].walls == 7:
                    generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict,  sixgrams_dict, N, V, 'ROOM_MOVE1', '.', 1)
                    generated_sentence = generated_sentence.replace("direction___", "up")
                    print(generated_sentence)
                elif self.dungeon[x][y].walls == 11:
                    generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict,  sixgrams_dict, N, V, 'ROOM_MOVE1', '.', 1)
                    generated_sentence = generated_sentence.replace("direction___", "right")
                    print(generated_sentence)
                elif self.dungeon[x][y].walls == 13:
                    generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict,  sixgrams_dict, N, V, 'ROOM_MOVE1', '.', 1)
                    generated_sentence = generated_sentence.replace("direction___", "down")
                    print(generated_sentence)
                elif self.dungeon[x][y].walls == 14:
                    generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict,  sixgrams_dict, N, V, 'ROOM_MOVE1', '.', 1)
                    generated_sentence = generated_sentence.replace("direction___", "left")
                    print(generated_sentence)
                elif self.dungeon[x][y].walls == 3:
                    generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict,  sixgrams_dict, N, V, 'ROOM_MOVE2', '.', 1)
                    generated_sentence = generated_sentence.replace("direction1___", "right")
                    generated_sentence = generated_sentence.replace("direction2___", "up")
                    print(generated_sentence)
                elif self.dungeon[x][y].walls == 5:
                    generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict,  sixgrams_dict, N, V, 'ROOM_MOVE2', '.', 1)
                    generated_sentence = generated_sentence.replace("direction1___", "down")
                    generated_sentence = generated_sentence.replace("direction2___", "up")
                    print(generated_sentence)
                elif self.dungeon[x][y].walls == 6:
                    generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, sixgrams_dict, N, V, 'ROOM_MOVE2', '.', 1)
                    generated_sentence = generated_sentence.replace("direction1___", "left")
                    generated_sentence = generated_sentence.replace("direction2___", "up")
                    print(generated_sentence)
                elif self.dungeon[x][y].walls == 9:
                    generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, sixgrams_dict, N, V, 'ROOM_MOVE2', '.', 1)
                    generated_sentence = generated_sentence.replace("direction1___", "down")
                    generated_sentence = generated_sentence.replace("direction2___", "right")
                    print(generated_sentence)
                elif self.dungeon[x][y].walls == 10:
                    generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, sixgrams_dict, N, V, 'ROOM_MOVE2', '.', 1)
                    generated_sentence = generated_sentence.replace("direction1___", "left")
                    generated_sentence = generated_sentence.replace("direction2___", "right")
                    print(generated_sentence)
                elif self.dungeon[x][y].walls == 12:
                    generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, sixgrams_dict, N, V, 'ROOM_MOVE2', '.', 1)
                    generated_sentence = generated_sentence.replace("direction1___", "left")
                    generated_sentence = generated_sentence.replace("direction2___", "down")
                    print(generated_sentence)
                elif self.dungeon[x][y].walls == 1:
                    generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, sixgrams_dict, N, V, 'ROOM_MOVE3', '.', 1)
                    generated_sentence = generated_sentence.replace("direction1___", "down")
                    generated_sentence = generated_sentence.replace("direction2___", "right")
                    generated_sentence = generated_sentence.replace("direction3___", "up")
                    print(generated_sentence)
                elif self.dungeon[x][y].walls == 2:
                    generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, sixgrams_dict, N, V, 'ROOM_MOVE3', '.', 1)
                    generated_sentence = generated_sentence.replace("direction1___", "left")
                    generated_sentence = generated_sentence.replace("direction2___", "right")
                    generated_sentence = generated_sentence.replace("direction3___", "up")
                    print(generated_sentence)
                elif self.dungeon[x][y].walls == 4:
                    generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, sixgrams_dict, N, V, 'ROOM_MOVE3', '.', 1)
                    generated_sentence = generated_sentence.replace("direction1___", "left")
                    generated_sentence = generated_sentence.replace("direction2___", "down")
                    generated_sentence = generated_sentence.replace("direction3___", "up")
                    print(generated_sentence)
                elif self.dungeon[x][y].walls == 8:
                    generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, sixgrams_dict, N, V, 'ROOM_MOVE3', '.', 1)
                    generated_sentence = generated_sentence.replace("direction1___", "left")
                    generated_sentence = generated_sentence.replace("direction2___", "down")
                    generated_sentence = generated_sentence.replace("direction3___", "right")
                    print(generated_sentence)
                
    def nextRoom(self, word):
        x1,y1 = self.currentRoom
        #x2,y2 = self.lastRoom
        x,y = tuple(map(operator.sub, self.currentRoom, self.lastRoom))
        #last room -> north -> current room
        if x == -1:
            newDoors = 15 - (self.dungeon[x1][y1].walls + 2)
        elif y == 1:
            newDoors = 15 - (self.dungeon[x1][y1].walls + 1)
        elif x == 1:
            newDoors = 15 - (self.dungeon[x1][y1].walls + 8)
        elif y == -1:
            newDoors = 15 - (self.dungeon[x1][y1].walls + 4)
        
        if newDoors == 8 or newDoors == 4 or newDoors == 2 or newDoors == 1:
            generated_sentence = self.sentence_gen_five(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, N, V, 'NEXT_ROOM', '.', 1)
            print(generated_sentence)
                
        if newDoors == 8:
            self.moving("up", word)
        elif newDoors == 4:
            self.moving("right", word)
        elif newDoors == 2:
            self.moving("down", word)
        elif newDoors == 1:
            self.moving("left", word)

                        
    def move(self):
        playerInput = input("")
        parser = self.inputParser(playerInput)
        if "movement" in self.dictionary.get(parser["Action"], [""]):
            moveWord = parser["Action"]
            if parser["Direct Object"]:
                if len(parser["Direct Object"].split()) == 1:
                    if set(self.dictionary.get(parser["Direct Object"], [""])) & set(self.dictionary['direction']):
                        self.moving(self.dictionary[parser["Direct Object"]][0], moveWord)
                    elif "next" in self.dictionary.get(parser["Direct Object"], [""]) and self.lastRoom is not None:
                        self.nextRoom(moveWord)
            elif parser["Indirect Object"]:
                if any(word in self.dictionary.get(parser["Indirect Object"].split()[-1], [""]) for word in ("room", "door")):
                    if set(self.dictionary.get(parser["Indirect Object"].split()[0], [""])) & set(self.dictionary['direction']):
                        self.moving(self.dictionary[parser["Indirect Object"].split()[0]][0], moveWord)
                    elif "next" in self.dictionary.get(parser["Indirect Object"].split()[0], [""]) and self.lastRoom is not None:
                        self.nextRoom(moveWord)
                elif set(self.dictionary.get(parser["Indirect Object"].split()[-1], [""])) & set(self.dictionary['direction']):
                    self.moving(self.dictionary[parser["Indirect Object"].split()[-1]][0], moveWord)
                elif "next" in self.dictionary.get(parser["Indirect Object"].split()[0], [""]) and self.lastRoom is not None:
                    self.nextRoom(moveWord)
        elif "look" in self.dictionary.get(parser["Action"], [""]) and any("map" in self.dictionary.get(parser[obj], [""]) for obj in ["Direct Object", "Indirect Object"]):
            self.generate_map()
        elif any(word in self.dictionary.get(parser["Action"], [""]) for word in ("look", "open")) and any("chest" in self.dictionary.get(parser[obj], [""]) for obj in ["Direct Object", "Indirect Object"]):
            x,y = self.currentRoom
            if isinstance(self.dungeon[x][y].contents, Chest):
                #print("chest to inspect")
                self.state = "Inspect"
        elif any(word in self.dictionary.get(parser["Action"], [""]) for word in ("use", "drink")) and parser["Direct Object"] != None:
            if len(parser["Direct Object"].split()) == 2 and "potion" in self.dictionary.get(parser["Direct Object"].split()[-1], [""]):
                if "healing" in self.dictionary.get(parser["Direct Object"].split()[0], [""]):
                    #print("Use health potion?")
                    health_potions = [item for item in self.player.inventory if isinstance(item, Potion) and item.type == "Health"]
                    if health_potions:                        
                        #print("Yes!")
                        before_health = self.player.health                        
                        health_potions[0].use(self.player)
                        self.player.inventory.remove(health_potions[0])
                        after_health = self.player.health
                        if after_health > before_health and self.player.health == self.player.maxHealth:
                            generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, sixgrams_dict, N, V, 'HEALTHPOTION', '.', 3)
                            print(generated_sentence)
                            generated_sentence = self.sentence_gen_five(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, N, V, 'HEALTHPOTION_MAXHEALTH', '?', 1)
                            print(generated_sentence)
                        else:
                            generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, sixgrams_dict, N, V, 'HEALTHPOTION', '?', 1)
                            print(generated_sentence)
                    else:
                        #print("No")
                        generated_sentence = self.sentence_gen_five(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, N, V, 'POTION_FAIL', '.', 1)
                        generated_sentence = generated_sentence.replace("type___", "health")
                        print(generated_sentence)
                elif "strength" in self.dictionary.get(parser["Direct Object"].split()[0], [""]):
                    #print("Use strength potion?")
                    strength_potions = [item for item in self.player.inventory if isinstance(item, Potion) and item.type == "Strength"]
                    if strength_potions:
                        #print("Yes!")
                        generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, sixgrams_dict, N, V, 'STRENGTHPOTION', '?', 1)
                        print(generated_sentence)
                        strength_potions[0].use(self.player)
                        self.player.inventory.remove(strength_potions[0])
                    else:
                        #print("No")
                        generated_sentence = self.sentence_gen_five(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, N, V, 'POTION_FAIL', '.', 1)
                        generated_sentence = generated_sentence.replace("type___", "strength")
                        print(generated_sentence)
        elif "show" in self.dictionary.get(parser["Action"], [""]) and parser["Direct Object"] != None:
            if "health" in self.dictionary.get(parser["Direct Object"].split()[-1], [""]):
                generated_sentence = self.sentence_gen_five(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, N, V, 'SHOW_HEALTH', '.', 1)
                generated_sentence = generated_sentence.replace("health___", str(self.player.health))
                print(generated_sentence)
                #print("Health:", self.player.health)
            elif "inventory" in self.dictionary.get(parser["Direct Object"].split()[-1], [""]):
                if self.player.inventory:
                    generated_sentence = self.sentence_gen_four(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, N, V, 'SHOW_INVENTORY', '.', 1)
                    print(generated_sentence)
                    for item in self.player.inventory:
                        print(item.type,"Potion")
                else:
                    generated_sentence = self.sentence_gen_five(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, N, V, 'NO_ITEMS', '.', 1)
                    print(generated_sentence)
                    #print("No items")
            print("\n")
        else:
            generated_sentence = self.sentence_gen_five(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, N, V, 'INAPPROPRIATE', '.', 2)
            print(generated_sentence)
        
    def fight(self, monster):
        while 0 < self.player.health and 0 < monster.health:
            print("\n")
            print("Player's health:", self.player.health, "\nEnemy's health:", monster.health)
            print("\n")
            playerInput = input("")
            parser = self.inputParser(playerInput)
            
            if "attack" in self.dictionary.get(parser["Action"], [""]):
                if parser["Direct Object"] is None or any(word in self.dictionary.get(parser["Direct Object"], [""]) for word in ("monster", "enemy")):
                    #Player move
                    playerDamage = random.randint(self.player.weapon.minDamage, self.player.weapon.maxDamage) + self.player.strength
                    if random.random() < self.player.weapon.criticalChance:
                        generated_sentence = self.sentence_gen_five(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, N, V, 'ATTACK', '.', 1)
                        generated_sentence = generated_sentence.replace("weapon_name___", game.player.weapon.name.lower())
                        generated_sentence = generated_sentence.replace("damage_type___", "critical damage")
                        print(generated_sentence)
                        #print("Player Critical!")
                        playerDamage = int(playerDamage * self.player.weapon.critical)
                        #crit_damage = int(base_damage * crit_multiplier)
                    else:
                        generated_sentence = self.sentence_gen_five(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, N, V, 'ATTACK', '.', 1)
                        generated_sentence = generated_sentence.replace("weapon_name___", game.player.weapon.name.lower())
                        generated_sentence = generated_sentence.replace("damage_type___", "regular damage")
                        print(generated_sentence)
                    print("Player Damage:",playerDamage)
                    monster.health -= playerDamage
                    
                    if monster.health <= 0:
                        generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, sixgrams_dict, N, V, 'MONSTER_DEFEATED', '.', 3)
                        print(generated_sentence)
                        #print("Enemy defeated!")
                        print("\n")
                        x,y = self.currentRoom
                        self.dungeon[x][y].contents = None
                        for ability in self.player.abilities:
                            ability.cooldown = 0
                        self.state = "Move"
                        if self.dungeon[x][y].walls == 7:
                            generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict,  sixgrams_dict, N, V, 'ROOM_MOVE1', '.', 1)
                            generated_sentence = generated_sentence.replace("direction___", "up")
                            print(generated_sentence)
                        elif self.dungeon[x][y].walls == 11:
                            generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict,  sixgrams_dict, N, V, 'ROOM_MOVE1', '.', 1)
                            generated_sentence = generated_sentence.replace("direction___", "right")
                            print(generated_sentence)
                        elif self.dungeon[x][y].walls == 13:
                            generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict,  sixgrams_dict, N, V, 'ROOM_MOVE1', '.', 1)
                            generated_sentence = generated_sentence.replace("direction___", "down")
                            print(generated_sentence)
                        elif self.dungeon[x][y].walls == 14:
                            generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict,  sixgrams_dict, N, V, 'ROOM_MOVE1', '.', 1)
                            generated_sentence = generated_sentence.replace("direction___", "left")
                            print(generated_sentence)
                        elif self.dungeon[x][y].walls == 3:
                            generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict,  sixgrams_dict, N, V, 'ROOM_MOVE2', '.', 1)
                            generated_sentence = generated_sentence.replace("direction1___", "right")
                            generated_sentence = generated_sentence.replace("direction2___", "up")
                            print(generated_sentence)
                        elif self.dungeon[x][y].walls == 5:
                            generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict,  sixgrams_dict, N, V, 'ROOM_MOVE2', '.', 1)
                            generated_sentence = generated_sentence.replace("direction1___", "down")
                            generated_sentence = generated_sentence.replace("direction2___", "up")
                            print(generated_sentence)
                        elif self.dungeon[x][y].walls == 6:
                            generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, sixgrams_dict, N, V, 'ROOM_MOVE2', '.', 1)
                            generated_sentence = generated_sentence.replace("direction1___", "left")
                            generated_sentence = generated_sentence.replace("direction2___", "up")
                            print(generated_sentence)
                        elif self.dungeon[x][y].walls == 9:
                            generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, sixgrams_dict, N, V, 'ROOM_MOVE2', '.', 1)
                            generated_sentence = generated_sentence.replace("direction1___", "down")
                            generated_sentence = generated_sentence.replace("direction2___", "right")
                            print(generated_sentence)
                        elif self.dungeon[x][y].walls == 10:
                            generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, sixgrams_dict, N, V, 'ROOM_MOVE2', '.', 1)
                            generated_sentence = generated_sentence.replace("direction1___", "left")
                            generated_sentence = generated_sentence.replace("direction2___", "right")
                            print(generated_sentence)
                        elif self.dungeon[x][y].walls == 12:
                            generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, sixgrams_dict, N, V, 'ROOM_MOVE2', '.', 1)
                            generated_sentence = generated_sentence.replace("direction1___", "left")
                            generated_sentence = generated_sentence.replace("direction2___", "down")
                            print(generated_sentence)
                        elif self.dungeon[x][y].walls == 1:
                            generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, sixgrams_dict, N, V, 'ROOM_MOVE3', '.', 1)
                            generated_sentence = generated_sentence.replace("direction1___", "down")
                            generated_sentence = generated_sentence.replace("direction2___", "right")
                            generated_sentence = generated_sentence.replace("direction3___", "up")
                            print(generated_sentence)
                        elif self.dungeon[x][y].walls == 2:
                            generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, sixgrams_dict, N, V, 'ROOM_MOVE3', '.', 1)
                            generated_sentence = generated_sentence.replace("direction1___", "left")
                            generated_sentence = generated_sentence.replace("direction2___", "right")
                            generated_sentence = generated_sentence.replace("direction3___", "up")
                            print(generated_sentence)
                        elif self.dungeon[x][y].walls == 4:
                            generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, sixgrams_dict, N, V, 'ROOM_MOVE3', '.', 1)
                            generated_sentence = generated_sentence.replace("direction1___", "left")
                            generated_sentence = generated_sentence.replace("direction2___", "down")
                            generated_sentence = generated_sentence.replace("direction3___", "up")
                            print(generated_sentence)
                        elif self.dungeon[x][y].walls == 8:
                            generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, sixgrams_dict, N, V, 'ROOM_MOVE3', '.', 1)
                            generated_sentence = generated_sentence.replace("direction1___", "left")
                            generated_sentence = generated_sentence.replace("direction2___", "down")
                            generated_sentence = generated_sentence.replace("direction3___", "right")
                            print(generated_sentence)
                        break
                    
                    print("\n")
                    #Monster move
                    if monster.isStuned:
                        generated_sentence = self.sentence_gen_five(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, N, V, 'STUN_WEAR_OFF', '.', 1)
                        print(generated_sentence)
                        #print("Monster is no longer stunned")
                        monster.isStuned = False
                    else:
                        if random.random() <= self.player.dodge:
                            generated_phrase1 = self.sentence_gen_five(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, N, V, 'MONSTER_ATTACK_PART1', '@@', 1)
                            generated_phrase1 = generated_phrase1.replace("monster_weapon___", monster.weapon.name.lower())
                            generated_phrase1 = generated_phrase1.replace("@@", "")
                            generated_phrase2 = self.sentence_gen_five(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, N, V, 'MONSTER_ATTACK_DODGE', '.', 1)                            
                            generated_sentence = generated_phrase1 + generated_phrase2
                            print(generated_sentence)
                            #print("Dodge. No damage taken")
                            generated_sentence = self.sentence_gen_five(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, N, V, 'PLAYER_NOT_HIT', '?', 1)
                            generated_sentence = generated_sentence.replace("monster_type___", monster.mType)
                            print(generated_sentence)
                        else:
                            generated_phrase1 = self.sentence_gen_five(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, N, V, 'MONSTER_ATTACK_P1', '@@', 1)
                            generated_phrase1 = generated_phrase1.replace("monster_weapon___", monster.weapon.name.lower())
                            generated_phrase1 = generated_phrase1.replace("@@", "")
                            enemyDamage = random.randint(monster.weapon.minDamage, monster.weapon.maxDamage)
                            if random.random() < monster.weapon.criticalChance:
                                generated_phrase2 = self.sentence_gen_five(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, N, V, 'MONSTER_ATTACK_HIT', '.', 1)                                
                                generated_phrase2 = generated_phrase2.replace("monster_damage_type___", "critical damage")
                                generated_sentence = generated_phrase1 + generated_phrase2
                                print(generated_sentence)
                                #print("Monster Critical!")
                                enemyDamage = int(enemyDamage * monster.weapon.critical)
                            else:
                                generated_phrase2 = self.sentence_gen_five(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, N, V, 'MONSTER_ATTACK_HIT', '.', 1)                                
                                generated_phrase2 = generated_phrase2.replace("monster_damage_type___", "regular damage")
                                generated_sentence = generated_phrase1 + generated_phrase2
                                print(generated_sentence)
                            #print("Enemy Damage:",enemyDamage)
                            self.player.health -= enemyDamage
                            if self.player.health > 0:
                                generated_sentence = self.sentence_gen_four(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, N, V, 'PLAYER_HIT', '?', 1)                        
                                print(generated_sentence)
                        
                        if self.player.health <= 0:
                            generated_sentence = self.sentence_gen_five(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, N, V, 'PLAYER_DEFEATED', '.', 1)
                            print(generated_sentence)
                            #print("Game Over!")
                            self.state = "Game Over"
                            self.running = False
                            break
                        
                    if self.player.abilities[0].cooldown > 0:
                        self.player.abilities[0].cooldown -= 1
                        if self.player.abilities[0].cooldown == 0:
                            generated_sentence = self.sentence_gen_five(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, N, V, 'SKILL_USABLE', '.', 1)                            
                            generated_sentence = generated_sentence.replace("skill___", "stun")
                            print(generated_sentence)
                            #print("You can now stun")
                    if self.player.abilities[1].cooldown > 0:
                        self.player.abilities[1].cooldown -= 1
                        if self.player.abilities[1].cooldown == 0:
                            generated_sentence = self.sentence_gen_five(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, N, V, 'SKILL_USABLE', '.', 1)                            
                            generated_sentence = generated_sentence.replace("skill___", "fireball")
                            print(generated_sentence)
                            #print("You can now fireball")
            
            elif any(word in self.dictionary.get(parser["Action"], [""]) for word in ("use", "drink")) and parser["Direct Object"] != None:
                if len((parser["Direct Object"] or "").split()) == 2 and "potion" in self.dictionary.get(parser["Direct Object"].split()[-1], [""]):
                    if "healing" in self.dictionary.get(parser["Direct Object"].split()[0], [""]):
                        #print("Use health potion?")
                        health_potions = [item for item in self.player.inventory if isinstance(item, Potion) and item.type == "Health"]
                        if health_potions:                            
                            #print("Yes!")   
                            before_health = self.player.health
                            health_potions[0].use(self.player)
                            self.player.inventory.remove(health_potions[0])
                            after_health = self.player.health
                            if after_health > before_health and self.player.health == self.player.maxHealth:
                                generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, sixgrams_dict, N, V, 'HEALTHPOTION', '.', 3)
                                print(generated_sentence)
                                generated_sentence = self.sentence_gen_five(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, N, V, 'HEALTHPOTION_MAXHEALTH', '?', 1)
                                print(generated_sentence)
                            else:
                                generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, sixgrams_dict, N, V, 'HEALTHPOTION', '?', 1)
                                print(generated_sentence)
                        else:
                            #print("No")
                            generated_sentence = self.sentence_gen_five(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, N, V, 'POTION_FAIL', '.', 1)
                            generated_sentence = generated_sentence.replace("type___", "health")
                            print(generated_sentence) 
                        
                        if monster.isStuned:
                            generated_sentence = self.sentence_gen_five(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, N, V, 'STUN_WEAR_OFF', '.', 1)
                            print(generated_sentence)
                            #print("Monster is no longer stunned")
                            monster.isStuned = False
                    elif "strength" in self.dictionary.get(parser["Direct Object"].split()[0], [""]):
                        #print("Use strength potion?")
                        strength_potions = [item for item in self.player.inventory if isinstance(item, Potion) and item.type == "Strength"]
                        if strength_potions:
                            #print("Yes!")
                            generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, sixgrams_dict, N, V, 'STRENGTHPOTION', '?', 1)
                            print(generated_sentence)
                            strength_potions[0].use(self.player)
                            self.player.inventory.remove(strength_potions[0])
                        else:
                            #print("No")
                            generated_sentence = self.sentence_gen_five(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, N, V, 'POTION_FAIL', '.', 1)
                            generated_sentence = generated_sentence.replace("type___", "strength")
                            print(generated_sentence)
                        
                        if monster.isStuned:
                            generated_sentence = self.sentence_gen_five(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, N, V, 'STUN_WEAR_OFF', '.', 1)
                            print(generated_sentence)
                            #print("Monster is no longer stunned")
                            monster.isStuned = False
            elif "run" in self.dictionary.get(parser["Action"], [""]):
                generated_sentence = self.sentence_gen_five(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, N, V, 'RUN', '?', 1)
                print(generated_sentence)
                print("\n")
                oldRoom = self.currentRoom
                self.currentRoom = self.lastRoom
                self.lastRoom = oldRoom
                monster.isStuned = False
                self.state = "Move"
                x = self.currentRoom[0]
                y = self.currentRoom[1]
                if self.dungeon[x][y].walls == 7:
                    generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict,  sixgrams_dict, N, V, 'ROOM_MOVE1', '.', 1)
                    generated_sentence = generated_sentence.replace("direction___", "up")
                    print(generated_sentence)
                elif self.dungeon[x][y].walls == 11:
                    generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict,  sixgrams_dict, N, V, 'ROOM_MOVE1', '.', 1)
                    generated_sentence = generated_sentence.replace("direction___", "right")
                    print(generated_sentence)
                elif self.dungeon[x][y].walls == 13:
                    generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict,  sixgrams_dict, N, V, 'ROOM_MOVE1', '.', 1)
                    generated_sentence = generated_sentence.replace("direction___", "down")
                    print(generated_sentence)
                elif self.dungeon[x][y].walls == 14:
                    generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict,  sixgrams_dict, N, V, 'ROOM_MOVE1', '.', 1)
                    generated_sentence = generated_sentence.replace("direction___", "left")
                    print(generated_sentence)
                elif self.dungeon[x][y].walls == 3:
                    generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict,  sixgrams_dict, N, V, 'ROOM_MOVE2', '.', 1)
                    generated_sentence = generated_sentence.replace("direction1___", "right")
                    generated_sentence = generated_sentence.replace("direction2___", "up")
                    print(generated_sentence)
                elif self.dungeon[x][y].walls == 5:
                    generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict,  sixgrams_dict, N, V, 'ROOM_MOVE2', '.', 1)
                    generated_sentence = generated_sentence.replace("direction1___", "down")
                    generated_sentence = generated_sentence.replace("direction2___", "up")
                    print(generated_sentence)
                elif self.dungeon[x][y].walls == 6:
                    generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, sixgrams_dict, N, V, 'ROOM_MOVE2', '.', 1)
                    generated_sentence = generated_sentence.replace("direction1___", "left")
                    generated_sentence = generated_sentence.replace("direction2___", "up")
                    print(generated_sentence)
                elif self.dungeon[x][y].walls == 9:
                    generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, sixgrams_dict, N, V, 'ROOM_MOVE2', '.', 1)
                    generated_sentence = generated_sentence.replace("direction1___", "down")
                    generated_sentence = generated_sentence.replace("direction2___", "right")
                    print(generated_sentence)
                elif self.dungeon[x][y].walls == 10:
                    generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, sixgrams_dict, N, V, 'ROOM_MOVE2', '.', 1)
                    generated_sentence = generated_sentence.replace("direction1___", "left")
                    generated_sentence = generated_sentence.replace("direction2___", "right")
                    print(generated_sentence)
                elif self.dungeon[x][y].walls == 12:
                    generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, sixgrams_dict, N, V, 'ROOM_MOVE2', '.', 1)
                    generated_sentence = generated_sentence.replace("direction1___", "left")
                    generated_sentence = generated_sentence.replace("direction2___", "down")
                    print(generated_sentence)
                elif self.dungeon[x][y].walls == 1:
                    generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, sixgrams_dict, N, V, 'ROOM_MOVE3', '.', 1)
                    generated_sentence = generated_sentence.replace("direction1___", "down")
                    generated_sentence = generated_sentence.replace("direction2___", "right")
                    generated_sentence = generated_sentence.replace("direction3___", "up")
                    print(generated_sentence)
                elif self.dungeon[x][y].walls == 2:
                    generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, sixgrams_dict, N, V, 'ROOM_MOVE3', '.', 1)
                    generated_sentence = generated_sentence.replace("direction1___", "left")
                    generated_sentence = generated_sentence.replace("direction2___", "right")
                    generated_sentence = generated_sentence.replace("direction3___", "up")
                    print(generated_sentence)
                elif self.dungeon[x][y].walls == 4:
                    generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, sixgrams_dict, N, V, 'ROOM_MOVE3', '.', 1)
                    generated_sentence = generated_sentence.replace("direction1___", "left")
                    generated_sentence = generated_sentence.replace("direction2___", "down")
                    generated_sentence = generated_sentence.replace("direction3___", "up")
                    print(generated_sentence)
                elif self.dungeon[x][y].walls == 8:
                    generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, sixgrams_dict, N, V, 'ROOM_MOVE3', '.', 1)
                    generated_sentence = generated_sentence.replace("direction1___", "left")
                    generated_sentence = generated_sentence.replace("direction2___", "down")
                    generated_sentence = generated_sentence.replace("direction3___", "right")
                    print(generated_sentence)
                break
            elif "show" in self.dictionary.get(parser["Action"], [""]) and parser["Direct Object"] != None:
                if "health" in self.dictionary.get(parser["Direct Object"].split()[-1], [""]):
                    generated_sentence = self.sentence_gen_five(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, N, V, 'SHOW_HEALTH', '.', 1)
                    generated_sentence = generated_sentence.replace("health___", str(self.player.health))
                    print(generated_sentence)
                    #print("Health:", self.player.health)
                elif "inventory" in self.dictionary.get(parser["Direct Object"].split()[-1], [""]):                    
                    if self.player.inventory:
                        generated_sentence = self.sentence_gen_four(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, N, V, 'SHOW_INVENTORY', '.', 1)
                        print(generated_sentence)
                        for item in self.player.inventory:
                            print(item.type,"Potion")
                    else:
                        generated_sentence = self.sentence_gen_five(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, N, V, 'NO_ITEMS', '.', 1)
                        print(generated_sentence)
                        #print("No items")
            elif "stun" in self.dictionary.get(parser["Action"], [""]):
                if parser["Direct Object"] is None or any(word in self.dictionary.get(parser["Direct Object"], [""]) for word in ("monster", "enemy")):
                    stun = self.player.abilities[0]
                    if stun.cooldown == 0:
                        generated_sentence = self.sentence_gen_five(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, N, V, 'STUN_ATTEMPT', '.', 1)
                        print(generated_sentence)
                        if random.random() < stun.chance:
                            generated_sentence = self.sentence_gen_five(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, N, V, 'STUN_ATTEMPT_SUCCESS', '.', 1)
                            print(generated_sentence)
                            #print("stunned enemy")
                            playerDamage = random.randint(stun.minDamage, stun.maxDamage)
                            generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, sixgrams_dict, N, V, 'STUN_DAMAGE', '.', 1)
                            print(generated_sentence)
                            print("Player Stun Damage:",playerDamage)
                            monster.health -= playerDamage
                            monster.isStuned = True
                            
                            if monster.health <= 0:
                                generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, sixgrams_dict, N, V, 'MONSTER_DEFEATED', '.', 3)
                                print(generated_sentence)
                                #print("Enemy defeated!")
                                print("\n")
                                x,y = self.currentRoom
                                self.dungeon[x][y].contents = None
                                for ability in self.player.abilities:
                                    ability.cooldown = 0
                                self.state = "Move"
                                if self.dungeon[x][y].walls == 7:
                                    generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict,  sixgrams_dict, N, V, 'ROOM_MOVE1', '.', 1)
                                    generated_sentence = generated_sentence.replace("direction___", "up")
                                    print(generated_sentence)
                                elif self.dungeon[x][y].walls == 11:
                                    generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict,  sixgrams_dict, N, V, 'ROOM_MOVE1', '.', 1)
                                    generated_sentence = generated_sentence.replace("direction___", "right")
                                    print(generated_sentence)
                                elif self.dungeon[x][y].walls == 13:
                                    generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict,  sixgrams_dict, N, V, 'ROOM_MOVE1', '.', 1)
                                    generated_sentence = generated_sentence.replace("direction___", "down")
                                    print(generated_sentence)
                                elif self.dungeon[x][y].walls == 14:
                                    generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict,  sixgrams_dict, N, V, 'ROOM_MOVE1', '.', 1)
                                    generated_sentence = generated_sentence.replace("direction___", "left")
                                    print(generated_sentence)
                                elif self.dungeon[x][y].walls == 3:
                                    generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict,  sixgrams_dict, N, V, 'ROOM_MOVE2', '.', 1)
                                    generated_sentence = generated_sentence.replace("direction1___", "right")
                                    generated_sentence = generated_sentence.replace("direction2___", "up")
                                    print(generated_sentence)
                                elif self.dungeon[x][y].walls == 5:
                                    generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict,  sixgrams_dict, N, V, 'ROOM_MOVE2', '.', 1)
                                    generated_sentence = generated_sentence.replace("direction1___", "down")
                                    generated_sentence = generated_sentence.replace("direction2___", "up")
                                    print(generated_sentence)
                                elif self.dungeon[x][y].walls == 6:
                                    generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, sixgrams_dict, N, V, 'ROOM_MOVE2', '.', 1)
                                    generated_sentence = generated_sentence.replace("direction1___", "left")
                                    generated_sentence = generated_sentence.replace("direction2___", "up")
                                    print(generated_sentence)
                                elif self.dungeon[x][y].walls == 9:
                                    generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, sixgrams_dict, N, V, 'ROOM_MOVE2', '.', 1)
                                    generated_sentence = generated_sentence.replace("direction1___", "down")
                                    generated_sentence = generated_sentence.replace("direction2___", "right")
                                    print(generated_sentence)
                                elif self.dungeon[x][y].walls == 10:
                                    generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, sixgrams_dict, N, V, 'ROOM_MOVE2', '.', 1)
                                    generated_sentence = generated_sentence.replace("direction1___", "left")
                                    generated_sentence = generated_sentence.replace("direction2___", "right")
                                    print(generated_sentence)
                                elif self.dungeon[x][y].walls == 12:
                                    generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, sixgrams_dict, N, V, 'ROOM_MOVE2', '.', 1)
                                    generated_sentence = generated_sentence.replace("direction1___", "left")
                                    generated_sentence = generated_sentence.replace("direction2___", "down")
                                    print(generated_sentence)
                                elif self.dungeon[x][y].walls == 1:
                                    generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, sixgrams_dict, N, V, 'ROOM_MOVE3', '.', 1)
                                    generated_sentence = generated_sentence.replace("direction1___", "down")
                                    generated_sentence = generated_sentence.replace("direction2___", "right")
                                    generated_sentence = generated_sentence.replace("direction3___", "up")
                                    print(generated_sentence)
                                elif self.dungeon[x][y].walls == 2:
                                    generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, sixgrams_dict, N, V, 'ROOM_MOVE3', '.', 1)
                                    generated_sentence = generated_sentence.replace("direction1___", "left")
                                    generated_sentence = generated_sentence.replace("direction2___", "right")
                                    generated_sentence = generated_sentence.replace("direction3___", "up")
                                    print(generated_sentence)
                                elif self.dungeon[x][y].walls == 4:
                                    generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, sixgrams_dict, N, V, 'ROOM_MOVE3', '.', 1)
                                    generated_sentence = generated_sentence.replace("direction1___", "left")
                                    generated_sentence = generated_sentence.replace("direction2___", "down")
                                    generated_sentence = generated_sentence.replace("direction3___", "up")
                                    print(generated_sentence)
                                elif self.dungeon[x][y].walls == 8:
                                    generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, sixgrams_dict, N, V, 'ROOM_MOVE3', '.', 1)
                                    generated_sentence = generated_sentence.replace("direction1___", "left")
                                    generated_sentence = generated_sentence.replace("direction2___", "down")
                                    generated_sentence = generated_sentence.replace("direction3___", "right")
                                    print(generated_sentence)
                                break
                            generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, sixgrams_dict, N, V, 'GENERAL_QUESTION', '?', 1)
                            print(generated_sentence)
                            
                        else:
                            generated_sentence = self.sentence_gen_five(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, N, V, 'STUN_ATTEMPT_FAIL', '.', 1)
                            print(generated_sentence)
                            #print("didn't stun enemy")
                            if monster.isStuned:
                                generated_sentence = self.sentence_gen_five(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, N, V, 'STUN_WEAR_OFF', '.', 1)
                                print(generated_sentence)
                                #print("Monster is no longer stunned")
                                monster.isStuned = False
                                generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, sixgrams_dict, N, V, 'GENERAL_QUESTION', '?', 1)
                                print(generated_sentence)
                            else:
                                print("\n")
                                if random.random() <= self.player.dodge:
                                    generated_phrase1 = self.sentence_gen_five(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, N, V, 'MONSTER_ATTACK_PART1', '@@', 1)
                                    generated_phrase1 = generated_phrase1.replace("monster_weapon___", monster.weapon.name.lower())
                                    generated_phrase1 = generated_phrase1.replace("@@", "")
                                    generated_phrase2 = self.sentence_gen_five(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, N, V, 'MONSTER_ATTACK_DODGE', '.', 1)                            
                                    generated_sentence = generated_phrase1 + generated_phrase2
                                    print(generated_sentence)
                                    #print("Dodge. No damage taken")
                                    generated_sentence = self.sentence_gen_five(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, N, V, 'PLAYER_NOT_HIT', '?', 1)
                                    generated_sentence = generated_sentence.replace("monster_type___", monster.mType)
                                    print(generated_sentence)
                                else:
                                    generated_phrase1 = self.sentence_gen_five(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, N, V, 'MONSTER_ATTACK_P1', '@@', 1)
                                    generated_phrase1 = generated_phrase1.replace("monster_weapon___", monster.weapon.name.lower())
                                    generated_phrase1 = generated_phrase1.replace("@@", "")
                                    enemyDamage = random.randint(monster.weapon.minDamage, monster.weapon.maxDamage)
                                    if random.random() < monster.weapon.criticalChance:
                                        generated_phrase2 = self.sentence_gen_five(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, N, V, 'MONSTER_ATTACK_HIT', '.', 1)                                
                                        generated_phrase2 = generated_phrase2.replace("monster_damage_type___", "critical damage")
                                        generated_sentence = generated_phrase1 + generated_phrase2
                                        print(generated_sentence)
                                        #print("Monster Critical!")
                                        enemyDamage = int(enemyDamage * monster.weapon.critical)
                                    else:
                                        generated_phrase2 = self.sentence_gen_five(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, N, V, 'MONSTER_ATTACK_HIT', '.', 1)                                
                                        generated_phrase2 = generated_phrase2.replace("monster_damage_type___", "regular damage")
                                        generated_sentence = generated_phrase1 + generated_phrase2
                                        print(generated_sentence)
                                    #print("Enemy Damage:",enemyDamage)
                                    self.player.health -= enemyDamage
                                    if self.player.health > 0:
                                        generated_sentence = self.sentence_gen_four(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, N, V, 'PLAYER_HIT', '?', 1)                        
                                        print(generated_sentence)
                                if self.player.health <= 0:
                                    generated_sentence = self.sentence_gen_five(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, N, V, 'PLAYER_DEFEATED', '.', 1)
                                    print(generated_sentence)
                                    #print("Game Over!")
                                    self.state = "Game Over"
                                    self.running = False
                                    break                         
                        stun.cooldown = stun.refreshRate
                    else:                        
                        generated_sentence = self.sentence_gen_five(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, N, V, 'SKILL_FAIL', '.', 1)
                        generated_sentence = generated_sentence.replace("skill___", "stun")
                        print(generated_sentence)
                        #print("Can't stun now")
                        
                        if monster.isStuned:
                            generated_sentence = self.sentence_gen_five(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, N, V, 'STUN_WEAR_OFF', '.', 1)
                            print(generated_sentence)
                            #print("Monster is no longer stunned")
                            monster.isStuned = False
            elif "cast" in self.dictionary.get(parser["Action"], [""]) and "fireball" in self.dictionary.get(parser["Direct Object"], [""]):
                fireball = self.player.abilities[1]
                if fireball.cooldown == 0:
                    generated_sentence = self.sentence_gen_five(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, N, V, 'FIREBALL_ATTEMPT', '.', 1)
                    print(generated_sentence)
                    if random.random() < fireball.chance:
                        generated_sentence = self.sentence_gen_five(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, N, V, 'FIREBALL_ATTEMPT_SUCCESS', '.', 1)
                        print(generated_sentence)
                        #print("enemy fireballed")
                        playerDamage = random.randint(fireball.minDamage, fireball.maxDamage)
                        print("Player Fireball Damage:",playerDamage)
                        monster.health -= playerDamage
                        
                        if monster.health <= 0:
                            generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, sixgrams_dict, N, V, 'MONSTER_DEFEATED', '.', 3)
                            print(generated_sentence)
                            #print("Enemy defeated!")
                            print("\n")
                            x,y = self.currentRoom
                            self.dungeon[x][y].contents = None
                            for ability in self.player.abilities:
                                ability.cooldown = 0
                            self.state = "Move"
                            if self.dungeon[x][y].walls == 7:
                                generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict,  sixgrams_dict, N, V, 'ROOM_MOVE1', '.', 1)
                                generated_sentence = generated_sentence.replace("direction___", "up")
                                print(generated_sentence)
                            elif self.dungeon[x][y].walls == 11:
                                generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict,  sixgrams_dict, N, V, 'ROOM_MOVE1', '.', 1)
                                generated_sentence = generated_sentence.replace("direction___", "right")
                                print(generated_sentence)
                            elif self.dungeon[x][y].walls == 13:
                                generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict,  sixgrams_dict, N, V, 'ROOM_MOVE1', '.', 1)
                                generated_sentence = generated_sentence.replace("direction___", "down")
                                print(generated_sentence)
                            elif self.dungeon[x][y].walls == 14:
                                generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict,  sixgrams_dict, N, V, 'ROOM_MOVE1', '.', 1)
                                generated_sentence = generated_sentence.replace("direction___", "left")
                                print(generated_sentence)
                            elif self.dungeon[x][y].walls == 3:
                                generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict,  sixgrams_dict, N, V, 'ROOM_MOVE2', '.', 1)
                                generated_sentence = generated_sentence.replace("direction1___", "right")
                                generated_sentence = generated_sentence.replace("direction2___", "up")
                                print(generated_sentence)
                            elif self.dungeon[x][y].walls == 5:
                                generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict,  sixgrams_dict, N, V, 'ROOM_MOVE2', '.', 1)
                                generated_sentence = generated_sentence.replace("direction1___", "down")
                                generated_sentence = generated_sentence.replace("direction2___", "up")
                                print(generated_sentence)
                            elif self.dungeon[x][y].walls == 6:
                                generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, sixgrams_dict, N, V, 'ROOM_MOVE2', '.', 1)
                                generated_sentence = generated_sentence.replace("direction1___", "left")
                                generated_sentence = generated_sentence.replace("direction2___", "up")
                                print(generated_sentence)
                            elif self.dungeon[x][y].walls == 9:
                                generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, sixgrams_dict, N, V, 'ROOM_MOVE2', '.', 1)
                                generated_sentence = generated_sentence.replace("direction1___", "down")
                                generated_sentence = generated_sentence.replace("direction2___", "right")
                                print(generated_sentence)
                            elif self.dungeon[x][y].walls == 10:
                                generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, sixgrams_dict, N, V, 'ROOM_MOVE2', '.', 1)
                                generated_sentence = generated_sentence.replace("direction1___", "left")
                                generated_sentence = generated_sentence.replace("direction2___", "right")
                                print(generated_sentence)
                            elif self.dungeon[x][y].walls == 12:
                                generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, sixgrams_dict, N, V, 'ROOM_MOVE2', '.', 1)
                                generated_sentence = generated_sentence.replace("direction1___", "left")
                                generated_sentence = generated_sentence.replace("direction2___", "down")
                                print(generated_sentence)
                            elif self.dungeon[x][y].walls == 1:
                                generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, sixgrams_dict, N, V, 'ROOM_MOVE3', '.', 1)
                                generated_sentence = generated_sentence.replace("direction1___", "down")
                                generated_sentence = generated_sentence.replace("direction2___", "right")
                                generated_sentence = generated_sentence.replace("direction3___", "up")
                                print(generated_sentence)
                            elif self.dungeon[x][y].walls == 2:
                                generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, sixgrams_dict, N, V, 'ROOM_MOVE3', '.', 1)
                                generated_sentence = generated_sentence.replace("direction1___", "left")
                                generated_sentence = generated_sentence.replace("direction2___", "right")
                                generated_sentence = generated_sentence.replace("direction3___", "up")
                                print(generated_sentence)
                            elif self.dungeon[x][y].walls == 4:
                                generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, sixgrams_dict, N, V, 'ROOM_MOVE3', '.', 1)
                                generated_sentence = generated_sentence.replace("direction1___", "left")
                                generated_sentence = generated_sentence.replace("direction2___", "down")
                                generated_sentence = generated_sentence.replace("direction3___", "up")
                                print(generated_sentence)
                            elif self.dungeon[x][y].walls == 8:
                                generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, sixgrams_dict, N, V, 'ROOM_MOVE3', '.', 1)
                                generated_sentence = generated_sentence.replace("direction1___", "left")
                                generated_sentence = generated_sentence.replace("direction2___", "down")
                                generated_sentence = generated_sentence.replace("direction3___", "right")
                                print(generated_sentence)
                            break
                    else:
                        generated_sentence = self.sentence_gen_five(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, N, V, 'FIREBALL_ATTEMPT_FAIL', '.', 1)
                        print(generated_sentence)
                        #print("didn't hit enemy")
                    generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, sixgrams_dict, N, V, 'GENERAL_QUESTION', '?', 1)
                    print(generated_sentence)
                    fireball.cooldown = fireball.refreshRate
                else:
                    generated_sentence = self.sentence_gen_five(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, N, V, 'SKILL_FAIL', '.', 1)
                    generated_sentence = generated_sentence.replace("skill___", "fireball")
                    print(generated_sentence)
                    #print("Can't fireball now")
            else:
                generated_sentence = self.sentence_gen_five(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, N, V, 'INAPPROPRIATE', '.', 2)
                print(generated_sentence)
                        
            
            
    def inspect(self, chest):
        while True:
            itemsToRemove = []
            for item in chest.items:
                if isinstance(item, Weapon):
                    if item.name == "Long Sword":
                        generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, sixgrams_dict, N, V, 'LONG_SWORD_DESCRIPTION', '?', 1)
                        print(generated_sentence)
                    elif item.name == "Steel Sword":
                        generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, sixgrams_dict, N, V, 'STEEL_SWORD_DESCRIPTION', '?', 1)
                        print(generated_sentence)
                    #print("Take",item.name+"?")
                elif isinstance(item, Potion):                    
                    if item.type == "Strength":
                        if self.player.encounteredStrengthPotion == False:
                            self.player.encounteredStrengthPotion = True
                            generated_sentence = self.sentence_gen_four(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, N, V, 'GENERIC_POTION_DESCRIPTION', '.', 1)
                            generated_sentence = generated_sentence.replace("potion_type___", item.type)
                            generated_sentence = generated_sentence.replace("color___", "purple")
                            print(generated_sentence)
                            generated_sentence = self.sentence_gen_five(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, N, V, 'STRENGTH_POTION_DESCRIPTION', '?', 1)
                            print(generated_sentence)
                        else:
                            generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, sixgrams_dict, N, V, 'ENCOUNTERED_POTION', '.', 1)
                            generated_sentence = generated_sentence.replace("potion_type___", item.type) 
                            print(generated_sentence)
                            generated_sentence = self.sentence_gen_five(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, N, V, 'POTION_QUESTION', '?', 1)                            
                            print(generated_sentence)
                            #print("Take",item.type,"Potion?")
                    elif item.type == "Health":
                        if self.player.encounteredHealthPotion == False:
                            self.player.encounteredHealthPotion = True
                            generated_sentence = self.sentence_gen_four(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, N, V, 'GENERIC_POTION_DESCRIPTION', '.', 1)
                            generated_sentence = generated_sentence.replace("potion_type___", item.type)                        
                            generated_sentence = generated_sentence.replace("color___", "green")
                            print(generated_sentence)
                            generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, sixgrams_dict, N, V, 'HEALTH_POTION_DESCRIPTION', '?', 1)
                            print(generated_sentence)
                        else:
                            generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, sixgrams_dict, N, V, 'ENCOUNTERED_POTION', '.', 1)
                            generated_sentence = generated_sentence.replace("potion_type___", item.type) 
                            print(generated_sentence)
                            generated_sentence = self.sentence_gen_five(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, N, V, 'POTION_QUESTION', '?', 1)                            
                            print(generated_sentence)
                            #print("Take",item.type,"Potion?")
                    
                playerInput = input("")
                
                if playerInput == "yes":
                    if isinstance(item, Weapon):
                        generated_sentence = self.sentence_gen_five(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, N, V, 'YES_TAKE_WEAPON', '.', 1)
                        generated_sentence = generated_sentence.replace("player_weapon___", self.player.weapon.name.lower())
                        generated_sentence = generated_sentence.replace("chest_weapon___", item.name.lower())
                        print(generated_sentence)
                        self.player.weapon = item
                        if item.name == "Long Sword":
                            generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, sixgrams_dict, N, V, 'TAKE_LONG_SWORD', '.', 1)
                            print(generated_sentence)
                        elif item.name == "Steel Sword":
                            generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, sixgrams_dict, N, V, 'TAKE_STEEL_SWORD', '.', 1)
                            print(generated_sentence)
                        print(self.player.weapon.name, self.player.weapon.minDamage, self.player.weapon.maxDamage)
                    elif isinstance(item, Potion):
                        generated_sentence = self.sentence_gen_five(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, N, V, 'YES_TAKE_ITEM', '.', 1)
                        generated_sentence = generated_sentence.replace("chest_item___", item.type + " Potion")
                        print(generated_sentence)
                        self.player.inventory.append(item)
                    itemsToRemove.append(item)
                elif playerInput == "no":
                    generated_sentence = self.sentence_gen_five(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, N, V, 'NO', '.', 1)
                    if isinstance(item, Weapon):
                        generated_sentence = generated_sentence.replace("chest_item___", item.name)
                    elif isinstance(item, Potion):
                        generated_sentence = generated_sentence.replace("chest_item___", item.type + " Potion")
                    print(generated_sentence)
                else:
                    generated_sentence = self.sentence_gen_five(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, N, V, 'INAPPROPRIATE', '.', 2)
                    print(generated_sentence)
            
            for item in itemsToRemove:
                chest.items.remove(item)
                    
            if not chest.items:
                generated_sentence = self.sentence_gen_five(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, N, V, 'EMPTIED_CHEST', '?', 1)                
                print(generated_sentence)
                print("\n")
                break
            
            print("Leave non-empty chest?")
            playerInput = input("")
            if playerInput == "yes":
                generated_sentence = self.sentence_gen_five(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, N, V, 'YES_LEAVE_CHEST', '?', 1)
                print(generated_sentence)
                print("\n")
                break
        
        x = self.currentRoom[0]
        y = self.currentRoom[1]
        self.state = "Move"
        if self.dungeon[x][y].walls == 7:
            generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict,  sixgrams_dict, N, V, 'ROOM_MOVE1', '.', 1)
            generated_sentence = generated_sentence.replace("direction___", "up")
            print(generated_sentence)
        elif self.dungeon[x][y].walls == 11:
            generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict,  sixgrams_dict, N, V, 'ROOM_MOVE1', '.', 1)
            generated_sentence = generated_sentence.replace("direction___", "right")
            print(generated_sentence)
        elif self.dungeon[x][y].walls == 13:
            generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict,  sixgrams_dict, N, V, 'ROOM_MOVE1', '.', 1)
            generated_sentence = generated_sentence.replace("direction___", "down")
            print(generated_sentence)
        elif self.dungeon[x][y].walls == 14:
            generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict,  sixgrams_dict, N, V, 'ROOM_MOVE1', '.', 1)
            generated_sentence = generated_sentence.replace("direction___", "left")
            print(generated_sentence)
        elif self.dungeon[x][y].walls == 3:
            generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict,  sixgrams_dict, N, V, 'ROOM_MOVE2', '.', 1)
            generated_sentence = generated_sentence.replace("direction1___", "right")
            generated_sentence = generated_sentence.replace("direction2___", "up")
            print(generated_sentence)
        elif self.dungeon[x][y].walls == 5:
            generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict,  sixgrams_dict, N, V, 'ROOM_MOVE2', '.', 1)
            generated_sentence = generated_sentence.replace("direction1___", "down")
            generated_sentence = generated_sentence.replace("direction2___", "up")
            print(generated_sentence)
        elif self.dungeon[x][y].walls == 6:
            generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, sixgrams_dict, N, V, 'ROOM_MOVE2', '.', 1)
            generated_sentence = generated_sentence.replace("direction1___", "left")
            generated_sentence = generated_sentence.replace("direction2___", "up")
            print(generated_sentence)
        elif self.dungeon[x][y].walls == 9:
            generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, sixgrams_dict, N, V, 'ROOM_MOVE2', '.', 1)
            generated_sentence = generated_sentence.replace("direction1___", "down")
            generated_sentence = generated_sentence.replace("direction2___", "right")
            print(generated_sentence)
        elif self.dungeon[x][y].walls == 10:
            generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, sixgrams_dict, N, V, 'ROOM_MOVE2', '.', 1)
            generated_sentence = generated_sentence.replace("direction1___", "left")
            generated_sentence = generated_sentence.replace("direction2___", "right")
            print(generated_sentence)
        elif self.dungeon[x][y].walls == 12:
            generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, sixgrams_dict, N, V, 'ROOM_MOVE2', '.', 1)
            generated_sentence = generated_sentence.replace("direction1___", "left")
            generated_sentence = generated_sentence.replace("direction2___", "down")
            print(generated_sentence)
        elif self.dungeon[x][y].walls == 1:
            generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, sixgrams_dict, N, V, 'ROOM_MOVE3', '.', 1)
            generated_sentence = generated_sentence.replace("direction1___", "down")
            generated_sentence = generated_sentence.replace("direction2___", "right")
            generated_sentence = generated_sentence.replace("direction3___", "up")
            print(generated_sentence)
        elif self.dungeon[x][y].walls == 2:
            generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, sixgrams_dict, N, V, 'ROOM_MOVE3', '.', 1)
            generated_sentence = generated_sentence.replace("direction1___", "left")
            generated_sentence = generated_sentence.replace("direction2___", "right")
            generated_sentence = generated_sentence.replace("direction3___", "up")
            print(generated_sentence)
        elif self.dungeon[x][y].walls == 4:
            generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, sixgrams_dict, N, V, 'ROOM_MOVE3', '.', 1)
            generated_sentence = generated_sentence.replace("direction1___", "left")
            generated_sentence = generated_sentence.replace("direction2___", "down")
            generated_sentence = generated_sentence.replace("direction3___", "up")
            print(generated_sentence)
        elif self.dungeon[x][y].walls == 8:
            generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, sixgrams_dict, N, V, 'ROOM_MOVE3', '.', 1)
            generated_sentence = generated_sentence.replace("direction1___", "left")
            generated_sentence = generated_sentence.replace("direction2___", "down")
            generated_sentence = generated_sentence.replace("direction3___", "right")
            print(generated_sentence)
        
    def endgame(self):
        monster = self.dungeon[4][4].contents
        
        if self.difficulty == "Hard":
            monsterAbilities = [Ability("ice shards", 3, 5, 1, 2, 0),
                          Ability("frostbite", 10, 15, 1, 4, 0),
                          Ability("lifesteal", 20, 30, 1, 4, 0)]
        else:
            monsterAbilities = [Ability("ice shards", 3, 5, 1, 2, 0),
                          Ability("frostbite", 10, 15, 1, 4, 0),
                          Ability("lifesteal", 20, 30, 1, 4, 0)]
        
        gotFrostbite = False
        frostbiteDamage = 0
        
        while 0 < self.player.health and 0 < monster.health:
            print("\n")
            print("Player's health:", self.player.health, "\nEnemy's health:", monster.health)
            print("\n")
            playerInput = input("")
            parser = self.inputParser(playerInput)
            
            #random.choices(["attack", "ice shards", "frostbite", "lifesteal"], weights=[0.5, 0.3, 0.1, 0.1], k=1)[0]
            
            if "attack" in self.dictionary.get(parser["Action"], [""]):
                if parser["Direct Object"] is None or any(word in self.dictionary.get(parser["Direct Object"], [""]) for word in ("monster", "enemy")):
                    #Player move
                    playerDamage = random.randint(self.player.weapon.minDamage, self.player.weapon.maxDamage) + self.player.strength
                    if random.random() < self.player.weapon.criticalChance:
                        generated_sentence = self.sentence_gen_five(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, N, V, 'ATTACK', '.', 1)
                        generated_sentence = generated_sentence.replace("weapon_name___", game.player.weapon.name.lower())
                        generated_sentence = generated_sentence.replace("damage_type___", "critical damage")
                        print(generated_sentence)
                        #print("Player Critical!")
                        playerDamage = int(playerDamage * self.player.weapon.critical)
                        #crit_damage = int(base_damage * crit_multiplier)
                    else:
                        generated_sentence = self.sentence_gen_five(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, N, V, 'ATTACK', '.', 1)
                        generated_sentence = generated_sentence.replace("weapon_name___", game.player.weapon.name.lower())
                        generated_sentence = generated_sentence.replace("damage_type___", "regular damage")
                        print(generated_sentence)
                    #print("Player Damage:",playerDamage)
                    monster.health -= int(playerDamage * 0.75)
                    
                    if gotFrostbite:
                        print("Frostbite takes effect.")
                        self.player.health -= frostbiteDamage
                        frostbiteDamage -= 1
                        if frostbiteDamage == 0:
                            gotFrostbite = False
                        if self.player.health <= 0:
                            generated_sentence = self.sentence_gen_five(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, N, V, 'FROSTBITE_DEFEAT', '.', 1)
                            print(generated_sentence)
                            #print("You died. Game Over!")
                            self.state = "Game Over"
                            self.running = False
                            break
                    if self.player.abilities[0].cooldown > 0:
                        self.player.abilities[0].cooldown -= 1
                        if self.player.abilities[0].cooldown == 0:
                            generated_sentence = self.sentence_gen_five(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, N, V, 'SKILL_USABLE', '.', 1)                            
                            generated_sentence = generated_sentence.replace("skill___", "stun")
                            print(generated_sentence)
                            #print("You can now stun")
                    if self.player.abilities[1].cooldown > 0:
                        self.player.abilities[1].cooldown -= 1
                        if self.player.abilities[1].cooldown == 0:
                            generated_sentence = self.sentence_gen_five(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, N, V, 'SKILL_USABLE', '.', 1)                            
                            generated_sentence = generated_sentence.replace("skill___", "fireball")
                            print(generated_sentence)
                            #print("You can now fireball")
                    
                    if monster.health <= 0:
                        generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, sixgrams_dict, N, V, 'MONSTER_DEFEATED', '.', 3)
                        print(generated_sentence)
                        #print("Enemy defeated! You escaped the dungeon!")
                        generated_sentence = self.sentence_gen_five(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, N, V, 'GAME_COMPLETED', '.', 1)
                        print(generated_sentence)
                        self.state = "Game Over"
                        self.running = False
                        break
                    
                    print("\n")
                    #Monster move
                    if self.player.dodge > 0 and random.random() <= self.player.dodge:
                        generated_phrase1 = self.sentence_gen_five(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, N, V, 'MONSTER_ATTACK_PART1', '@@', 1)
                        generated_phrase1 = generated_phrase1.replace("monster_weapon___", monster.weapon.name.lower())
                        generated_phrase1 = generated_phrase1.replace("@@", "")
                        generated_phrase2 = self.sentence_gen_five(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, N, V, 'MONSTER_ATTACK_DODGE', '.', 1)                            
                        generated_sentence = generated_phrase1 + generated_phrase2
                        print(generated_sentence)
                        #print("Dodge. No damage taken")
                        generated_sentence = self.sentence_gen_five(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, N, V, 'PLAYER_NOT_HIT', '?', 1)
                        generated_sentence = generated_sentence.replace("monster_type___", monster.mType)
                        print(generated_sentence)
                        generated_sentence = self.sentence_gen_five(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, N, V, 'MONSTER_LEARNING', '.', 2)
                        print(generated_sentence)                        
                        #print("Boss is learning your dodging")
                        self.player.dodge -= 0.05
                            
                        if self.player.dodge == 0:
                            print("Can't dodge now. Boss has learned your moves and can predict how you dodge.")
                    else:
                        activeAbilities = ["attack"]
                        probAbilities = [1]
                        
                        if monsterAbilities[0].cooldown == 0:
                            activeAbilities.append(monsterAbilities[0].name)
                            probAbilities.append(0.3)
                            probAbilities[0] -= 0.3
                            
                        if monsterAbilities[1].cooldown == 0:
                            if self.difficulty == "Hard":
                                activeAbilities.append(monsterAbilities[1].name)
                                probAbilities.append(0.2)
                                probAbilities[0] -= 0.2
                            else:
                                activeAbilities.append(monsterAbilities[1].name)
                                probAbilities.append(0.1)
                                probAbilities[0] -= 0.1
                        
                        if monsterAbilities[2].cooldown == 0:
                            activeAbilities.append(monsterAbilities[2].name)
                            probAbilities.append(0.1)
                            probAbilities[0] -= 0.1
                        
                        monsterAction = random.choices(activeAbilities, weights=probAbilities, k=1)[0]
                        
                        if monsterAction == "attack":
                            generated_phrase1 = self.sentence_gen_five(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, N, V, 'MONSTER_ATTACK_P1', '@@', 1)
                            generated_phrase1 = generated_phrase1.replace("monster_weapon___", monster.weapon.name.lower())
                            generated_phrase1 = generated_phrase1.replace("@@", "")
                            enemyDamage = random.randint(monster.weapon.minDamage, monster.weapon.maxDamage)
                            if random.random() < monster.weapon.criticalChance:
                                generated_phrase2 = self.sentence_gen_five(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, N, V, 'MONSTER_ATTACK_HIT', '.', 1)                                
                                generated_phrase2 = generated_phrase2.replace("monster_damage_type___", "critical damage")
                                generated_sentence = generated_phrase1 + generated_phrase2
                                print(generated_sentence)
                                #print("Monster Critical!")
                                enemyDamage = int(enemyDamage * monster.weapon.critical)
                            else:
                                generated_phrase2 = self.sentence_gen_five(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, N, V, 'MONSTER_ATTACK_HIT', '.', 1)                                
                                generated_phrase2 = generated_phrase2.replace("monster_damage_type___", "regular damage")
                                generated_sentence = generated_phrase1 + generated_phrase2
                                print(generated_sentence)
                            #print("Enemy Damage:",enemyDamage)
                            self.player.health -= enemyDamage
                        elif monsterAction == "ice shards":
                            totalDamage = 0
                            generated_sentence = self.sentence_gen_five(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, N, V, 'MONSTER_ICESHARDS', '.', 1)
                            print(generated_sentence)
                            for i in range(random.randint(3, 5)):
                                if self.difficulty == "Hard":
                                    enemyDamage = random.randint(monsterAbilities[0].minDamage*2, monsterAbilities[0].maxDamage*2)
                                else:
                                    enemyDamage = random.randint(monsterAbilities[0].minDamage, monsterAbilities[0].maxDamage)
                                #print(enemyDamage, end=" ")
                                totalDamage += enemyDamage
                            #print("\ntotalDamage", totalDamage)
                            #print("You got hit by multiple ice shards")
                            self.player.health -= totalDamage
                            monsterAbilities[0].cooldown = monsterAbilities[0].refreshRate+1
                        elif monsterAction == "frostbite":                            
                            generated_sentence = self.sentence_gen_five(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, N, V, 'MONSTER_FROSTBITE', '.', 1)
                            print(generated_sentence)
                            enemyDamage = random.randint(monsterAbilities[1].minDamage*2, monsterAbilities[1].maxDamage*2)
                            #print("Enemy Damage:",enemyDamage)
                            self.player.health -= enemyDamage
                            
                            print("Got hit by an ice attack. Now you have frostbite")
                            if self.difficulty == "Hard":
                                frostbiteDamage = random.randint(int(monsterAbilities[1].minDamage*2), int(monsterAbilities[1].maxDamage*2)) 
                            else:
                                frostbiteDamage = random.randint(int(monsterAbilities[1].minDamage/3), int(monsterAbilities[1].maxDamage/3))
                            gotFrostbite = True
                            monsterAbilities[1].cooldown = monsterAbilities[1].refreshRate+1
                        elif monsterAction == "lifesteal":                            
                            generated_sentence = self.sentence_gen_five(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, N, V, 'MONSTER_LIFESTEAL', '.', 1)
                            print(generated_sentence)
                            enemyDamage = random.randint(monsterAbilities[2].minDamage, monsterAbilities[2].maxDamage)
                            print("Your loss is his gain.", end=" ")
                            print("You lose",enemyDamage,"and he heals",enemyDamage,end=". ")
                            self.player.health -= enemyDamage
                            monster.health += enemyDamage
                            monsterAbilities[2].cooldown = monsterAbilities[2].refreshRate+1
                        if self.player.health > 0:
                            generated_sentence = self.sentence_gen_four(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, N, V, 'PLAYER_HIT', '?', 1)                        
                            print(generated_sentence)
                    
                    if monsterAbilities[0].cooldown > 0:
                        monsterAbilities[0].cooldown -= 1
                    if monsterAbilities[1].cooldown > 0:
                        monsterAbilities[1].cooldown -= 1
                    if monsterAbilities[2].cooldown > 0:
                        monsterAbilities[2].cooldown -= 1
                        
                    if self.player.health <= 0:
                        generated_sentence = self.sentence_gen_five(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, N, V, 'PLAYER_DEFEATED', '.', 1)
                        print(generated_sentence)
                        #print("You died. Game Over!")
                        self.state = "Game Over"
                        self.running = False
                        break
            elif any(word in self.dictionary.get(parser["Action"], [""]) for word in ("use", "drink")) and parser["Direct Object"] != None:
                if len((parser["Direct Object"] or "").split()) == 2 and "potion" in self.dictionary.get(parser["Direct Object"].split()[-1], [""]):
                    if "healing" in self.dictionary.get(parser["Direct Object"].split()[0], [""]):
                        #print("Use health potion?")
                        health_potions = [item for item in self.player.inventory if isinstance(item, Potion) and item.type == "Health"]
                        if health_potions:
                            #print("Yes!")
                            before_health = self.player.health                            
                            health_potions[0].use(self.player)                            
                            self.player.inventory.remove(health_potions[0])
                            after_health = self.player.health
                            if after_health > before_health and self.player.health == self.player.maxHealth:
                                generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, sixgrams_dict, N, V, 'HEALTHPOTION', '.', 3)
                                print(generated_sentence)
                                generated_sentence = self.sentence_gen_five(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, N, V, 'HEALTHPOTION_MAXHEALTH', '?', 1)
                                print(generated_sentence)
                            else:
                                generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, sixgrams_dict, N, V, 'HEALTHPOTION', '?', 1)
                                print(generated_sentence)
                            
                            if monsterAbilities[0].cooldown > 0:
                                monsterAbilities[0].cooldown -= 1
                            if monsterAbilities[1].cooldown > 0:
                                monsterAbilities[1].cooldown -= 1
                            if monsterAbilities[2].cooldown > 0:
                                monsterAbilities[2].cooldown -= 1
                        else:
                            #print("No")
                            generated_sentence = self.sentence_gen_five(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, N, V, 'POTION_FAIL', '.', 1)
                            generated_sentence = generated_sentence.replace("type___", "health")
                            print(generated_sentence)  
                        
                        if monster.isStuned:
                            print("Monster is no longer stunned")
                            monster.isStuned = False
                    elif "strength" in self.dictionary.get(parser["Direct Object"].split()[0], [""]):
                        #print("Use strength potion?")
                        strength_potions = [item for item in self.player.inventory if isinstance(item, Potion) and item.type == "Strength"]
                        if strength_potions:
                            #print("Yes!")
                            generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, sixgrams_dict, N, V, 'STRENGTHPOTION', '?', 1)
                            print(generated_sentence) 
                            strength_potions[0].use(self.player)
                            self.player.inventory.remove(strength_potions[0])
                            
                            if monsterAbilities[0].cooldown > 0:
                                monsterAbilities[0].cooldown -= 1
                            if monsterAbilities[1].cooldown > 0:
                                monsterAbilities[1].cooldown -= 1
                            if monsterAbilities[2].cooldown > 0:
                                monsterAbilities[2].cooldown -= 1
                        else:
                            #print("No")
                            generated_sentence = self.sentence_gen_five(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, N, V, 'POTION_FAIL', '.', 1)
                            generated_sentence = generated_sentence.replace("type___", "strength")
                            print(generated_sentence)
            elif "run" in self.dictionary.get(parser["Action"], [""]):
                #print("Can't run away. The monster has blocked your path")
                generated_sentence = self.sentence_gen_five(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, N, V, 'RUN_FAIL', '.', 2)
                print(generated_sentence)                
            elif "show" in self.dictionary.get(parser["Action"], [""]) and parser["Direct Object"] != None:
                if "health" in self.dictionary.get(parser["Direct Object"].split()[-1], [""]):
                    generated_sentence = self.sentence_gen_five(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, N, V, 'SHOW_HEALTH', '.', 1)
                    generated_sentence = generated_sentence.replace("health___", str(self.player.health))
                    print(generated_sentence)                    
                    #print("Health:", self.player.health)
                elif "inventory" in self.dictionary.get(parser["Direct Object"].split()[-1], [""]):                    
                    if self.player.inventory:
                        generated_sentence = self.sentence_gen_four(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, N, V, 'SHOW_INVENTORY', '.', 1)
                        print(generated_sentence)
                        for item in self.player.inventory:
                            print(item.type,"Potion")
                    else:
                        generated_sentence = self.sentence_gen_five(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, N, V, 'NO_ITEMS', '.', 1)
                        print(generated_sentence)
                        #print("No items")
            elif "stun" in self.dictionary.get(parser["Action"], [""]):
                if parser["Direct Object"] is None or any(word in self.dictionary.get(parser["Direct Object"], [""]) for word in ("monster", "enemy")):
                    stun = self.player.abilities[0]
                    if stun.cooldown == 0:
                        generated_sentence = self.sentence_gen_five(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, N, V, 'STUN_ATTEMPT', '.', 1)
                        print(generated_sentence)
                        playerDamage = random.randint(stun.minDamage, stun.maxDamage)
                        generated_sentence = self.sentence_gen_five(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, N, V, 'STUN_ATTEMPT_BOSS', '.', 1)
                        print(generated_sentence)
                        generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, sixgrams_dict, N, V, 'STUN_DAMAGE_BOSS', '.', 1)
                        print(generated_sentence)
                        print("Player Stun Damage:",playerDamage)
                        monster.health -= playerDamage
                        #print("stun attack doesn't work")                        
                        stun.cooldown = stun.refreshRate
                        
                        if monster.health <= 0:
                            generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, sixgrams_dict, N, V, 'MONSTER_DEFEATED', '.', 3)
                            print(generated_sentence)
                            #print("Enemy defeated! You escaped the dungeon!")
                            generated_sentence = self.sentence_gen_five(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, N, V, 'GAME_COMPLETED', '.', 1)
                            print(generated_sentence)
                            self.state = "Game Over"
                            self.running = False
                            break
                        generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, sixgrams_dict, N, V, 'GENERAL_QUESTION', '?', 1)
                        print(generated_sentence)
                        
                    else:
                        generated_sentence = self.sentence_gen_five(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, N, V, 'SKILL_FAIL', '.', 1)
                        generated_sentence = generated_sentence.replace("skill___", "stun")
                        print(generated_sentence)
                        #print("Can't stun now")
                    
                    if monsterAbilities[0].cooldown > 0:
                        monsterAbilities[0].cooldown -= 1
                    if monsterAbilities[1].cooldown > 0:
                        monsterAbilities[1].cooldown -= 1
                    if monsterAbilities[2].cooldown > 0:
                        monsterAbilities[2].cooldown -= 1
            elif "cast" in self.dictionary.get(parser["Action"], [""]) and "fireball" in self.dictionary.get(parser["Direct Object"], [""]):
                fireball = self.player.abilities[1]
                if fireball.cooldown == 0:
                    generated_sentence = self.sentence_gen_five(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, N, V, 'FIREBALL_ATTEMPT', '.', 1)
                    print(generated_sentence)
                    if random.random() < fireball.chance:
                        generated_sentence = self.sentence_gen_five(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, N, V, 'FIREBALL_ATTEMPT_SUCCESS', '.', 1)
                        print(generated_sentence)
                        #print("enemy fireballed")
                        playerDamage = random.randint(fireball.minDamage, fireball.maxDamage)
                        print("Player Fireball Damage:",playerDamage)
                        monster.health -= playerDamage
                        
                        if monster.health <= 0:
                            generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, sixgrams_dict, N, V, 'MONSTER_DEFEATED', '.', 3)
                            print(generated_sentence)                            
                            #print("Enemy defeated! You escaped the dungeon!")
                            generated_sentence = self.sentence_gen_five(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, N, V, 'GAME_COMPLETED', '.', 1)
                            print(generated_sentence)
                            self.state = "Game Over"
                            self.running = False
                            break
                    else:
                        generated_sentence = self.sentence_gen_five(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, N, V, 'FIREBALL_ATTEMPT_FAIL', '.', 1)
                        print(generated_sentence)
                        #print("didn't hit enemy")
                        
                    if gotFrostbite:
                        generated_sentence = self.sentence_gen_five(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, N, V, 'FROSTBITE_CURE', '.', 1)
                        print(generated_sentence)
                        #print("Using fireball removed inflicted frostbite")
                        gotFrostbite = False
                        frostbiteDamage = 0
                    generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, sixgrams_dict, N, V, 'GENERAL_QUESTION', '?', 1)
                    print(generated_sentence)
                    fireball.cooldown = fireball.refreshRate
                else:
                    generated_sentence = self.sentence_gen_five(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, N, V, 'SKILL_FAIL', '.', 1)
                    generated_sentence = generated_sentence.replace("skill___", "fireball")
                    print(generated_sentence)
                    #print("Can't fireball now")
                    
                if monsterAbilities[0].cooldown > 0:
                    monsterAbilities[0].cooldown -= 1
                if monsterAbilities[1].cooldown > 0:
                    monsterAbilities[1].cooldown -= 1
                if monsterAbilities[2].cooldown > 0:
                    monsterAbilities[2].cooldown -= 1
            else:
                generated_sentence = self.sentence_gen_five(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, N, V, 'INAPPROPRIATE', '.', 2)
                print(generated_sentence)
    
    def typoChecker(self, typo):
        words = list(self.actions | self.prepositions | self.adjectives | self.objects)
        
        word = typo.lower().strip()
        matches = difflib.get_close_matches(word, words, n=1, cutoff=0.75)
        return matches[0] if matches else word
        
    
    def inputParser(self, userInput):
        words = userInput.lower().split()
        inputChecked = [self.typoChecker(word) for word in words]
        userInput = ' '.join(inputChecked)

        # Try to match the longest verb first
        sorted_verbs = sorted(self.actions, key=lambda v: -len(v))
        prsa = None
        for verb in sorted_verbs:
            if userInput.startswith(verb):
                prsa = verb
                userInput = userInput[len(verb):].strip()
                break

        prso = None
        prsi = None
        preposition = None

        # Look for prepositions to split PRSO and PRSI
        for prep in self.prepositions:
            pattern = rf"\b{prep}\b"
            if re.search(pattern, userInput):
                preposition = prep
                parts = userInput.split(prep, 1)
                prso_part = parts[0].strip()
                prsi_part = parts[1].strip()
                break
            else:
                prso_part = userInput.strip()
                prsi_part = None

        # Match object first, then adjectives around it
        def match_object(text):
            text = text.strip()
            for obj in sorted(self.objects, key=lambda o: -len(o)):
                if obj in text:
                    # Find adjectives near the object
                    words = text.split()
                    obj_words = obj.split()
                    obj_start = None

                    # Try to locate the object in the word list
                    for i in range(len(words) - len(obj_words) + 1):
                        if words[i:i+len(obj_words)] == obj_words:
                            obj_start = i
                            break

                    adjectives_found = []
                    if obj_start is not None:
                        # Look at words before the object for adjectives
                        for word in words[:obj_start]:
                            if word in self.adjectives:
                                adjectives_found.append(word)
                        # Look at words after object for post-modifiers (less common)
                        for word in words[obj_start + len(obj_words):]:
                            if word in self.adjectives:
                                adjectives_found.append(word)

                    return " ".join(adjectives_found), obj
            return None, text  # Fallback if no object is found

        # Parse the direct and indirect objects
        if prso_part:
            adj, prso = match_object(prso_part)
            if adj:
                prso = f"{adj} {prso}"
        if prsi_part:
            adj, prsi = match_object(prsi_part)
            if adj:
                prsi = f"{adj} {prsi}"

        #print({"Action": prsa, "Direct Object": prso, "Indirect Object": prsi})

        return {
            "Action": prsa,
            "Direct Object": prso,
            "Indirect Object": prsi
        }
    
            
    
    def play(self):
        print("Please select a difficulty level for the game. You have the following options:")
        print("normal")
        print("hard")
        print("\n")
        playerInput = input("")
        
        while playerInput.lower() != "normal" and playerInput.lower() != "hard":
            print("Please type one of the following options:")
            print("normal")
            print("hard")
            playerInput = input("")      
        
        if playerInput.lower() == "normal":
            self.difficulty = "Normal"
        elif playerInput.lower() == "hard":
            self.difficulty = "Hard"
            self.hard_mode_changes()
        
        print("\n")
        print("Welcome to the game. Your goal is to escape the dungeon.")
        generated_sentence = self.sentence_gen_five(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, N, V, 'GAME_START', '.', 1)
        print(generated_sentence)
        self.state = "Move"
        generated_sentence = self.sentence_gen_six(unigrams_dict, bigrams_dict, trigrams_dict, fourgrams_dict, fivegrams_dict, sixgrams_dict, N, V, 'ROOM_MOVE2', '.', 1)
        generated_sentence = generated_sentence.replace("direction1___", "down")
        generated_sentence = generated_sentence.replace("direction2___", "right")
        print(generated_sentence)
        
        while self.running:
            #print(self.state)
            
            if self.state == "Move":
                self.move()
            elif self.state == "Endgame":
                result = self.endgame()
            elif self.state == "Fight":
                x,y = self.currentRoom
                self.fight(self.dungeon[x][y].contents)
            elif self.state == "Inspect":
                x,y = self.currentRoom
                self.inspect(self.dungeon[x][y].contents)
            elif self.state == "Game Over":
                break
            
        return 0
    

if __name__ == "__main__":
    game = Game()
    game.play()
    
    
    
    
    
    
    
    
    
    
    
    
    

