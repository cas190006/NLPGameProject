import spacy
from collections import Counter
import random
import math

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
    def __init__(self, doors, room=None):
        if room != None:
            self.type = room
        else:
            self.type = random.choice(['Empty', 'Chest', 'Monster'])
            
        self.description = self.generate_room_description()
        self.doors = doors
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
        if direction == "n" and self.doors >= 8:
            return True
        elif direction == "e" and 3 < self.doors % 8:
            return True
        elif direction == "s" and 1 < self.doors % 4:
            return True
        elif direction == "w" and self.doors % 2 == 1:
            return True
        
        return False


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
    
    
    def move(self, direction):
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
        
    def fight(self, monster):
        while 0 < game.player.health and 0 < monster.health:
            print(game.player.health, monster.health)
            playerInput = input("")
            if playerInput == "attack":
                #Player move
                playerDamage = random.randint(game.player.weapon.minDamage, game.player.weapon.maxDamage) + game.player.strength
                if random.random() < game.player.weapon.criticalChance:
                    print("Player Critcal!")
                    playerDamage = int(playerDamage * game.player.weapon.critical)
                    #crit_damage = int(base_damage * crit_multiplier)
                print("Player Damage:",playerDamage)
                monster.health -= playerDamage
                
                if monster.health < 0:
                    print("Enemy defeated!")
                    x,y = self.currentRoom
                    self.dungeon[x][y].contents = None
                    game.state = "Move"
                    break
                
                #Monster move
                if random.random() <= game.player.dodge:
                    print("Dodge. No damage taken")
                else:
                    enemyDamage = random.randint(monster.weapon.minDamage, monster.weapon.maxDamage)
                    if random.random() < monster.weapon.criticalChance:
                        print("Monster Critcal!")
                        enemyDamage = int(enemyDamage * monster.weapon.critical)
                    print("Enemy Damage:",enemyDamage)
                    game.player.health -= enemyDamage
                
                if game.player.health <= 0:
                    print("Game Over!")
                    game.state = "Game Over"
                    self.running = False
                    break
            elif playerInput == "health potion":
                health_potions = [item for item in game.player.inventory if isinstance(item, Potion) and item.type == "Health"]
                if health_potions:
                    health_potions[0].use(game.player)
                    game.player.inventory.remove(health_potions[0])
            elif playerInput == "strength potion":
                strength_potions = [item for item in game.player.inventory if isinstance(item, Potion) and item.type == "Strength"]
                if strength_potions:
                    strength_potions[0].use(game.player)
                    game.player.inventory.remove(strength_potions[0])
            elif playerInput == "run":
                self.currentRoom = self.lastRoom
                self.lastRoom = None
                game.state = "Move"
                break
            
            
    def inspect(self, chest):
        while True:
            for item in chest.items:
                if isinstance(item, Weapon):
                    print(item.name)
                elif isinstance(item, Potion):
                    print(item.type,"Potion")
                    
                playerInput = input("")
                
                if playerInput == "yes":
                    if isinstance(item, Weapon):
                        game.player.weapon = item
                        print(game.player.weapon.name, game.player.weapon.minDamage, game.player.weapon.maxDamage)
                    elif isinstance(item, Potion):
                        game.player.inventory.append(item)
                    chest.items.remove(item)
                    
            if not chest.items:
                break
            
            print("Leave chest?")
            playerInput = input("")
            if playerInput == "yes":
                break
        
        game.state = "Move"
        
    def endgame(self):
        monster = self.dungeon[4][4].contents
        while 0 < game.player.health and 0 < monster.health:
            print(game.player.health, monster.health)
            playerInput = input("")
            if playerInput == "attack":
                #Player move
                playerDamage = random.randint(game.player.weapon.minDamage, game.player.weapon.maxDamage) + game.player.strength
                if random.random() < game.player.weapon.criticalChance:
                    print("Player Critcal!")
                    playerDamage = int(playerDamage * game.player.weapon.critical)
                    #crit_damage = int(base_damage * crit_multiplier)
                print("Player Damage:",playerDamage)
                monster.health -= playerDamage
                
                if monster.health < 0:
                    print("Enemy defeated! You beat the game")
                    self.running = False
                    break
                
                #Monster move
                if random.random() < game.player.dodge:
                    print("Dodge. No damage taken")
                else:
                    enemyDamage = random.randint(monster.weapon.minDamage, monster.weapon.maxDamage)
                    if random.random() < monster.weapon.criticalChance:
                        print("Monster Critcal!")
                        enemyDamage = int(enemyDamage * monster.weapon.critical)
                    print("Enemy Damage:",enemyDamage)
                    game.player.health -= enemyDamage
                
                if game.player.health < 0:
                    print("Game Over!")
                    game.state = "Game Over"
                    self.running = False
                    break
            elif playerInput == "health potion":
                health_potions = [item for item in game.player.inventory if isinstance(item, Potion) and item.type == "Health"]
                if health_potions:
                    health_potions[0].use(game.player)
                    game.player.inventory.remove(health_potions[0])
            elif playerInput == "strength potion":
                strength_potions = [item for item in game.player.inventory if isinstance(item, Potion) and item.type == "Strength"]
                if strength_potions:
                    strength_potions[0].use(game.player)
                    game.player.inventory.remove(strength_potions[0])
            elif playerInput == "run":
                self.currentRoom = self.lastRoom
                self.lastRoom = None
                game.state = "Move"
                break
        
            
    
    def play(self):
        #print("Playing game")
        directions = ["up", "down", "right", "left"]
        
        print("Welcome to the game. You're goal is to escape the dungeon.")
        game.state = "Move"
        
        while self.running:
            print(game.state)
            #print(game.lastRoom, game.currentRoom)
            
            #print(f"Hello, {response}!")
            
            """
            if playerInput == "end":
                print("\nGoodbye")
                break;
            """
            
            if game.state == "Move":
                playerInput = input("")
                if playerInput in directions:
                    self.move(playerInput)
                elif playerInput == "map":
                    self.generate_map()
                elif playerInput == "chest":
                    x,y = self.currentRoom
                    if self.dungeon[x][y].contents.items:
                        game.state = "Inspect"
                elif playerInput == "health potion":
                    health_potions = [item for item in game.player.inventory if isinstance(item, Potion) and item.type == "Health"]
                    if health_potions:
                        health_potions[0].use(game.player)
                        game.player.inventory.remove(health_potions[0])
                elif playerInput == "strength potion":
                    strength_potions = [item for item in game.player.inventory if isinstance(item, Potion) and item.type == "Strength"]
                    if strength_potions:
                        strength_potions[0].use(game.player)
                        game.player.inventory.remove(strength_potions[0])
            elif game.state == "Endgame":
                result = self.endgame()
            elif game.state == "Fight":
                x,y = self.currentRoom
                self.fight(self.dungeon[x][y].contents)
            elif game.state == "Inspect":
                x,y = self.currentRoom
                self.inspect(self.dungeon[x][y].contents)
            elif game.state == "Game Over":
                break
            
        return 0
    

if __name__ == "__main__":
    game = Game()
    #game.generate_full_map()
    #game.generate_map()
    game.play();
    
    
    
    
    
    
    
    
    
    
