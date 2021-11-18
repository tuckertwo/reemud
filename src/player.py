import os, random
from commands import commands, printSituation, pause
from txt_parser import CmdParseError, CmdRunError, good_split_spc, abbrev_cmd, Arg, Command
import updater

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

class Player:
    def __init__(self, seed=random.randint(0, 2^64-1)):
        # Stuff will get screwy if there are multiple Player()s with different
        # seeds, but that is an eventuality that seems unlikely to occur.
        # (Famous last words.)
        self.seed = seed
        random.seed(seed)
        self.log = []
        self.playing = True
        self.location = None
        self.items = []
        self.health = 50
        self.maxhealth = 50
        self.weapon = None
        self.armor = None
        self.weightlimit = 10
        self.groan_threshold = 2
        self.alive = True
        self.level = 1
        self.skill = [0, 0, 0, 0] #base scores for dexterity, strength, constitution, and magical skill
    def goDirection(self, direction):
        newloc = self.location.getDestination(direction)
        if newloc is None:
            raise CmdRunError("no such location")
        else:
            self.location = newloc
    def pickup(self, item):
        self.items.append(item)
        item.loc = self
        self.location.removeItem(item)
    def equip(self, name):
        item = self.getItemByName(name)
        if item:
            if item.weapon:
                if self.weapon == None:
                    self.weapon = item
                    print(item.name + " equipped!")
                else:
                    print("You have a weapon already equipped! What are you, ambidexterous?")
            elif item.armor:
                if self.armor == None:
                    self.armor = item
                    print(item.name + " equipped!")
                else:
                    print("You can't wear two suits of armor at once!")
            else:
                print("That is not a weapon or armor!")
        else:
            print("Item Not In Inventory")
    def getItemByName(self, name):
        for i in self.items: #note- to be improved later so exact names aren't needed
            if i.name.lower() == name.lower():
                return i
        return False
    def removeItem(self, item):
        if item in self.items:
            self.items.remove(item)
    def heal(self, amount):
        self.health += amount
        if self.health > self.maxhealth:
            self.health = self.maxhealth
            print("Healed to full health (" + self.maxhealth + " hp)")
        else:
            print("Healed by " + amount + " hp")
    def showInventory(self):
        print("You are currently carrying:")
        items_dict = {}
        weight_dict = {}
        for i in self.items:
            if i.name in items_dict:
                items_dict[i.name] += 1
                weight_dict[i.name] += i.weight
            else:
                items_dict[i.name] = 1
                weight_dict[i.name] = i.weight
        for name, num in items_dict.items():
            # Weight is a mess
            print("{:>10} ×{:02}, {:02} kg".format(name, num,
                                                   weight_dict[name]))
        print()
    def showStats(self):
        print("Current Health: " + str(self.health) + " out of " + str(self.maxhealth))
        print("Dexterity: +" + str(self.skill[0]))
        print("Strength: +" + str(self.skill[1]))
        print("Constitution: +" + str(self.skill[2]))
        print("Magical Skill: +" + str(self.skill[3]))
        print()
    def getItemByName(self, name):
        for i in self.items:
            if i.name.lower() == name.lower():
                return i
        return False
    def removeItem(self, item):
        if item in self.items:
            self.items.remove(item)


    def attackMonster(self, mon):
        mon.agg = True
        while len(self.location.getAggro()) > 0:
            if len(self.location.getAggro()) > 1:
                print(str(len(self.location.getAggro())) + " monsters confront you")
            else:
                print("A monster confronts you")
            n = 1
            for i in self.location.getMonsters():
                print(str(n) + ". " + i.name + " with " + str(i.health) + " hp")
                n += 1
            print("What will you do?")
            cmdstr = input("> ") #I'll integrate this into the command system as a whole in the future. Placeholder for now
            if cmdstr:
                cmd_split = good_split_spc(cmdstr)
                cmd_obj   = attackcommands[abbrev_cmd(attackcommands.keys(),
                                        cmd_split[0],
                                        CmdParseError("ambiguous command"),
                                        CmdParseError("invalid command"))]
                cmd_obj.func(self, updater, cmdstr)
                if cmd_obj.sideeffects:
                    self.log.append(cmdstr)
            else:
                print("Well I guess you're doing nothing")





      #  print("You are attacking " + mon.name)
      #  print("Your health is " + str(self.health) + ".")
      #  print(mon.name + "'s health is " + str(mon.health) + ".")
      #  if self.health > mon.health:
      #      self.health -= mon.health
      #      print("You win. Your health is now " + str(self.health) + ".")
      #      mon.die()
      #  else:
      #      print("You lose.")
      #      self.alive = False
      #  print()

class Flee(Command):
    sideeffects = True

    def __init__(self, direction=None):
        if direction is not None:
            self.desc = "Flees {}".format(direction)
            self.args = []
            self.direction = direction
        else:
            self.desc = "Flees in the given direction"
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

class Equip(Command):
    args = [None, Arg("item", False, False, True)]
    desc = "Equips a Weapon or Armour Suit"
    sideeffects = True

    def func_ap(self, player, _updater, args_parsed):
        targetName = args_parsed["item"]
        player.equip(targetName)

attackcommands = {
    "flee": Flee(),
    "eluip": Equip()
}

