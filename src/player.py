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
    def unequip(self, name):
        if not (self.weapon == None):
            if self.weapon.name.lower() == name.lower():
                self.items.append(self.weapon)
                self.weapon = None
                print(name + " unequipped!")
                return True
        if not (self.armor == None):
            if self.armor.name.lower() == name.lower():
                self.items.append(self.armor)
                self.armor = None
                print(name + " unequipped!")
                return True
        print ("You are already not wearing or weilding " + name)
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
        if not self.weapon == None:
            print("Equipped Weapon: " + self.weapon.name) #Note: currently weapons and armor don't factor into weight
        if not self.armor == None:
            print("Equipped Armor: " + self.armor.name)
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
    def takeDamage(self, amt):
        dam = int(random.random() * amt) + 1
        if not self.armor == None:
            dam = int(dam / self.armor.stren)
        self.health -= dam
        return dam

    def attackMonster(self, mon):
        mon.agg = True
        while len(self.location.getAggro()) > 0:
            if len(self.location.getAggro()) > 1:
                print(str(len(self.location.getAggro())) + " monsters confront you")
            else:
                print("A monster confronts you")
            n = 1
            for i in self.location.getAggro():
                print(str(n) + ". " + i.name + " with " + str(i.health) + " hp")
                n += 1
            print("Your health is at " + str(self.health) + " points")
            print()
            cmdstr = input("> ")
            try: #TODO: Implement replay capability
                if cmdstr:
                    cmd_split = good_split_spc(cmdstr)
                    cmd_obj   = attackcommands[abbrev_cmd(attackcommands.keys(),
                                            cmd_split[0],
                                            CmdParseError("ambiguous command"),
                                            CmdParseError("invalid commandx"))]
                    cmd_obj.func(self, updater, cmdstr)
                    if cmd_obj.sideeffects:
                        self.log.append(cmdstr)
                        for k in self.location.getAggro():
                            if k.health < 0:
                                k.die()
                        for j in self.location.getAggro():
                            attk = j.findAttack()
                            if random.random() < attk[3]:
                                    print(j.name + attk[0] + " for " + str(self.takeDamage(attk[2])) + " damage!") #TODO: add effects
                            else:
                                print(j.name + attk[1])
                                
                        if self.health <= 0: #everything here is to be eventually elaborated on
                            print("You have died.")
                            self.alive = False
                    
                else:
                    print("Well I guess you're doing nothing (type Help for battle-commands)")
                        
            except CmdParseError as e: # Pass all other errors through, I guess.
                print("Error parsing command: " + str(e))
            except CmdRunError as e:
                print("Error running command: " + str(e))
            except EOFError:
                print("End-Of_File Error")
                

                



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
        printSituation(player)

class Equip(Command):
    args = [None, Arg("item", False, False, True)]
    desc = "Equips a Weapon or Armour Suit"
    sideeffects = True

    def func_ap(self, player, _updater, args_parsed):
        targetName = args_parsed["item"]
        player.equip(targetName)
        
class UnEquip(Command):
    args = [None, Arg("item", False, False, True)]
    desc = "Unequips a Weapon or Armour Suit"
    sideeffects = True
    
    def func_ap(self, player, _updater, args_parsed):
        targetName = args_parsed["item"]
        player.unequip(targetName)
        
class Hit(Command):
    args = [None, Arg("monster", False, False, True)]
    desc = "Hit the monster."
    sideeffects = True

    def func_ap(self, player, _updater, args_parsed):
        targetName = args_parsed["monster"]
        target = player.location.getMonsterByName(targetName)
        if target:
            if player.weapon == None:
                print("You punch " + targetName + " with your fists for " + str(target.takeDamage(1 + player.skill[1])) + " damage")
            else:
                print("You hit " + targetName + " with " + player.weapon.name + " for " + str(target.takeDamage(player.weapon.damage + player.skill[1])) + " damage")
            return True
        else:
            raise CmdRunError("no such monster")

attackcommands = {
    "flee": Flee(None),
    "equip": Equip(),
    "unequip": UnEquip(),
    "hit": Hit()
}

