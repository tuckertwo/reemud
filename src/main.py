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

def printSituation(player):
    print(player.location.desc)
    if player.location.hasMonsters():
        print("This room contains the following monsters:")
        for m in player.location.monsters:
            print("  - " + m.name)
    if player.location.hasItems():
        print("This room contains the following items:")
        for i in player.location.items:
            print("  - " + i.name)
    print("You can go {}.".format(eng_list(player.location.exitNames())))
    print()

def eng_list(xs, str_acc=""):
    if len(xs) == 0:
        return str
    elif len(xs) == 1:
        return xs[0]
    elif len(xs) == 2:
        return "{}{} and {}".format(str_acc, xs[0], xs[1])
    elif len(xs) == 2:
        return "{}{}, {}, and {}".format(str_acc, xs[0], xs[1], xs[2])
    else:
        return eng_list(xs[1:], "{}{}, ".format(str_acc, xs[0]))


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
        if not hasattr(self, "args_hr"):
            if self.args is not None and len(self.args) >= 2:
                self.args_hr = " ".join([str(x) for x in self.args[1:]])
            else:
                self.args_hr = ""

    def func(self, p, u, cmdstr):
        return self.func_ap(p, u, self.cmdparse(cmdstr))

    def cmdparse(self, cmdstr):
        # Awful mutable data stuff ahead
        def parser(args_parsed, args_inp, args_to_fill):
            # If out of stuff to parse
            if len(args_inp) == 0:
                # Premature end?
                if len(args_to_fill) == 0 or args_to_fill[0].optional or \
                    (args_to_fill[0].infinite and
                     args_to_fill[0].name in args_parsed):
                    return args_parsed
                else:
                    raise CmdParseError("not enough arguments")
            # Out of buckets and still more arguments exist?
            elif len(args_to_fill) == 0:
                raise CmdParseError("too many arguments")
            else:
                # Defer setting convenience variables until we are sure that
                # the queues are not empty
                tofill = args_to_fill[0]
                toproc = args_inp[0]
                if tofill is None: # Ignore this argument
                    return parser(args_parsed, args_inp[1:], args_to_fill[1:])
                # Handle placeholder/nonsense arguments, used to make commands
                # appear more English-like
                # (*e.g.* `kill troll with axe` as opposed to `kill troll axe`)
                elif tofill.nonsense:
                    if toproc == tofill.name:
                        return parser(args_parsed, args_inp[1:],
                                      args_to_fill[1:])
                    else:
                        return parser(args_parsed, args_inp, args_to_fill[1:])
                # Infinite arguments are placed at the end of a string of
                # args to capture the remainder of the command.
                elif tofill.infinite:
                    if tofill.name in args_parsed:
                        args_parsed[tofill.name].append(toproc)
                        return parser(args_parsed, args_inp[1:],
                                      args_to_fill[1:])
                    else:
                        args_parsed[tofill.name] = [toproc]
                        return parser(args_parsed, args_inp[1:],
                                      args_to_fill[1:])
                # Normal (non-infinite, non-nonsense) arguments
                else:
                    args_parsed[tofill.name] = toproc
                    return parser(args_parsed, args_inp[1:],
                                    args_to_fill[1:])

        # Bail out if argument processing is unneeded
        if not self.args:
            return None
        # Otherwise, start the process
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
        printSituation(player)

class PickupCmd(Command):
    args = [None, Arg("item", False, False, True)]
    desc = "Picks up an item"

    def func(self, player, _updater, cmdstr):
        arg_split = good_split_spc(cmdstr, 1)
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

    def func(self, p, _u, _cmdstr):
        return p.showInventory()

class Help(Command):
    args = []
    desc = "Prints a summary of all commands"

    def __init__(self, commands):
        Command.__init__(self)

    def func(self, _p, _u, _cmdstr):
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

    def func(self, player, _updater, cmdstr):
        arg_split = good_split_spc(cmdstr, 1)
        targetName = arg_split[1]
        target = player.location.getMonsterByName(targetName)
        if target:
            player.attackMonster(target)
            return True
        else:
            raise CmdRunError("no such monster")

class LookCmd(Command):
    args = None
    desc = "Look around"

    def func(self, player, _updater, _cmdstr):
        printSituation(player)

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

    "look": LookCmd(),
    "pickup": PickupCmd(),
    "inventory": Inventory(),
    "exit": Exit(),
    "attack": Attack(),
}
commands["help"] = Help(commands) # Recursion!

def main(seed=random.randint(0, 2^64-1), replay=[]):
    createWorld()
    printSituation(player)
    new_replay = []
    while player.playing and player.alive:
        try:
            cmdstr = input("> ") # Does not have '\n' appended; I checked.
            cmd_split = good_split_spc(cmdstr)
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
                cmd_obj.func(player, updater, cmdstr)
        except CmdParseError as e: # Pass all other errors through, I guess.
            print("Error parsing command: " + str(e))
        except CmdRunError as e:
            print("Error running command: " + str(e))
        except EOFError:
            print()
            commands["exit"].func(player, updater, "^D")

main()
