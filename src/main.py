#!/usr/bin/env python3
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

def good_split_spc(string, limit=-1):
    return list(filter(lambda x: len(x) > 0, string.split(' ', limit)))


# This is really just a struct.
class Arg():
    def __init__(self, name, nonsense=False, optional=False, infinite=False):
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

class CmdRunError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value

class CmdParseError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value

class Command():
    def __init__(self):
        if not hasattr(self, "help"):
            if len(self.args) >= 2:
                self.args_hr = " ".join([str(x) for x in self.args[1:]])
            else:
                self.args_hr = ""

    def func(self, p, u, orig_cli):
        return self.func_ap(p, u, self.cmdparse(orig_cli))

    def cmdparse(self, cmdstr):
        # Awful mutable data stuff ahead
        def parser(args_parsed, args_inp, args_to_fill):
            if len(args_inp) == 0:
                if len(args_to_fill) == 0 or args_to_fill[0].optional or \
                    (args_to_fill[0].infinite and
                     args_to_fill[0].name in args_parsed):
                    return args_parsed
                else:
                    raise CmdParseError("not enough arguments")
            elif len(args_to_fill) == 0:
                raise CmdParseError("too many arguments")
            else:
                tofill = args_to_fill[0]
                toproc = args_inp[0]
                if tofill is None:
                    return parser(args_parsed, args_inp[1:], args_to_fill[1:])
                elif tofill.nonsense:
                    if toproc == tofill.name:
                        return parser(args_parsed, args_inp[1:],
                                      args_to_fill[1:])
                    else:
                        return parser(args_parsed, args_inp, args_to_fill[1:])
                elif tofill.infinite:
                    if tofill.name in args_parsed:
                        args_parsed[tofill.name].append(toproc)
                        return parser(args_parsed, args_inp[1:],
                                      args_to_fill[1:])
                    else:
                        args_parsed[tofill.name] = [toproc]
                        return parser(args_parsed, args_inp[1:],
                                      args_to_fill[1:])
                else:
                        args_parsed[tofill.name] = toproc
                        return parser(args_parsed, args_inp[1:],
                                      args_to_fill[1:])

        if not self.args:
            return None
        else:
            return parser({}, good_split_spc(cmdstr), self.args)

class GoCmd(Command):
    def __init__(self, direction=None):
        if direction is not None:
            self.desc = "Moves {}".format(direction)
            self.args = []
            self.direction = direction
        else:
            self.desc = "Moves in the given direction"
            self.args = [None, Arg("direction", False, False, False)]
            self.direction = None
        Command.__init__(self)

    def func_ap(self, player, updater, args_parsed):
        if self.direction is not None:
            direction = self.direction
        else:
            direction = args_parsed["direction"]

        player.goDirection(direction)
        updater.updateAll()

class PickupCmd(Command):
    args = [None, Arg("item", False, False, True)]
    desc = "Picks up an item"

    def func(self, player, _updater, orig_args):
        arg_split = good_split_spc(orig_args, 1)
        targetName = arg_split[1]
        target = player.location.getItemByName(targetName)
        if target:
            player.pickup(target)
            return True
        else:
            raise CmdRunError("no such item")

class Inventory(Command):
    args = []
    desc = "Prints the player's inventory"

    def func(self, p, _u, _orig_args):
        return p.showInventory()

class Help(Command):
    args = []
    desc = "Prints a summary of all commands"

    def __init__(self, commands):
        Command.__init__(self)

    def func(self, _p, _u, _orig_args):
        commands_full = {}
        commands_full.update(commands)
        commands_full.update({"help": self}) # Recursion has its limits
        helptext = "{:>10}   {:15}       {}\n".format("Command",
                                                     "Arguments", "Description")
        for k, v in commands_full.items():
            helptext += "{:>10}:  {:15}       {}\n".format(k, v.args_hr, v.desc)
        print(helptext)

class Exit(Command):
    args = []
    desc = "Exits the game"

    def func(self, p, _u, _orig_args):
        p.playing = False

class Attack(Command):
    args = [None, Arg("monster", False, False, True)]
    desc = "Attacks a monster"

    def func(self, player, _updater, orig_args):
        arg_split = good_split_spc(orig_args, 1)
        targetName = arg_split[1]
        target = player.location.getMonsterByName(targetName)
        if target:
            player.attackMonster(target)
            return True
        else:
            raise CmdRunError("no such monster")

commands = {
    "go": GoCmd(None),
    "north": GoCmd("north"),
    "n": GoCmd("north"),
    "south": GoCmd("south"),
    "s": GoCmd("south"),
    "east": GoCmd("east"),
    "e": GoCmd("east"),
    "west": GoCmd("west"),
    "w": GoCmd("west"),

    "pickup": PickupCmd(),
    "inventory": Inventory(),
    "exit": Exit(),
    "attack": Attack(),
}
commands["help"] = Help(commands) # Recursion!

def main(seed=random.randint(0, 2^64-1), replay=[]):
    createWorld()
    new_replay = []
    while player.playing and player.alive:
        printSituation()
        try:
            cmd_raw = input("> ") # Does not have '\n' appended; I checked.
            cmd_split = good_split_spc(cmd_raw)
            cmd_name = cmd_split[0].lower()
            cmd_obj = None
            if cmd_name in commands:
                cmd_obj = commands[cmd_name]
            else:
                for cmd_cand in commands.keys():
                    if cmd_name == cmd_cand[0:len(cmd_name)]:
                        if cmd_obj is not None:
                            raise CmdParseError("ambiguous command")
                        else:
                            cmd_obj = commands[cmd_cand]
            if cmd_obj is None:
                raise CmdParseError("invalid command")
            else:
                cmd_obj.func(player, updater, cmd_raw)
        except CmdParseError as e: # Pass all other errors through, I guess.
            print("Error parsing command: " + e)
        except CmdRunError as e:
            print("Error running command: " + e)
        except EOFError:
            print()
            commands["exit"].func(player, updater, "^D")

main()
