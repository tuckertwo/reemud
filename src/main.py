#!/usr/bin/env python3
from room import Room
from player import Player
import item
import monster
import updater

from commands import commands, printSituation, pause
from txt_parser import CmdParseError, CmdRunError, good_split_spc, abbrev_cmd
import random, ast, sys, os

def createWorld():

    #starting room
    a = Room("A grassy field. Several animals graze placidly. Flowers poke out from the green grass. The sun shines, the sky is blue, but ahead of you, the dark gate of a crumbling structure yawns\nTip: Try the command 'inspect instruction manual'")
    itm = item.Book("Instruction Manual", "Every year, according to Sacred Tradition, our village sends one human sacrifice to the Evil Necromancer Cultists. This year, you have been unwillingly elected to fill that role! But if you somehow manage to defeat the Necromancer, you can come back home I guess.\n(Type Help for a list of actions)")
    itm.putInRoom(a)
    for x in range(5):
        monster.Sheep(a)



    player.location = a
    updater.allocateLoot()
        
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
                    if player.sneak: #That is right, I have sulled the main loop
                        player.isDetected()
                    elif len(player.location.getAggro()) > 0:
                        player.attackMonster(player.location.getAggro()[0], True) #If the player isn't sneaking, angry monsters will attack them
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
