import os

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

class Item:
    weapon = False
    armor = False
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
    isweapon = True

class Armor(Item):
    armor = True
