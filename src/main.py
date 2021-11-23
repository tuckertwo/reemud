#!/usr/bin/env python3
from room import Room
from player import Player
from item import Item, Weapon, Armor
import monster
import updater

from commands import commands, printSituation, pause
from txt_parser import CmdParseError, CmdRunError, good_split_spc, abbrev_cmd
import random, ast, sys, os

def createWorld():
    a = Room("You are in room 1")
    b = Room("You are in room 2")
    c = Room("You are in room 3")
    d = Room("You are in room 4")
    Room.connectRooms(a, "east", b, "west")
    Room.connectRooms(c, "east", d, "west")
    Room.connectRooms(a, "north", c, "south")
    Room.connectRooms(b, "north", d, "south")
    i = Item("Rock", "This is just a rock.", 5)
    i.putInRoom(b)
    i = Item("Rock", "This is just a rock.", 5)
    j = Weapon("Rock", "A sharp rock that might hurt somebody.", 5, 5)
    i.putInRoom(c)
    j.putInRoom(c)
    i = Item("Orange Clock", "This is not a rock.")
    i.putInRoom(c)
    player.location = a
    for x in range(10):
        monster.Skeleton(b)
        
class Game:
    def __init__(self, replay=[], rep_flag=False):
        self.replay = replay
        self.rep_flag = rep_flag
    
    def main(self):
        createWorld()
        printSituation(player)
        while player.playing and player.alive:
            try:
                if self.replay:
                    cmdstr   = self.replay[0]
                    print(cmdstr)
                    self.replay   = self.replay[1:]
                    self.rep_flag = True
                else:
                    if self.rep_flag:
                        print("-------------------- Save loaded.")
                        pause()
                        self.rep_flag = False
                    cmdstr = input("> ") # Does not have '\n' appended; I checked.

                if cmdstr:
                    cmd_split = good_split_spc(cmdstr)
                    cmd_obj   = commands[abbrev_cmd(commands.keys(),
                                            cmd_split[0],
                                            CmdParseError("ambiguous command"),
                                            CmdParseError("invalid command"))]
                    cmd_obj.func(player, updater, cmdstr)
                    if cmd_obj.sideeffects:
                        player.log.append(cmdstr)
            except CmdParseError as e: # Pass all other errors through, I guess.
                print("Error parsing command: " + str(e))
            except CmdRunError as e:
                print("Error running command: " + str(e))
            except EOFError:
                print()
                commands["exit"].func(player, updater, "^D")




if len(sys.argv) > 1:
    seed, log = ast.literal_eval(open(sys.argv[1]).read())
    game = Game(log, True)
    player = Player(game, seed)
    game.main()
else:
    game = Game()
    player = Player(game)
    game.main()
