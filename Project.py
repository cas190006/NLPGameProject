import spacy
from collections import Counter
import random
import math

class Game:
    def __init__(self):
        self.dungeon = self.generateDungeon()
        
    def generateDungeon(self):
        
        matrix = [
                [Room('Start'), Room('Empty'), Room('Monster'), Room('Chest'), Room('Empty')],
                [Room('Monster'), Room('Chest'), Room('Empty'), Room('Chest'), Room('Monster')],
                [Room('Empty'), Room('Monster'), Room('Chest'), Room('Empty'), Room('Chest')],
                [Room('Empty'), Room('Chest'), Room('Empty'), Room('Monster'), Room('Chest')],
                [Room('Chest'), Room('Empty'), Room('Monster'), Room('Chest'), Room('End')]
            ]
        
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
    
    def generateMap(self):
        
        """
        for i in range(len(self.dungeon)):
            
            for j in range(len(self.dungeon[i])):
                print()
        """
        
        print("___________")
        print("| | | | | |")
        
        return ""
    
    def play(self):
        print("Playing game")
        return 0
        
    
"""
    def start(self):
        print(f"{self.name} has started!")
        self.is_running = True
        self.run()

    def run(self):
        while self.is_running:
            self.update()
            self.render()
    
    def update(self):
        # Game logic updates go here
        print("Updating game...")
    
    def render(self):
         # Game rendering logic goes here
        print("Rendering game...")

    def stop(self):
        print(f"{self.name} has stopped.")
        self.is_running = False
"""

class Room:
    def __init__(self, room=None):
        if room != None:
            self.type = room
        else:
            self.type = random.choice(['Empty', 'Chest', 'Monster'])
            
        self.description = self.generate_room_description()
        self.visited = False
        
    def generate_room_description(self):
        """Generate a description based on the room type."""
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

if __name__ == "__main__":
    game = Game()
    game.play();
    
    #print(game.dungeon)
    #print("\n".join(" ".join(room.type for room in row) for row in game.dungeon))
    
    #game.start()
    # Game is running
    #game.stop()
    
    
    
    
    
    
    
    
    
    