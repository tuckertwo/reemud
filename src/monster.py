import random
import updater

adjectives = ["venerable ", "youthful ", "sublime ", "dolorous ", "somber ", "jubilant ", "purple "] #flavor!

class Monster:
    def __init__(self, agg, name, health, room, armor=None, dex=0, stren=0, con=0, mag=0): #aggressiveness, name, health, room, armor, stats
        self.name = name
        self.description = None #placeholder
        self.attacks = []
        self.health = health
        self.skills = [dex, stren, con, mag]
        self.armor = armor
        self.room = room
        room.addMonster(self)
        updater.register(self)
    def addAttack(sverb, fverb, damage, prob, limit=None, effects=None):
        self.attacks.append([sverb, fverb, damage, prob, limit, effects])
    def giveSword(self): #specific but common attack
        self.attacks.append(["hits you with a sword", "tries to hit you with a sword, but misses", 4 + self.skills[1], .25 + (self.skills[0] / 15), None, None])
        self.attacks.append(["punches you", "punches you, harmlessly", 1 + self.skills[1], .25 + (self.skills[0] / 15), None, None])
    def update(self):
        if random.random() < .5:
            self.moveTo(self.room.randomNeighbor())
    def moveTo(self, room):
        self.room.removeMonster(self)
        self.room = room
        room.addMonster(self)
    def die(self):
        self.room.removeMonster(self)
        updater.deregister(self)

class Dumb(Monster):
    def findAttack(self): #Dumb monsters randomly choose between their powerful and ineffective attacks
        if len(self.attacks) > 0:
            return random.choice(self.attacks)
        else:
            return(["", "cannot attack you", 0, 0, None, None])

class Undead(Monster):
    def die(self): #Undead fortitude
        if random.random() < .3:
            print("You think the " + self.name + " is dead... but then it is revived by necromantic magic!")
            self.health = 1
        else:
            Monster.die(self)
            
class Skeleton(Undead):
    def __init__(self, room, armor=None):
        Undead.__init__(self, True, random.choice(adjectives) + "skeleton", 10, room, armor)
        self.giveSword()