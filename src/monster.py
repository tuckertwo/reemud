import random
import updater
from item import Weapon, Armor, Item

adjectives = ["venerable ", "youthful ", "sublime ", "dolorous ", "somber ", "jubilant ", "purple "] #flavor!

class Monster:
    def __init__(self, agg, name, health, room, xp=0, armor=None, dex=0, stren=0, con=0, mag=0): #aggressiveness, name, health, room, armor, stats
        self.name = name
        self.agg = agg #aggressiveness
        self.description = None #placeholder
        self.attacks = []
        self.health = health
        self.maxhealth = health
        self.xp = xp
        self.skills = [dex, stren, con, mag]
        self.inventory = []
        self.armor = armor
        self.room = room
        room.addMonster(self)
        updater.register(self)
    def addAttack(sverb, fverb, damage, prob, limit=None, effects=None):
        self.attacks.append([sverb, fverb, damage, prob, limit, effects])
    def giveSword(self): #specific but common attack
        self.attacks.append([" hits you with a sword", " tries to hit you with a sword, but misses", 6 + self.skills[1], .25 + (self.skills[0] / 15), None, None])
        self.attacks.append([" punches you", " punches you, harmlessly", 2 + self.skills[1], .25 + (self.skills[0] / 15), None, None])
        self.inventory.append(Weapon("Sword", "A nondescript metal sword.", 6, 3))
    def update(self):
        if random.random() < .5:
            self.moveTo(self.room.randomNeighbor())
    def moveTo(self, room):
        self.room.removeMonster(self)
        self.room = room
        room.addMonster(self)
    def takeDamage(self, amt):
        dam = int(random.random() * amt) + 1
        if not self.armor == None:
            dam = int(dam / self.armor.stren)
        self.health -= dam
        return dam  
    def isDead(self):
        return True
    def die(self):
        print(self.name + " dies!")
        if len(self.inventory) > 0:
            print("It drops:")
            for x in self.inventory:
                self.room.addItem(x)
                print(x.name)
        self.room.removeMonster(self)
        updater.deregister(self)
    def findAttack(self): #only should be used in the case of nonviolent monsters
        return(["", " cannot attack you", 0, 0, None, None])
    def triesToFlee(self):
        if self.health < int(self.maxhealth / 10):
            print(self.name + " flees!")
            self.moveTo(self.room.randomNeighbor())

class Dumb(Monster):
    def findAttack(self): #Dumb monsters randomly choose between their powerful and ineffective attacks
        if len(self.attacks) > 0:
            return random.choice(self.attacks)
        else:
            return(["", " cannot attack you", 0, 0, None, None])

class Undead(Dumb):
    def isDead(self): #Undead fortitude
        if random.random() < .3:
            print("You think " + self.name + " is dead... but then it is revived by necromantic magic!")
            self.health = 1
            return False
        else:
            return True
            
class Skeleton(Undead):
    def __init__(self, room, armor=None):
        Undead.__init__(self, True, random.choice(adjectives) + "skeleton", 3, room, 100, armor)
        self.giveSword()