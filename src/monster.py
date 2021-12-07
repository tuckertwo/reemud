import random
import updater
from item import Weapon, Armor, Item

adjectives = ["venerable ", "youthful ", "sublime ", "dolorous ", "somber ", "jubilant ", "purple "] #flavor!

class Monster:
    def __init__(self, agg, name, health, room, xp=0, perception=1, armor=None, dex=0, stren=0, con=0, mag=0): #aggressiveness, name, health, room, armor, stats
        self.name = name
        self.agg = agg #aggressiveness
        self.description = None #placeholder
        self.attacks = []
        self.health = health
        self.maxhealth = health
        self.xp = xp
        self.perception = perception
        self.skills = [dex, stren, con, mag]
        self.inventory = []
        self.condition = {}
        self.armor = armor
        self.room = room
        room.addMonster(self)
        updater.register(self)
    def addAttack(self, sverb, fverb, damage, prob, disarmable=False, limit=9999, effects=None):
        self.attacks.append([sverb, fverb, damage, prob, disarmable, limit, effects])
    def Punch(self):
        self.addAttack(" punches you", " punches you, harmlessly", 2 + self.skills[1], self.perception * (.25 + (self.skills[0] / 15)), False)
    def giveItem(self, item):
        self.inventory.append(item)
        if item.weapon:
            self.giveWeapon(item)
    def giveWeapon(self, weapon):
        self.addAttack(" hits you with " + weapon.name, " tries to hit you with " + weapon.name + ", but misses", weapon.damage + self.skills[1], self.perception * (.25 + (self.skills[0] / 15)), True, None, weapon.effects)
    def update(self):
        self.effectsOccur()
        if random.random() < .5:
            self.moveTo(self.room.randomNeighbor())
        if self.health <= 0:
            self.die(False)
    def moveTo(self, room):
        self.room.removeMonster(self)
        self.room = room
        room.addMonster(self)
    def takeDamage(self, amt, ignorearmor=False):
        dam = int(random.random() * amt) + 1
        if not ((self.armor == None) or ignorearmor):
            dam = int(dam / self.armor.stren)
        self.health -= dam
        return dam  
    def isDead(self):
        return True
    def applyEffect(self, effect, amount=0):
        if effect == "poison":
            self.poison(amount)
    def poison(self, amount):
        if "poison" in self.condition:
            self.condition["poison"] = self.condition["poison"] + amount
        else:
            self.condition["poison"] = amount
            print(self.name + " is poisoned!")
            
    def effectsOccur(self, inBattle=False):
        if "poison" in self.condition:
            dam = int(random.random() * self.condition["poison"])
            if inBattle:
                print(self.name + " takes " + str(dam) + " points of poison damage")
            self.takeDamage(dam, True)
    def die(self, inBattle=True):
        if inBattle:
            print(self.name + " dies!")
        if len(self.inventory) > 0:
            if inBattle:
                print("It drops:")
            for x in self.inventory:
                self.room.addItem(x)
                if inBattle:
                    print(x.name)
        self.room.removeMonster(self)
        updater.deregister(self)
    def findAttack(self): #only should be used in the case of nonviolent monsters
        return(["", " cannot attack you", 0, 0, False, 99999, None])
    def triesToFlee(self):
        print(self.name + " flees!")
        self.moveTo(self.room.randomNeighbor())
    def disarm(self, pstren):
        if (random.random() + pstren) > (random.random() + self.skills[1]):
            if len(self.attacks) > 0:
                y = random.choice(self.attacks)
                if y[4]:
                    print(self.name + y[1] + ", and you disarm them of that attack!")
                    self.attacks.remove(y)
                else:
                    print("You try to disarm " + self.name + " but fail")
        else:
            print("You try to disarm " + self.name + " but fail")

class Dumb(Monster):
    def findAttack(self): #Dumb monsters randomly choose between their powerful and ineffective attacks
        if len(self.attacks) > 0:
            return random.choice(self.attacks)
        else:
            return(["", " cannot attack you", 0, 0, False, None, None])

class Smart(Monster):
    def effectsOccur(self, inBattle=False):
        if (not inBattle) and ("poison" in self.condition):
            for m in self.inventory:
                if m.potion:
                    if m.antidote:
                        self.condition.remove("poison")
                        self.inventory.remove(m)
        Monster.effectsOccur(self)
            
    def update():
        if len(self.room.items) > 0:
            x = random.choice(self.room.items)
            if x.potion:
                self.inventory.append(x)
                self.room.removeItem(x)
            elif x.weapon:
                self.giveWeapon(x)
                self.room.removeItem(x)
            elif x.armor:
                if self.armor == None:
                    self.armor = x
                    self.room.removeItem(x)
                elif x.stren > self.armor.stren:
                    self.room.addItem(self.armor)
                    self.armor = x
                    self.room.removeItem(x)
        if self.health < int(self.maxhealth / 10):
            for m in self.inventory:
                if m.potion:
                    if m.heal:
                        print(self.name + " drinks a healing potion!")
                        self.health += m.amount
                        self.inventory.pop(m)
        Monster.update(self)
    def findAttack(self):
        if self.health < int(self.maxhealth / 10):
            found = False
            for m in self.inventory:
                if m.potion:
                    if m.heal:
                        print(self.name + " drinks a healing potion!")
                        self.health += m.amount
                        self.inventory.remove(m)
                        found = True
            if not found:
                self.triesToFlee()
        

class Undead(Dumb):
    def poison(self, amount): #Undead cannot be poisoned
        return None
    def isDead(self): #Undead fortitude
        if random.random() < .3:
            print("You think " + self.name + " is dead... but then it is revived by necromantic magic!")
            self.health = 1
            return False
        else:
            return True
            
class Skeleton(Undead):
    def __init__(self, room, armor=None):
        Undead.__init__(self, True, random.choice(adjectives) + "skeleton", 3, room, 25, 1, armor)
        self.Punch()