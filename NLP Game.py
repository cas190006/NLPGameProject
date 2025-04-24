import spacy
from collections import Counter
import random
import math
import re
import operator

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
                        "run", "escape", "retreat", "flee", "dash", "withdraw"
        }
        
        # Prepositions that often indicate PRSI
        self.prepositions = { "with", "using", "at", "in", "on", "into", "from", "to",
                             "towards"
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
                        "place", "spot", "location", "sector", "exit", "map", "chart",
                        "layout", "diagram", "guide", "grid", "dungeon", "terrain",
                        "atlas", "scroll", "parchment", "pathfinder", "schematic",
                        "overlay", "chest", "box", "crate", "container", "case", "stash", "strongbox",
                                  "cache", "trove",
                        "potion", "item", "flask", "vial", "tonic", "brew", "tincture", "essence", "elixir",
                        "sword", "blade", "steel", "brand"
        }
        
        self.dictionary = {
            "movement": ["move", "go", "head", "navigate", "advance", "take", "enter",
                         "traverse", "proceed", "step", "walk", "venture", "progress",
                         "veer", "approach"],
            "directions": {"up": ["up", "upper", "upward", "north", "northern"],
                           "down": ["down", "lower", "downward", "south", "southern"],
                           "left": ["left", "leftward", "west", "western"],
                           "right": ["right", "rightward", "east", "eastern"]},
            "room": ["room", "area", "space", "zone", "region", "section", "chamber",
                     "place", "spot", "location", "sector", "exit"],
            "next": ["next", "adjacent", "following", "neighboring", "ahead", "upcoming",
                     "subsequent", "succeeding", "other", "ensuing", "imminent", 
                     "forthcoming", "approaching", "adjoining", "forward"],
            
            "look": ["look", "check", "view", "inspect", "study", "examine",
                            "consult", "browse", "glance", "scan", "observe", "survey",
                            "gaze", "peek", "behold", "glimpse", "eye", "show", "display"],
            "map": ["map", "chart", "layout", "diagram", "guide", "grid", "dungeon",
                    "terrain", "atlas", "scroll", "parchment", "pathfinder", "schematic",
                    "overlay"],
            
            "open": ["open", "unseal", "pop", "access", "uncover", "reveal", "unveil",
                     "glimpse", "search", "rifle", "dig", "investigate", "explore", "audit"], 
            "chest": ["chest", "box", "crate", "container", "case", "stash", "strongbox",
                      "cache", "trove"],
            
            "use": ["use", "take", "apply", "activate", "employ", "cast", "utilize"], #Pop
            "drink": ["drink", "consume", "swallow", "guzzle", "down", "imbibe", "ingest", "chug"],
            
            "health": ["health", "healing", "restorative", "recovery", "cure", "rejuvenation", "herbal", "renewal"],
            "strength": ["strength", "might", "power", "brawn", "force", "muscle"],
            "potion": ["potion", "item", "flask", "vial", "tonic", "brew", "tincture", "essence", "elixir"],
            
            "attack": ["attack", "strike", "cut", "damage", "swing", "slash", "slice", "unleash", "hit", "fight"],
            "weapon": {"sword": ["sword", "blade", "steel", "brand"]},
            "run": ["run", "escape", "retreat", "flee", "dash", "withdraw"]
            
            #"potion": ["potion"]
        }
        
        """
        #actions (verbs)
        self.actions = {
            "look at", "burn down", "pick up", "put down",
            "examine", "look", "take", "drop", "attack", "burn", "go", "move"
        }
        
        # Prepositions that often indicate PRSI
        self.prepositions = {"with", "using", "at", "in", "on", "into", "from", "to"}
        
        #
        self.objects = {
            "room", "up" "mailbox", "glass bottle", "nasty-looking troll",
            "garlic", "white house", "elvish sword", "lantern", "onion", "carrot"
        }
        """
        
        #self.response = ""
        #self.events = []
        
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
        matrix[1][0].contents = Monster(Weapon("Fists", 8, 12, 0.25, 1.15), None, 60, 0.25)
        matrix[3][2].contents = Monster(Weapon("Sword", 10, 15, 0.4, 1.25), None, 70, 0.25)
        matrix[0][2].contents = Monster(Weapon("Sword", 10, 15, 0.4, 1.25), None, 70, 0.25)
        matrix[3][3].contents = Monster(Weapon("Long Sword", 13, 20, 0.45, 1.4), None, 80, 0.35)
        matrix[1][4].contents = Monster(Weapon("Long Sword", 15, 20, 0.45, 1.45), None, 85, 0.4)
        matrix[4][2].contents = Monster(Weapon("Sword", 10, 15, 0.4, 1.25), None, 60, 0.5)
        matrix[4][4].contents = Monster(Weapon("Steel Sword", 20, 40, 0.55, 1.5), None, 100, 0.4)
        
        #Chests
        matrix[1][1].contents = Chest([Potion("Health", 50)])
        matrix[4][0].contents = Chest([Weapon("Long Sword", 10, 20, 0.45, 1.25)])
        matrix[4][1].contents = Chest([Potion("Health", 100)])
        matrix[0][3].contents = Chest([Potion("Strength", 7)])
        matrix[0][4].contents = Chest([Weapon("Steel Sword", 15, 30, 0.55, 1.5), Potion("Health", 50)])
        
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
                    
                
                """
                if room.type != "Empty" and room.type != "Start" and room.type != "End":
                    stuff = room.type[0]
                else:
                    stuff = " "
                """
            
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
        
        
        
    
    def generate_full_map(self):
    
        print("Complete Map:")
        
        for i in range(len(self.dungeon)):
            # Top part of the maze
            for j in range(len(self.dungeon[0])):
                if self.dungeon[i][j].wall("n") and self.dungeon[i-1][j].wall("s"):
                    # Wall detected
                    print("+---", end="")
                else:
                    # No wall detected
                    print("+   ", end="")
            print("+")  # Close the top row of the current row
            
            # Side walls
            for j in range(len(self.dungeon[0])):
                if self.dungeon[i][j].wall("w") and self.dungeon[i][j-1].wall("e"):
                    # Wall detected
                    #print("|   ", end="")
                    print("| ", end="")
                    print(self.dungeon[i][j].type[0], end="")
                    print(" ", end="")
                else:
                    # No wall detected
                   # print("    ", end="")
                   print("  ", end="")
                   print(self.dungeon[i][j].type[0], end="")
                   print(" ", end="")
                    
                if j == len(self.dungeon[0]) - 1:
                    # Close the right part of the maze
                    print("|", end="")
            print()  # Newline after printing the row
        
        # Bottom part of the maze
        for j in range(len(self.dungeon[0])):
            # Leave the bottom part of the maze closed
            print("+---", end="")
        print("+")
            
        print()
    
    
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
        if self.find_part(parser["Action"]) == "movement":
            if self.find_part(parser["Direct Object"]) == "direction":
                for direction, synonyms in self.dictionary["directions"].items():
                    if playerInput.split()[1] in synonyms:
                        self.moving(direction)
                        break
            elif self.find_part(parser["Direct Object"]) == "next" and self.lastRoom is not None:
                self.nextRoom()
            elif parser["Indirect Object"] is not None:
                if self.find_part(parser["Indirect Object"].split()[-1]) == "room":
                    if self.find_part(parser["Indirect Object"].split()[0]) == "next":
                        self.nextRoom()
                    elif self.find_part(parser["Indirect Object"].split()[0]) == "direction":
                       for direction, synonyms in self.dictionary["directions"].items():
                           if parser["Indirect Object"].split()[0] in synonyms:
                               self.moving(direction)
                               break
        elif self.find_part(parser["Action"]) == "look" and (self.find_part(parser["Direct Object"]) == "map" or self.find_part(parser["Indirect Object"]) == "map"):
            self.generate_map()
        elif (self.find_part(parser["Action"]) == "look" or self.find_part(parser["Action"]) == "open") and (self.find_part(parser["Direct Object"]) == "chest" or self.find_part(parser["Indirect Object"]) == "chest"):
            x,y = self.currentRoom
            if isinstance(self.dungeon[x][y].contents, Chest):
                print("chest to inspect")
                self.state = "Inspect"
            else:
                print("no chest")
        elif self.find_part(parser["Action"]) == "use" or self.find_part(parser["Action"]) == "drink":
            if self.find_part(parser["Direct Object"].split()[0]) == "health" and self.find_part(parser["Direct Object"].split()[-1]) == "potion":
                print("Use health potion?")
                health_potions = [item for item in self.player.inventory if isinstance(item, Potion) and item.type == "Health"]
                if health_potions:
                    print("Yes!")
                    health_potions[0].use(self.player)
                    self.player.inventory.remove(health_potions[0])
                else:
                    print("No")
            elif self.find_part(parser["Direct Object"].split()[0]) == "strength" and self.find_part(parser["Direct Object"].split()[-1]) == "potion":
                print("Use strength potion?")
                strength_potions = [item for item in self.player.inventory if isinstance(item, Potion) and item.type == "Strength"]
                if strength_potions:
                    print("Yes!")
                    strength_potions[0].use(self.player)
                    self.player.inventory.remove(strength_potions[0])
                else:
                    print("No")
        
        
    def fight(self, monster):
        while 0 < self.player.health and 0 < monster.health:
            print(self.player.health, monster.health)
            playerInput = input("")
            parser = self.inputParser(playerInput)
            
            if self.find_part(parser["Action"]) == "attack":
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
                    self.state = "Move"
                    break
                
                #Monster move
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
            elif self.find_part(parser["Action"]) == "use" or self.find_part(parser["Action"]) == "drink":
                if self.find_part(parser["Direct Object"].split()[0]) == "health" and self.find_part(parser["Direct Object"].split()[-1]) == "potion":
                    print("Use health potion?")
                    health_potions = [item for item in self.player.inventory if isinstance(item, Potion) and item.type == "Health"]
                    if health_potions:
                        print("Yes!")
                        health_potions[0].use(self.player)
                        self.player.inventory.remove(health_potions[0])
                    else:
                        print("No")
                elif self.find_part(parser["Direct Object"].split()[0]) == "strength" and self.find_part(parser["Direct Object"].split()[-1]) == "potion":
                    print("Use strength potion?")
                    strength_potions = [item for item in self.player.inventory if isinstance(item, Potion) and item.type == "Strength"]
                    if strength_potions:
                        print("Yes!")
                        strength_potions[0].use(self.player)
                        self.player.inventory.remove(strength_potions[0])
                    else:
                        print("No")
            elif self.find_part(parser["Action"]) == "run":
                oldRoom = self.currentRoom
                self.currentRoom = self.lastRoom
                self.lastRoom = oldRoom
                self.state = "Move"
                break
            
            
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
        while 0 < self.player.health and 0 < monster.health:
            print(self.player.health, monster.health)
            playerInput = input("")
            parser = self.inputParser(playerInput)
            
            if self.find_part(parser["Action"]) == "attack":
                #Player move
                playerDamage = random.randint(self.player.weapon.minDamage, self.player.weapon.maxDamage) + self.player.strength
                if random.random() < self.player.weapon.criticalChance:
                    print("Player Critcal!")
                    playerDamage = int(playerDamage * self.player.weapon.critical)
                    #crit_damage = int(base_damage * crit_multiplier)
                print("Player Damage:",playerDamage)
                monster.health -= playerDamage
                
                if monster.health <= 0:
                    print("Enemy defeated! You beat the game!")
                    x,y = self.currentRoom
                    self.dungeon[x][y].contents = None
                    self.state = "Move"
                    break
                
                #Monster move
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
            elif self.find_part(parser["Action"]) == "use" or self.find_part(parser["Action"]) == "drink":
                if self.find_part(parser["Direct Object"].split()[0]) == "health" and self.find_part(parser["Direct Object"].split()[-1]) == "potion":
                    print("Use health potion?")
                    health_potions = [item for item in self.player.inventory if isinstance(item, Potion) and item.type == "Health"]
                    if health_potions:
                        print("Yes!")
                        health_potions[0].use(self.player)
                        self.player.inventory.remove(health_potions[0])
                    else:
                        print("No")
                elif self.find_part(parser["Direct Object"].split()[0]) == "strength" and self.find_part(parser["Direct Object"].split()[-1]) == "potion":
                    print("Use strength potion?")
                    strength_potions = [item for item in self.player.inventory if isinstance(item, Potion) and item.type == "Strength"]
                    if strength_potions:
                        print("Yes!")
                        strength_potions[0].use(self.player)
                        self.player.inventory.remove(strength_potions[0])
                    else:
                        print("No")
            elif self.find_part(parser["Action"]) == "run":
                oldRoom = self.currentRoom
                self.currentRoom = self.lastRoom
                self.lastRoom = oldRoom
                self.state = "Move"
                break
        
    def inputParser(self, userInput):
        userInput = userInput.lower()

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
    
    def find_part(self, word):
        for key, value in self.dictionary.items():
            if isinstance(value, dict) and key == "directions":  # Handle nested direction subcategories
                for sublist in value.values():
                    if word in sublist:
                        return "direction"
            elif isinstance(value, dict) and key == "weapon":  # Handle nested direction subcategories
                for sublist in value.values():
                    if word in sublist:
                        print("weapon")
                        return "weapon"
            elif word in value:
                return key
        return "Not found"
            
    
    def play(self):
        #print("Playing game")
        #directions = ["up", "down", "right", "left"]
        
        print("Welcome to the game. You're goal is to escape the dungeon.")
        self.state = "Move"
        
        while self.running:
            print(self.state)
            #print(self.lastRoom, self.currentRoom)
            
            #print(f"Hello, {response}!")
            
            """
            if playerInput == "end":
                print("\nGoodbye")
                break;
            """
            
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
    #game.generate_full_map()
    #game.generate_map()
    game.play();
    
    
    
    
    
    
    
    
    
    
