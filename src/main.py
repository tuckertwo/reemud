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
    a = Room("A grassy field. Several animals graze placidly. Flowers poke out from the green grass. The sun shines, the sky is blue, but ahead of you, to the north, the dark gate of a crumbling ruin yawns\nTip: Try the command 'inspect instruction manual'")
    itm1 = item.Book("Instruction Manual", "Every year, according to Sacred Tradition, our village sends one human sacrifice to the Evil Necromancer Cultists. This year, you have been unwillingly elected to fill that role! But if you somehow manage to defeat the Necromancer, you can come back home I guess.\n(Type Help for a list of actions)")
    itm1.putInRoom(a)
    for x in range(5):
        monster.Sheep(a)
        
    #dungeon enterance
    b = Room("The entry-hall of the ruin is dark and reeks of mildew. Rubble from the high ceiling litters the ground.")
    Room.connectRooms(a, "north", b)
    itm3 = item.Book("Water-soiled Journal", "Death closes in on me.... if only I knew how to use the equip and unequip commands to don or doff weapons and armor... or if I knew how to use the unlock command to open a locked door... or if I knew how to use the attack command to attack a monster... or to type 'look' to repeat a room's description... alas, I am doomed")
    itm4 = item.Weapon("Blunt rock", "Be careful with that thing! You could bash someone's head in.", 3, 5)
    itm5 = item.Key("Rusted Key")
    itm3.putInRoom(b)
    itm4.putInRoom(b)
    x = monster.Rat(b, "rat with a key in its mouth")
    x.giveItem(itm5)

    #dungeon corridor
    c = Room("A long and gloomy corridor stretches down into the ruin. It is bisected by a river of slowly-flowing blood!")
    itm6 = item.Door(itm5, "north", c)
    itm6.putInRoom(b)
    monster.Skeleton(c)
    monster.Skeleton(c)
    
    #blood river shrine
    d = Room("The blood river seems to have its source here, beneath a gigantic statue of a grim-faced bronze king. Ghostly chanting echoes from afar.")
    Room.connectRooms(c, "north", d)
    monster.Cultist(a)
    
    
    
    
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
