import os

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

class Item:
    weapon = False
    armor = False
    book = False
    potion = False
    def __init__(self, name, desc, weight=1):
        self.name = name
        self.desc = desc
        self.weight = weight
        self.loc = None
    def describe(self):
        print(self.desc)
        print()
    def putInRoom(self, room):
        self.loc = room
        room.addItem(self)

class Weapon(Item):
    weapon = True
    def __init__(self, name, desc, damage=1, weight=1, effects=None, effmt=0):
        self.damage = damage
        self.effects = effects
        Item.__init__(self, name, desc, weight)
        
    def describe(self):
        print(self.desc)
        print("Power: " + str(self.damage))
        print()

class Armor(Item):
    armor = True
    def __init__(self, name, desc, stren, weight=1, effects=None):
        self.stren = stren
        self.effects = effects
        Item.__init__(self, name, desc, weight)
        
    def describe(self):
        print(self.desc)
        print("Strength: " + str(self.stren))
        print()

class Book(Item):
    book = True
    def __init__(self, name, text, desc="A book", weight=1):
        self.text = text
        Item.__init__(self, name, desc, weight)
        
class Potion(Item):
    potion = True
    
class HealingPotion(Potion):
    def __init__(self, amt, name="Healing Potion", desc="A red-colored vial of healing potion", weight=1):
        self.amount = amt
        Item.__init__(self, name, desc, weight)
        
    def drink(self, _player):
        _player.heal(self.amount)
        
    def describe(self):
        print(self.desc)
        print("Power: " + str(self.amount) + " hp")
        print()
        
class Poison(Potion):
    def __init__(self, amt, name="Poison", desc="A green-colored vial of poison", weight=1):
        self.amount = amt
        Item.__init__(self, name, desc, weight)
        
    def drink(self, _player):
        _player.applyEffect("poison", self.amount)
    
    def describe(self):
        print(self.desc)
        print("Power: " + str(self.amount))        
        print()
    
    def applyTo(self, weapon):
        if weapon.effects == None:
            weapon.effects = {"poison": self.amount}
        elif "poison" in weapon.effects:
            weapon.effects["poison"] = weapon.effects["poison"] + self.amount
        else:
            weapon.effects["poison"] = self.amount
        print("The " + self.name + " has been applied to the " + weapon.name)
    
class Antidote(Potion):
    def __init__(self, name="Antidotes", desc="A blue-colored vial of antidote", weight=1):
        Item.__init__(self, name, desc, weight)

    def drink(self, _player):
        _player.applyEffect("antidote")
    