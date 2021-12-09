import os
import room

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

class Item:
    weapon = False
    armor = False
    book = False
    potion = False
    container = False
    key = False
    door = False
    scroll = False
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
        if not self.effects == None:
            poison = False
            fire = False
            for x in self.effects:
                if x[0] == "poison":
                    poison = True
                elif x[0] == "fire":
                    fire = True
            if poison:
                print("This weapon is lathered with poison")
            if fire:
                print("This weapon is enchanted with fire magic")

        print()

class Armor(Item):
    armor = True
    def __init__(self, name, desc, stren, weight=2, effects=None):
        self.stren = stren
        self.effects = effects
        Item.__init__(self, name, desc, weight)

    def describe(self):
        print(self.desc)
        print("Strength: " + str(self.stren))
        print()

class Book(Item):
    book = True
    def __init__(self, name, desc):
        Item.__init__(self, name, desc, .5)

    def describe(self):
        print("The text reads as follows:")
        print(self.desc)
        print()

class Potion(Item):
    potion = True
    heal = False
    antidote = False

    def applyTo(self, weapon):
        print("Why would you want to apply " + self.name + " to a weapon?")

class HealingPotion(Potion):
    heal = True
    def __init__(self, amt, name="Healing Potion", desc="A red-colored vial of healing potion", weight=1):
        self.amount = amt
        Item.__init__(self, name, desc, weight)

    def drink(self, _player):
        _player.heal(self.amount)

    def describe(self):
        print(self.desc)
        print("Power: " + str(self.amount) + " hp")
        print()

    def applyTo(self, weapon):
        print("Why would you want to apply " + self.name + " to a weapon? What, do you want to heal your enemies?")


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
            weapon.effects = []
        weapon.effects.append(["poison", self.amount])
        print("The " + self.name + " has been applied to the " + weapon.name)

class Antidote(Potion):
    antidote = True
    def __init__(self, name="Antidote", desc="A blue-colored vial of antidote", weight=1):
        Item.__init__(self, name, desc, weight)

    def drink(self, _player):
        _player.applyEffect("antidote")

class Water(Potion):
    def __init__(self, name="Fire Extinguisher", desc="A fire extinguisher for you to drink", weight=1):
        Item.__init__(self, name, desc, weight)

    def drink(self, _player):
        _player.applyEffect("water")

class Regeneration(Potion):
    def __init__(self, amt, name="Regeneration Potion", desc="An orange-colored vial of regeneration potion", weight=1):
        self.amount = amt
        Item.__init__(self, name, desc, weight)

    def drink(self, _player):
        _player.applyEffect("regeneration", self.amount)

    def describe(self):
        print(self.desc)
        print("Power: " + str(int(self.amount / 2)) + " rounds")
        print()

class Container(Item):
    container = True
    locked = False
    def __init__(self, name, desc, contents=[], weight=100):
        self.contents = contents
        Item.__init__(self, name, desc, weight)

    def putInside(self, item):
        self.contents.append(item)
        self.weight += item.weight

    def getItemByName(self, targetName):
        for i in self.contents:
            if i.name.lower()[:len(targetName)] == targetName.lower():
                return i
        return False

    def removeItem(self, item):
        if item in self.contents:
            self.weight -= item.weight
            self.contents.remove(item)
            return True
        return False


    def describe(self):
        print(self.desc)
        print("Inside is: ")
        for x in self.contents:
            print("  - " + x.name)
        print()

    def unlock(self, keys, player):
        print("The " + self.name + " isn't locked")

    def lock(self, keys):
        print("The " + self.name + " can't be locked")

class Key(Item):
    key = True
    def __init__(self, name):
        Item.__init__(self, name, "A " + name, .05)

class LockedChest(Container):

    def __init__(self, name, desc, key, contents=[], locked=True, weight=100):
        self.locked = locked
        self.key = key
        Container.__init__(self, name, desc, contents, weight)

    def getItemByName(self, targetName):
        if locked:
            return False
        else:
            return Container.getItemByName(self, targetName)

    def describe(self):
        if locked:
            print(self.desc)
            print("The " + self.name + " is locked")
            print()
        else:
            Container.describe(self)

    def unlock(self, keys):
        if locked:
            for k in keys:
                if k.name == self.key.name:
                    print("You unlock the " + self.name + " with " + k.name)
                    locked = False
                    return True
                print("You do not have the key to unlock the " + self.name)
        else:
            print("The " + self.name + " isn't locked")

    def lock(self, keys, player): #some wandering monsters take items from unlocked chests
        if not locked:
            for k in keys:
                if k.name == self.key.name:
                    print("You lock the " + self.name + " with " + k.name)
                    locked = True
                    return True
                print("You do not have the key to lock the " + self.name)
        else:
            print("The " + self.name + " is already locked")

class Door(Item):
    door = True
    def __init__(self, key, direction, connectingroom, name="x", desc="x"):
        if name == "x":
            name = "Locked Door " + direction
            desc = "Locked Door " + " facing " + direction
        self.key = key
        self.direction = direction
        self.connecting = connectingroom
        Item.__init__(self, name, desc, 99999)

    def unlock(self, keys, player):
        for k in keys:
            if k.name == self.key.name:
                print("You unlock the " + self.name + " and it swings open")
                room.Room.connectRooms(player.location, self.direction, self.connecting)
                player.location.removeItem(self)
                return True
        print("You don't have the right key")


class MagicScroll(Item):
    scroll = True

    def applyTo(self, weapon):
        if weapon.effects == None:
            weapon.effects = []
        weapon.effects.append(self.effect)
        print("The " + self.name + " has been applied to the " + weapon.name)

class HealingScroll(MagicScroll):
    def __init__(self, name="Scroll of Healing", desc="A powerful magic scroll of healing"):
        Item.__init__(self, name, desc, .1)
        self.effect = ["heal"]

    def applyTo(self, weapon):
        print("Why would you ever want to apply a scroll of healing to a weapon? What, do you want to heal your enemies?")

class DamageScroll(MagicScroll):

    def __init__(self, amt, name="Scroll of Destruction", desc="A powerful magic scroll of destruction"):
        self.effect = ["dam"]
        self.amt = amt
        Item.__init__(self, name, desc, .1)

    def applyTo(self, weapon):
        weapon.damage += int(self.amt / 2)
        print("The " + self.name + " has been applied to the " + weapon.name)
        print("The " + weapon.name + " now does more damage")

class PoisonScroll(MagicScroll):
    def __init__(self, amt, name="Scroll of Poison Cloud", desc="A powerful magic scroll of poison gas"):
        self.effect = ["poison", amt]
        self.bdes = "A clowd of poison fog smothers your opponents!"
        Item.__init__(self, name, desc, .1)

class Fireball(MagicScroll):
    def __init__(self, amt, name="Scroll of Fireball", desc="A powerful magic scroll of FIREBALL!!!"):
        self.effect = ["fire", amt]
        self.bdes = "A huge fireball engulfs the room!"
        Item.__init__(self, name, desc, .1)

class Polymorph(MagicScroll):
    def __init__(self, name="Scroll of Polymorph", desc="A powerful magic scroll of polymorph"):
        self.effect = ["polymorph"]
        Item.__init__(self, name, desc, .1)
