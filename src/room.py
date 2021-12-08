import random

class Room:
    def __init__(self, description):
        self.desc = description
        self.monsters = []
        self.exits = []
        self.items = []
    def addExit(self, exitName, destination):
        self.exits.append([exitName, destination])
    def getDestination(self, direction):
        for e in self.exits:
            if e[0] == direction:
                return e[1]
    def connectRooms(room1, dir1, room2, dir2=None):
        #creates "dir1" exit from room1 to room2 and vice versa
        if dir2 == None:
            if dir1 == "north":
                dir2 = "south"
            elif dir1 == "south":
                dir2 = "north"
            elif dir1 == "west":
                dir2 = "east"
            elif dir1 == "east":
                dir2 = "west"
        room1.addExit(dir1, room2)
        room2.addExit(dir2, room1)
    def exitNames(self):
        return [x[0] for x in self.exits]
    def addItem(self, item):
        self.items.append(item)
    def removeItem(self, item):
        if item in self.items:
            self.items.remove(item)
        else:
            for x in self.items:
                if x.container:
                    if x.removeItem(item):
                        return True
    def addMonster(self, monster):
        self.monsters.append(monster)
    def killAll(self):
        for x in self.monsters:
            x.die(True)
    def removeMonster(self, monster):
        self.monsters.remove(monster)
    def getMonsters(self):
        return self.monsters
    def getAggro(self): #specifically for the fight function
        mons = []
        for i in self.monsters:
            if i.agg:
                mons.append(i)
        return mons
    def hasItems(self):
        return self.items != []
    def getItemByName(self, name):
        for i in self.items:
            if i.name.lower() == name.lower():
                return i
            elif i.container:
                k = i.getItemByName(name)
                if k:
                    return k
        return False
    def hasMonsters(self):
        return self.monsters != []
    def getMonsterByName(self, name):
        for i in self.monsters:
            if i.name.lower() == name.lower():
                return i
        return False
    def randomNeighbor(self):
        return random.choice(self.exits)[1]