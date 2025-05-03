import spacy
from collections import Counter
import random
import math
import re
import operator
import difflib

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
    
    def nextRoom(self, lastRoom):
        print("next")


class Chest:
    def __init__(self, items=None):
        if items == None:
            self.items = []
        else:
            self.items = items
        

class Monster:
    def __init__(self,weapon=None,armor=None,health=None, dodge=None):
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
                
                #"withdraw": ["run"]
            }
        
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
        matrix[0][1].contents = Monster(Weapon("Fists", 6, 10, 0.25, 1.15), None, 50, 0.2)
        matrix[1][0].contents = Monster(Weapon("Fists", 8, 12, 0.25, 1.15), None, 70, 0.25)
        matrix[3][2].contents = Monster(Weapon("Sword", 10, 15, 0.4, 1.25), None, 80, 0.25)
        matrix[0][2].contents = Monster(Weapon("Sword", 10, 15, 0.4, 1.25), None, 85, 0.25)
        matrix[3][3].contents = Monster(Weapon("Long Sword", 13, 20, 0.45, 1.4), None, 90, 0.35)
        matrix[1][4].contents = Monster(Weapon("Long Sword", 15, 20, 0.45, 1.45), None, 100, 0.4)
        matrix[4][2].contents = Monster(Weapon("Sword", 10, 15, 0.4, 1.25), None, 70, 0.5)
        matrix[4][4].contents = Monster(Weapon("Steel Sword", 20, 30, 0.55, 1.5), None, 150, 0.4)
        
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
    
    def generate_map(self):
    
        print("Traveled Map:")
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
    
    
    def moving(self, direction):
        x = self.currentRoom[0]
        y = self.currentRoom[1]
        
        maxX = len(self.dungeon)-1
        maxY = len(self.dungeon[x])-1
        
        if direction == "up":
            if not self.dungeon[x][y].wall("n"):
                x -= 1
                self.dungeon[x][y].visited = True;
        elif direction == "down":
            if not self.dungeon[x][y].wall("s"):
                x += 1
                self.dungeon[x][y].visited = True;
        elif direction == "right":
            if not self.dungeon[x][y].wall("e"):
                y += 1
                self.dungeon[x][y].visited = True;
        elif direction == "left":
            if not self.dungeon[x][y].wall("w"):
                y -= 1
                self.dungeon[x][y].visited = True;
            
        #print((x,y))
        if self.currentRoom != (x,y):
            self.lastRoom = self.currentRoom
            self.currentRoom = (x,y)
            
            if self.dungeon[x][y].type == "End":
                self.state = "Endgame"
            elif isinstance(self.dungeon[x][y].contents, Monster):
                self.state = "Fight"
            elif isinstance(self.dungeon[x][y].contents, Chest):
                self.state = "Inspect"
                
    def nextRoom(self):
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
        
        if newDoors == 8:
            self.moving("up")
        elif newDoors == 4:
            self.moving("right")
        elif newDoors == 2:
            self.moving("down")
        elif newDoors == 1:
            self.moving("left")

        
                
    def move(self):
        playerInput = input("")
        parser = self.inputParser(playerInput)
        if "movement" in self.dictionary.get(parser["Action"], [""]):
            if parser["Direct Object"]:
                if len(parser["Direct Object"].split()) == 1:
                    if set(self.dictionary.get(parser["Direct Object"], [""])) & set(self.dictionary['direction']):
                        self.moving(self.dictionary[parser["Direct Object"]][0])
                    elif "next" in self.dictionary.get(parser["Direct Object"], [""]) and self.lastRoom is not None:
                        self.nextRoom()
            elif parser["Indirect Object"]:
                if any(word in self.dictionary.get(parser["Indirect Object"].split()[-1], [""]) for word in ("room", "door")):
                    if set(self.dictionary.get(parser["Indirect Object"].split()[0], [""])) & set(self.dictionary['direction']):
                        self.moving(self.dictionary[parser["Indirect Object"].split()[0]][0])
                    elif "next" in self.dictionary.get(parser["Indirect Object"].split()[0], [""]) and self.lastRoom is not None:
                        self.nextRoom()
                elif set(self.dictionary.get(parser["Indirect Object"].split()[-1], [""])) & set(self.dictionary['direction']):
                    self.moving(self.dictionary[parser["Indirect Object"].split()[-1]][0])
                elif "next" in self.dictionary.get(parser["Indirect Object"].split()[0], [""]) and self.lastRoom is not None:
                    self.nextRoom()
        elif "look" in self.dictionary.get(parser["Action"], [""]) and any("map" in self.dictionary.get(parser[obj], [""]) for obj in ["Direct Object", "Indirect Object"]):
            self.generate_map()
        elif any(word in self.dictionary.get(parser["Action"], [""]) for word in ("look", "open")) and any("chest" in self.dictionary.get(parser[obj], [""]) for obj in ["Direct Object", "Indirect Object"]):
            x,y = self.currentRoom
            if isinstance(self.dungeon[x][y].contents, Chest):
                print("chest to inspect")
                self.state = "Inspect"
            else:
                print("no chest")
        elif any(word in self.dictionary.get(parser["Action"], [""]) for word in ("use", "drink")):
            if len(parser["Direct Object"].split()) == 2 and "potion" in self.dictionary.get(parser["Direct Object"].split()[-1], [""]):
                if "healing" in self.dictionary.get(parser["Direct Object"].split()[0], [""]):
                    print("Use health potion?")
                    health_potions = [item for item in self.player.inventory if isinstance(item, Potion) and item.type == "Health"]
                    if health_potions:
                        print("Yes!")
                        health_potions[0].use(self.player)
                        self.player.inventory.remove(health_potions[0])
                    else:
                        print("No")
                elif "strength" in self.dictionary.get(parser["Direct Object"].split()[0], [""]):
                    print("Use strength potion?")
                    strength_potions = [item for item in self.player.inventory if isinstance(item, Potion) and item.type == "Strength"]
                    if strength_potions:
                        print("Yes!")
                        strength_potions[0].use(self.player)
                        self.player.inventory.remove(strength_potions[0])
                    else:
                        print("No")
        elif "show" in self.dictionary.get(parser["Action"], [""]):
            if "health" in self.dictionary.get(parser["Direct Object"].split()[-1], [""]):
                print("Health:", self.player.health)
            elif "inventory" in self.dictionary.get(parser["Direct Object"].split()[-1], [""]):
                if self.player.inventory:
                    for item in self.player.inventory:
                        print(item.type,"Potion")
                else:
                    print("No items")
        
        
    def fight(self, monster):
        while 0 < self.player.health and 0 < monster.health:
            print(self.player.health, monster.health)
            playerInput = input("")
            parser = self.inputParser(playerInput)
            
            if "attack" in self.dictionary.get(parser["Action"], [""]):
                if parser["Direct Object"] is None or any(word in self.dictionary.get(parser["Direct Object"], [""]) for word in ("monster", "enemy")):
                    #Player move
                    playerDamage = random.randint(self.player.weapon.minDamage, self.player.weapon.maxDamage) + self.player.strength
                    if random.random() < self.player.weapon.criticalChance:
                        print("Player Critcal!")
                        playerDamage = int(playerDamage * self.player.weapon.critical)
                        #crit_damage = int(base_damage * crit_multiplier)
                    print("Player Damage:",playerDamage)
                    monster.health -= playerDamage
                    
                    if monster.health <= 0:
                        print("Enemy defeated!")
                        x,y = self.currentRoom
                        self.dungeon[x][y].contents = None
                        for ability in self.player.abilities:
                            ability.cooldown = 0
                        self.state = "Move"
                        break
                    
                    #Monster move
                    if monster.isStuned:
                        print("Monster is no logner stunned")
                        monster.isStuned = False
                    else:
                        if random.random() <= self.player.dodge:
                            print("Dodge. No damage taken")
                        else:
                            enemyDamage = random.randint(monster.weapon.minDamage, monster.weapon.maxDamage)
                            if random.random() < monster.weapon.criticalChance:
                                print("Monster Critcal!")
                                enemyDamage = int(enemyDamage * monster.weapon.critical)
                            print("Enemy Damage:",enemyDamage)
                            self.player.health -= enemyDamage
                        
                        if self.player.health <= 0:
                            print("Game Over!")
                            self.state = "Game Over"
                            self.running = False
                            break
                        
                    if self.player.abilities[0].cooldown > 0:
                        self.player.abilities[0].cooldown -= 1
                        if self.player.abilities[0].cooldown == 0:
                            print("You can now stun")
                    if self.player.abilities[1].cooldown > 0:
                        self.player.abilities[1].cooldown -= 1
                        if self.player.abilities[1].cooldown == 0:
                            print("You can now fireball")
            
            elif any(word in self.dictionary.get(parser["Action"], [""]) for word in ("use", "drink")):
                if len((parser["Direct Object"] or "").split()) == 2 and "potion" in self.dictionary.get(parser["Direct Object"].split()[-1], [""]):
                    if "healing" in self.dictionary.get(parser["Direct Object"].split()[0], [""]):
                        print("Use health potion?")
                        health_potions = [item for item in self.player.inventory if isinstance(item, Potion) and item.type == "Health"]
                        if health_potions:
                            print("Yes!")
                            health_potions[0].use(self.player)
                            self.player.inventory.remove(health_potions[0])
                        else:
                            print("No")
                        
                        if monster.isStuned:
                            print("Monster is no logner stunned")
                            monster.isStuned = False
                    elif "strength" in self.dictionary.get(parser["Direct Object"].split()[0], [""]):
                        print("Use strength potion?")
                        strength_potions = [item for item in self.player.inventory if isinstance(item, Potion) and item.type == "Strength"]
                        if strength_potions:
                            print("Yes!")
                            strength_potions[0].use(self.player)
                            self.player.inventory.remove(strength_potions[0])
                        else:
                            print("No")
                        
                        if monster.isStuned:
                            print("Monster is no logner stunned")
                            monster.isStuned = False
            elif "run" in self.dictionary.get(parser["Action"], [""]):
                oldRoom = self.currentRoom
                self.currentRoom = self.lastRoom
                self.lastRoom = oldRoom
                monster.isStuned = False
                self.state = "Move"
                break
            elif "show" in self.dictionary.get(parser["Action"], [""]):
                if "health" in self.dictionary.get(parser["Direct Object"].split()[-1], [""]):
                    print("Health:", self.player.health)
                elif "inventory" in self.dictionary.get(parser["Direct Object"].split()[-1], [""]):
                    if self.player.inventory:
                        for item in self.player.inventory:
                            print(item.type,"Potion")
                    else:
                        print("No items")
            elif "stun" in self.dictionary.get(parser["Action"], [""]):
                if parser["Direct Object"] is None or any(word in self.dictionary.get(parser["Direct Object"], [""]) for word in ("monster", "enemy")):
                    stun = self.player.abilities[0]
                    if stun.cooldown == 0:
                        if random.random() < stun.chance:
                            print("stunned enemy")
                            playerDamage = random.randint(stun.minDamage, stun.maxDamage)
                            print("Player Stun Damage:",playerDamage)
                            monster.health -= playerDamage
                            monster.isStuned = True
                        else:
                            print("didn't stunned enemy")
                            if monster.isStuned:
                                print("Monster is no logner stunned")
                                monster.isStuned = False
                            else:
                                if random.random() <= self.player.dodge:
                                    print("Dodge. No damage taken")
                                else:
                                    enemyDamage = random.randint(monster.weapon.minDamage, monster.weapon.maxDamage)
                                    if random.random() < monster.weapon.criticalChance:
                                        print("Monster Critcal!")
                                        enemyDamage = int(enemyDamage * monster.weapon.critical)
                                    print("Enemy Damage:",enemyDamage)
                                    self.player.health -= enemyDamage
                                
                                if self.player.health <= 0:
                                    print("Game Over!")
                                    self.state = "Game Over"
                                    self.running = False
                                    break
                        stun.cooldown = stun.refreshRate
                    else:
                        print("Can't stun now")
                        if monster.isStuned:
                            print("Monster is no logner stunned")
                            monster.isStuned = False
            elif "cast" in self.dictionary.get(parser["Action"], [""]) and "fireball" in self.dictionary.get(parser["Direct Object"], [""]):
                fireball = self.player.abilities[1]
                if fireball.cooldown == 0:
                    if random.random() < fireball.chance:
                        print("enemy fireballed")
                        playerDamage = random.randint(fireball.minDamage, fireball.maxDamage)
                        print("Player Fireball Damage:",playerDamage)
                        monster.health -= playerDamage
                    else:
                        print("didn't hit enemy")
                    fireball.cooldown = fireball.refreshRate
                else:
                    print("Can't fireball now")
                
                        
            
            
    def inspect(self, chest):
        while True:
            itemsToRemove = []
            for item in chest.items:
                if isinstance(item, Weapon):
                    print("Take",item.name+"?")
                elif isinstance(item, Potion):
                    print("Take",item.type,"Potion?")
                    
                playerInput = input("")
                
                if playerInput == "yes":
                    if isinstance(item, Weapon):
                        self.player.weapon = item
                        print(self.player.weapon.name, self.player.weapon.minDamage, self.player.weapon.maxDamage)
                    elif isinstance(item, Potion):
                        self.player.inventory.append(item)
                    itemsToRemove.append(item)
            
            for item in itemsToRemove:
                chest.items.remove(item)
                    
            if not chest.items:
                break
            
            print("Leave non-empty chest?")
            playerInput = input("")
            if playerInput == "yes":
                break
        
        self.state = "Move"
        
    def endgame(self):
        monster = self.dungeon[4][4].contents
        
        monsterAbilities = [Ability("ice shards", 3, 5, 1, 2, 0),
                          Ability("frostbite", 10, 15, 1, 4, 0),
                          Ability("lifesteal", 20, 30, 1, 4, 0)]
        
        gotFrostbite = False
        frostbiteDamage = 0
        
        while 0 < self.player.health and 0 < monster.health:
            print(self.player.health, monster.health)
            playerInput = input("")
            parser = self.inputParser(playerInput)
            
            #random.choices(["attack", "ice shards", "frostbite", "lifesteal"], weights=[0.5, 0.3, 0.1, 0.1], k=1)[0]
            
            if "attack" in self.dictionary.get(parser["Action"], [""]):
                if parser["Direct Object"] is None or any(word in self.dictionary.get(parser["Direct Object"], [""]) for word in ("monster", "enemy")):
                    #Player move
                    playerDamage = random.randint(self.player.weapon.minDamage, self.player.weapon.maxDamage) + self.player.strength
                    if random.random() < self.player.weapon.criticalChance:
                        print("Player Critcal!")
                        playerDamage = int(playerDamage * self.player.weapon.critical)
                        #crit_damage = int(base_damage * crit_multiplier)
                    print("Player Damage:",playerDamage)
                    monster.health -= int(playerDamage * 0.75)
                    
                    if gotFrostbite:
                        print("Frostbite takes effect", frostbiteDamage)
                        self.player.health -= frostbiteDamage
                        frostbiteDamage -= 1
                        if frostbiteDamage == 0:
                            gotFrostbite = False
                    
                    if self.player.abilities[0].cooldown > 0:
                        self.player.abilities[0].cooldown -= 1
                        if self.player.abilities[0].cooldown == 0:
                            print("You can now stun")
                    if self.player.abilities[1].cooldown > 0:
                        self.player.abilities[1].cooldown -= 1
                        if self.player.abilities[1].cooldown == 0:
                            print("You can now fireball")
                    
                    if monster.health <= 0:
                        print("Enemy defeated! You escaped the dungeon!")
                        self.state = "Game Over"
                        self.running = False
                        break
                    
                    #Monster move
                    if self.player.dodge > 0 and random.random() <= self.player.dodge:
                        print("Dodge. No damage taken")
                        print("Boss is learning your dodging")
                        self.player.dodge -= 0.05
                            
                        if self.player.dodge == 0:
                            print("Can't dodge now. Boss has learned your moves and can predict how you dodge")
                    else:
                        activeAbilities = ["attack"]
                        probAbilities = [1]
                        
                        if monsterAbilities[0].cooldown == 0:
                            activeAbilities.append(monsterAbilities[0].name)
                            probAbilities.append(0.3)
                            probAbilities[0] -= 0.3
                            
                        if monsterAbilities[1].cooldown == 0:
                            activeAbilities.append(monsterAbilities[1].name)
                            probAbilities.append(0.1)
                            probAbilities[0] -= 0.1
                        
                        if monsterAbilities[2].cooldown == 0:
                            activeAbilities.append(monsterAbilities[2].name)
                            probAbilities.append(0.1)
                            probAbilities[0] -= 0.1
                        
                        monsterAction = random.choices(activeAbilities, weights=probAbilities, k=1)[0]
                        
                        if monsterAction == "attack":
                            enemyDamage = random.randint(monster.weapon.minDamage, monster.weapon.maxDamage)
                            if random.random() < monster.weapon.criticalChance:
                                print("Monster Critcal!")
                                enemyDamage = int(enemyDamage * monster.weapon.critical)
                            print("Enemy Damage:",enemyDamage)
                            self.player.health -= enemyDamage
                        elif monsterAction == "ice shards":
                            totalDamage = 0
                            for i in range(random.randint(3, 5)):
                                enemyDamage = random.randint(monsterAbilities[0].minDamage, monsterAbilities[0].maxDamage)
                                print(enemyDamage, end=" ")
                                totalDamage += enemyDamage
                            print("\ntotalDamage", totalDamage)
                            print("You got hit by multiple ice shards")
                            self.player.health -= totalDamage
                            monsterAbilities[0].cooldown = monsterAbilities[0].refreshRate+1
                        elif monsterAction == "frostbite":
                            enemyDamage = random.randint(monsterAbilities[1].minDamage, monsterAbilities[1].maxDamage)
                            print("Enemy Damage:",enemyDamage)
                            self.player.health -= enemyDamage
                            
                            print("Got hit by an ice attack. Now you have frostbite")
                            frostbiteDamage = random.randint(int(monsterAbilities[1].minDamage/3), int(monsterAbilities[1].maxDamage/3))
                            gotFrostbite = True
                            monsterAbilities[1].cooldown = monsterAbilities[1].refreshRate+1
                        elif monsterAction == "lifesteal":
                            enemyDamage = random.randint(monsterAbilities[2].minDamage, monsterAbilities[2].maxDamage)
                            print("Your loss is his gain")
                            print("You lose",enemyDamage,"and he heals",enemyDamage)
                            self.player.health -= enemyDamage
                            monster.health += enemyDamage
                            monsterAbilities[2].cooldown = monsterAbilities[2].refreshRate+1
                        
                    if monsterAbilities[0].cooldown > 0:
                        monsterAbilities[0].cooldown -= 1
                    if monsterAbilities[1].cooldown > 0:
                        monsterAbilities[1].cooldown -= 1
                    if monsterAbilities[2].cooldown > 0:
                        monsterAbilities[2].cooldown -= 1
                        
                    if self.player.health <= 0:
                        print("You died. Game Over!")
                        self.state = "Game Over"
                        self.running = False
                        break
            elif any(word in self.dictionary.get(parser["Action"], [""]) for word in ("use", "drink")):
                if len((parser["Direct Object"] or "").split()) == 2 and "potion" in self.dictionary.get(parser["Direct Object"].split()[-1], [""]):
                    if "healing" in self.dictionary.get(parser["Direct Object"].split()[0], [""]):
                        print("Use health potion?")
                        health_potions = [item for item in self.player.inventory if isinstance(item, Potion) and item.type == "Health"]
                        if health_potions:
                            print("Yes!")
                            health_potions[0].use(self.player)
                            self.player.inventory.remove(health_potions[0])
                            
                            if monsterAbilities[0].cooldown > 0:
                                monsterAbilities[0].cooldown -= 1
                            if monsterAbilities[1].cooldown > 0:
                                monsterAbilities[1].cooldown -= 1
                            if monsterAbilities[2].cooldown > 0:
                                monsterAbilities[2].cooldown -= 1
                        else:
                            print("No")
                        
                        if monster.isStuned:
                            print("Monster is no logner stunned")
                            monster.isStuned = False
                    elif "strength" in self.dictionary.get(parser["Direct Object"].split()[0], [""]):
                        print("Use strength potion?")
                        strength_potions = [item for item in self.player.inventory if isinstance(item, Potion) and item.type == "Strength"]
                        if strength_potions:
                            print("Yes!")
                            strength_potions[0].use(self.player)
                            self.player.inventory.remove(strength_potions[0])
                            
                            if monsterAbilities[0].cooldown > 0:
                                monsterAbilities[0].cooldown -= 1
                            if monsterAbilities[1].cooldown > 0:
                                monsterAbilities[1].cooldown -= 1
                            if monsterAbilities[2].cooldown > 0:
                                monsterAbilities[2].cooldown -= 1
                        else:
                            print("No")
            elif "run" in self.dictionary.get(parser["Action"], [""]):
                print("Can't run away. The monster has blocked your path")
            elif "show" in self.dictionary.get(parser["Action"], [""]):
                if "health" in self.dictionary.get(parser["Direct Object"].split()[-1], [""]):
                    print("Health:", self.player.health)
                elif "inventory" in self.dictionary.get(parser["Direct Object"].split()[-1], [""]):
                    if self.player.inventory:
                        for item in self.player.inventory:
                            print(item.type,"Potion")
                    else:
                        print("No items")
            elif "stun" in self.dictionary.get(parser["Action"], [""]):
                if parser["Direct Object"] is None or any(word in self.dictionary.get(parser["Direct Object"], [""]) for word in ("monster", "enemy")):
                    stun = self.player.abilities[0]
                    if stun.cooldown == 0:
                        playerDamage = random.randint(stun.minDamage, stun.maxDamage)
                        print("Player Stun Damage:",playerDamage)
                        monster.health -= playerDamage
                        print("stun attack doesn't work")
                        stun.cooldown = stun.refreshRate
                    else:
                        print("Can't stun now")
                    
                    if monsterAbilities[0].cooldown > 0:
                        monsterAbilities[0].cooldown -= 1
                    if monsterAbilities[1].cooldown > 0:
                        monsterAbilities[1].cooldown -= 1
                    if monsterAbilities[2].cooldown > 0:
                        monsterAbilities[2].cooldown -= 1
            elif "cast" in self.dictionary.get(parser["Action"], [""]) and "fireball" in self.dictionary.get(parser["Direct Object"], [""]):
                fireball = self.player.abilities[1]
                if fireball.cooldown == 0:
                    if random.random() < fireball.chance:
                        print("enemy fireballed")
                        playerDamage = random.randint(fireball.minDamage, fireball.maxDamage)
                        print("Player Fireball Damage:",playerDamage)
                        monster.health -= playerDamage
                    else:
                        print("didn't hit enemy")
                        
                    if gotFrostbite:
                        print("Using fireball removed inflicted frostbite")
                        gotFrostbite = False
                        frostbiteDamage = 0
                    fireball.cooldown = fireball.refreshRate
                else:
                    print("Can't fireball now")
                    
                if monsterAbilities[0].cooldown > 0:
                    monsterAbilities[0].cooldown -= 1
                if monsterAbilities[1].cooldown > 0:
                    monsterAbilities[1].cooldown -= 1
                if monsterAbilities[2].cooldown > 0:
                    monsterAbilities[2].cooldown -= 1
    
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

        # NEW: Match object first, then adjectives around it
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
                        # (Optional) Look at words after object for post-modifiers (less common)
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

        print({"Action": prsa, "Direct Object": prso, "Indirect Object": prsi})

        return {
            "Action": prsa,
            "Direct Object": prso,
            "Indirect Object": prsi
        }
    
            
    
    def play(self):
        print("Welcome to the game. You're goal is to escape the dungeon.")
        self.state = "Move"
        
        while self.running:
            print(self.state)
            
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
    
    
    
    
    
    
    
    
    
    
