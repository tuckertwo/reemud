from room import Room
from player import Player
from item import Item
from monster import Monster
import random
import os
import updater

player = Player()

def createWorld():
    a = Room("You are in room 1")
    b = Room("You are in room 2")
    c = Room("You are in room 3")
    d = Room("You are in room 4")
    Room.connectRooms(a, "east", b, "west")
    Room.connectRooms(c, "east", d, "west")
    Room.connectRooms(a, "north", c, "south")
    Room.connectRooms(b, "north", d, "south")
    i = Item("Rock", "This is just a rock.")
    i.putInRoom(b)
    player.location = a
    Monster("Bob the monster", 20, b)

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def printSituation():
    clear()
    print(player.location.desc)
    print()
    if player.location.hasMonsters():
        print("This room contains the following monsters:")
        for m in player.location.monsters:
            print(m.name)
        print()
    if player.location.hasItems():
        print("This room contains the following items:")
        for i in player.location.items:
            print(i.name)
        print()
    print("You can go in the following directions:")
    for e in player.location.exitNames():
        print(e)
    print()

def showHelp():
    clear()
    print("go <direction> -- moves you in the given direction")
    print("inventory -- opens your inventory")
    print("pickup <item> -- picks up the item")
    print()
    pause()

def pause():
    input("Please press 'enter' to continue.")

def good_split_spc(string):
    return filter(lambda x: len(x)>0, string.split(' '))


# This is really just a struct.
class Arg():
    def __init__(self, name, nonsense, optional, infinite):
        self.name = name
        self.nonsense = nonsense
        self.optional = optional
        self.infinite = infinite

    def __repr__(self):
        r = self.name
        if self.nonsense:
            r = "({})".format(r)
        if self.optional:
            r = "[{}]".format(r)
        if self.infinite:
            r = "{}+".format(r)
        return r

class CmdParseError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return "Cannot parse command: " + repr(self.value)

class Command():
    def __init__(self):
        if hasattr(self, "func"):
            raise ValueError("missing required parameters")
        if hasattr(self, "help"):
            self.help = [str(x) for x in self.args].join(" ")

    def cmdparse(self, cmdstr, args):
        if len(args) < len(filter(lambda x: x.optional, self.args)):
            raise CmdParseError("not enough arguments")
        if len(args) > len(self.args) and not args[-1].infinite:
            raise CmdParseError("too many arguments")

def main(seed=random.randint(0, 2^64-1), replay=[]):
    createWorld()
    playing = True
    while playing and player.alive:
        printSituation()
        commandSuccess = False
        timePasses = False
        while not commandSuccess:
            commandSuccess = True
            command = input("What now? ")
            commandWords = command.split()
            if commandWords[0].lower() == "go":       # cannot handle multi-word directions
                player.goDirection(commandWords[1])
                timePasses = True
            elif commandWords[0].lower() == "pickup": # can handle multi-word objects
                targetName = command[7:]
                target = player.location.getItemByName(targetName)
                if target != False:
                    player.pickup(target)
                else:
                    print("No such item.")
                    commandSuccess = False
            elif commandWords[0].lower() == "inventory":
                player.showInventory()
            elif commandWords[0].lower() == "help":
                showHelp()
            elif commandWords[0].lower() == "exit":
                playing = False
            elif commandWords[0].lower() == "attack":
                targetName = command[7:]
                target = player.location.getMonsterByName(targetName)
                if target != False:
                    player.attackMonster(target)
                else:
                    print("No such monster.")
                    commandSuccess = False
            else:
                print("Not a valid command")
                commandSuccess = False
        if timePasses == True:
            updater.updateAll()

main()
