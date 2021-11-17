import os, random
from txt_parser import CmdRunError

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

class Player:
    def __init__(self, seed=random.randint(0, 2^64-1)):
        # Stuff will get screwy if there are multiple Player()s with different
        # seeds, but that is an eventuality that seems unlikely to occur.
        # (Famous last words.)
        self.seed = seed
        random.seed(seed)
        self.log = []
        self.playing = True
        self.location = None
        self.items = []
        self.health = 50
        self.alive = True
    def goDirection(self, direction):
        newloc = self.location.getDestination(direction)
        if newloc is None:
            raise CmdRunError("no such location")
        else:
            self.location = newloc
    def pickup(self, item):
        self.items.append(item)
        item.loc = self
        self.location.removeItem(item)
    def getItemByName(self, name):
        for i in self.items:
            if i.name.lower() == name.lower():
                return i
        return False
    def removeItem(self, item):
        if item in self.items:
            self.items.remove(item)
    def showInventory(self):
        print("You are currently carrying:")
        items_dict = {}
        for i in self.items:
            if i.name in items_dict:
                items_dict[i.name] += 1
            else:
                items_dict[i.name] = 1
        for name, num in items_dict.items():
            print("{:>10} ×{:02}".format(name, num))
        print()
    def showStats(self):
        print("Health: " + self.health) #more shall be added later
        print()
    def attackMonster(self, mon):
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

