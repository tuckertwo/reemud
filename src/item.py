import os

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

class Item:
    weapon = False
    armor = False
    book = False
    def __init__(self, name, desc, weight=1):
        self.name = name
        self.desc = desc
        self.weight = weight
        self.loc = None
    def describe(self):
        clear()
        print(self.desc)
        print()
        input("Press enter to continue...")
    def putInRoom(self, room):
        self.loc = room
        room.addItem(self)

class Weapon(Item):
    weapon = True
    def __init__(self, name, desc, damage=1, weight=1, effects=None, effmt=0):
        self.damage = damage
        self.effects = effects
        Item.__init__(self, name, desc, weight)

class Armor(Item):
    armor = True
    def __init__(self, name, desc, stren, weight=1, effects=None):
        self.stren = stren
        self.effects = effects
        Item.__init__(self, name, desc, weight)

class Book(Item):
    book = True
    def __init__(self, name, text, desc="A book", weight=1):
        self.text = text
        Item.__init__(self, name, desc, weight)
        
    