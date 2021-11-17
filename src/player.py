import os

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

class Player:
    def __init__(self):
        self.playing = True
        self.location = None
        self.items = []
        self.health = 50
        self.alive = True
    def goDirection(self, direction):
        self.location = self.location.getDestination(direction)
    def pickup(self, item):
        self.items.append(item)
        item.loc = self
        self.location.removeItem(item)
    def showInventory(self):
        clear()
        print("You are currently carrying:")
        for i in self.items:
            print(i.name)
        print()
    def attackMonster(self, mon):
        clear()
        print("You are attacking " + mon.name)
        print("Your health is " + str(self.health) + ".")
        print(mon.name + "'s health is " + str(mon.health) + ".")
        if self.health > mon.health:
            self.health -= mon.health
            print("You win. Your health is now " + str(self.health) + ".")
            mon.die()
        else:
            print("You lose.")
            self.alive = False
        print()

