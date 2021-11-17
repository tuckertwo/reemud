#!/usr/bin/env python3
from room import Room
from player import Player
from item import Item
from monster import Monster
import os
import updater

from commands import commands, printSituation
from txt_parser import CmdParseError, CmdRunError, good_split_spc
import random

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

def main(seed=random.randint(0, 2^64-1), replay=[]):
    createWorld()
    printSituation(player)
    new_replay = []
    while player.playing and player.alive:
        try:
            cmdstr = input("> ") # Does not have '\n' appended; I checked.
            if cmdstr:
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
