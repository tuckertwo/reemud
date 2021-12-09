import random
import updater
from item import Weapon, Armor, Item

adjectives = ["venerable ", "youthful ", "sublime ", "dolorous ", "somber ", "jubilant ", "purple ", "adamant ", "adroit ", "arcadian ", "baleful ", "bellicose ", "bilious ", "calamitous ", "boorish ", "comely ", "contumacious ", "corpulent ", "dowdy ", "efficacious ", "effulgent ", "equanimous ", "execrable ", "fastidious ", "feckless ", "fulsome ", "garrulous ", "gustatory ", "histrionic ", "hubristic ", "insolent ", "intransigent ", "inveterate ", "invidious ", "irksome ", "jocular ", "lachrymose ", "loquacious ", "mendacious ", "meretricious ", "mordant ", "munificent ", "parsimonious ", "pendulous ", "pernicious ", "platitudinous ", "querulous ", "puckish ", "recalcitrant ", "redolent ", "rhadamanthine ", "ruminative ", "sagacious ", "salubrious ", "sartorial ", "taciturn ", "tenacious ", "tremulous ", "verdant ", "trenchant ", "uxorious ", "voluble ", "wheedling ", "zealous ", "adorable ", "aggressive ", "alert ", "angry ", "annoyed ", "anxious ", "arrogant ", "ashamed ", "attractive ", "awful ", "beautiful ", "bewildered ", "brave ", "breakable ", "condemned ", "delightful ", "CRAAZY ", "depressed ", "cruel ", "creepy ", "expensive ", "grotesque ", "grieving ", "grumpy ", "frail ", "foolish ", "fragile ", "fantastic ", "famous ", "exuberant ", "evil ", "handsome ", "happy ", "graceful ", "glorious ", "magnificent ", "lovely ", "lonely"] #flavor!

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
        elif item.armor and self.armor == None:
            self.armor = item
    def giveWeapon(self, weapon):
        self.addAttack(" hits you with " + weapon.name, " tries to hit you with " + weapon.name + ", but misses", weapon.damage + self.skills[1], self.perception * (.25 + (self.skills[0] / 15)), True, 9999, weapon.effects)
    def update(self):
        self.effectsOccur()
        if random.random() < .3:
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
    def applyEffects(self, effex):
        for x in effex:
            self.applyEffect(x[0], x[1])
    def applyEffect(self, effect, amount=0):
        if effect == "poison":
            self.poison(amount)
        if effect == "fire":
            self.fire(amount)
    def poison(self, amount):
        if "poison" in self.condition:
            self.condition["poison"] = self.condition["poison"] + amount
        else:
            self.condition["poison"] = amount
            print(self.name + " is poisoned!")
    def fire(self, amount):
        if "fire" in self.condition:
            self.condition["fire"] = self.condition["fire"] + amount
        else:
            self.condition["fire"] = amount
            print(self.name + "is set on fire!")
    def effectsOccur(self, inBattle=False):
        if "poison" in self.condition:
            dam = int(random.random() * self.condition["poison"])
            if inBattle:
                print(self.name + " takes " + str(dam) + " points of poison damage")
            self.takeDamage(dam, True)
        if "fire" in self.condition:
            dam = int(random.random() * self.condition["fire"])
            if inBattle:
                print("You take " + str(dam) + " damage from the fire")
            self.takeDamage(dam, True)
            self.condition["fire"] -= 2
            if self.condition["fire"] < 0:
                if InBattle:
                    print("The fire burning " + self.name + "is extinguished")
                self.condition.pop("fire")
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
            
    def cullAttacks(self):
        for x in self.attacks:
            if x[5] < 1:
                self.attacks.remove(x)

class Passive(Monster):
    def findAttack(self): #only should be used in the case of nonviolent monsters
        return(["", " cannot attack you", 0, 0, False, 99999, None])


class Dumb(Monster):
    def findAttack(self): #Dumb monsters randomly choose between their powerful and ineffective attacks
        self.cullAttacks()
        if len(self.attacks) > 0:
            x = random.randrange(len(self.attacks))
            self.attacks[x][5] -= 1
            return self.attacks[x]
        else:
            return(["", " cannot attack you", 0, 0, False, 9999, None])

class Smart(Monster):
    def effectsOccur(self, inBattle=False):
        if (not inBattle) and ("poison" in self.condition):
            for m in self.inventory:
                if m.potion:
                    if m.antidote:
                        self.condition.remove("poison")
                        self.inventory.remove(m)
        Monster.effectsOccur(self)
            
    def update(self):
        if len(self.room.items) > 0:
            x = random.choice(self.room.items)
            if x.container:
                if not x.locked:
                    if len(x.contents) > 0:
                        y = random.choice(x.contents)
                        x = y
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
        self.cullAttacks()
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
        elif len(self.attacks) == 0:
            self.triesToFlee()
        else:
            return self.findAttackHelper()
    
    def findAttackHelper(self): #made a different class so easily replacable
        x = random.randrange(len(self.attacks))
        y = random.randrange(len(self.attacks))
        if self.attacks[x][2] > self.attacks[x][2]:
            self.attacks[x][5] -= 1
            return self.attacks[x]
        else:
            self.attacks[y][5] -= 1
            return self.attacks[y]
        
class Murderous(Smart):
    def findAttackHelper(self):
        y = self.attacks[0]
        for x in self.attacks:
            if x[2] > y[2]:
                y = x
        y[4] -= 1
        return y

class Animal(Dumb):
    def giveWeapon(self, weapon):
        return None #animals can't hold weapons

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
 
 
class Cultist(Smart):
    def __init__(self, room, armor=None):
        Smart.__init__(self, True, random.choice(adjectives) + "cultist", 5, room, 50, 1, armor)
        self.Punch()
        self.addAttack(" hits you with a magical Fire Bolt", " tries to hit you with a spell but misses ", 4, .4, False, 1, [["fire", 5]])
        self.addAttack(" hits you with a magical Witch Bolt", " tries to hit you with a spell but misses ", 8, .4, False, 3)
 
class HeadCultist(Murderous):
    def __init__(self, room):
        Smart.__init__(self, True, "cultist priest", 5, room, 50, 5, armor)
        self.Punch()
        self.addAttack(" hits you with a magical Fire Bolt", " tries to hit you with a spell but misses ", 4, .5, False, 4, [["fire", 5]])
        self.addAttack(" hits you with a magical Witch Bolt", " tries to hit you with a spell but misses ", 8, .5, False, 5)
        self.addAttack(" casts FIREBALL!", " tries to hit you with a spell but misses ", 9, 1, False, 1, [["fire", 10]])
        self.addAttack(" casts poison cloud", " tries to hit you with a spell but misses ", 9, 1, False, 1, [["poison", 10]])
        

class Ork(Dumb):
    def __init__(self, room, armor=None):
        Dumb.__init__(self, True, random.choice(adjectives) + "ork", 10, room, 75, 1, armor, 0, 8)
        self.Punch()

class Rat(Animal):
    def __init__(self, room, name="Rat"):
        Monster.__init__(self, False, name, 3, room, 10)
        self.addAttack(" bites you", " tries to bite you, but only gnaws on your shoe", 4, .3)
        
    def update(self):
        self.effectsOccur()
        if self.health <= 0:
            self.die(False)

 
class Skeleton(Undead):
    def __init__(self, room, armor=None):
        Undead.__init__(self, True, random.choice(adjectives) + "skeleton", 3, room, 25, 1, armor)
        self.Punch()
        
class Sheep(Passive):
    def __init__(self, room):
        Monster.__init__(self, False, "Sheep", 3, room, 2, 0)
    def update(self):
        self.effectsOccur()
        if random.random() < .9:
            self.moveTo(self.room.randomNeighbor())
        if self.health <= 0:
            self.die(False)
        

        #self, sverb, fverb, damage, prob, disarmable=False, limit=9999, effects=None)
        
class BigBeast(Dumb):
    def __init__(self, name, room):
        Dumb.__init__(self, True, name, 20, room, 300, 10, None, 0, 20)
        self.Punch()
        self.addAttack(" bites you", " tries to bite you, but only gnaws on your shoe", 14, .3)
        self.addAttack(" pounds you into the ground", " tries to punch you", 14, .3)
        
class Ghost(Undead):
    def __init__(self, room, armor=None):
        Undead.__init__(self, True, random.choice(adjectives) + "ghost", 15, room, 100, 1, armor)
        self.addAttack(" chokes you with its chilly fingers", " swoops down at you but misses", 14, .3)

class Zombie(Undead):
    def __init__(self, room, armor=None):
        Undead.__init__(self, True, random.choice(adjectives) + "zombia", 15, room, 100, 1, armor)
        self.Punch()
        
class LichKing(Murderous):
    