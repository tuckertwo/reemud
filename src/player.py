import os, random
import commands
from txt_parser import CmdParseError, CmdRunError, good_split_spc, abbrev_cmd, Arg, Command
import updater

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

class Player:
    def __init__(self, game, seed=random.randint(0, 2^64-1)):
        # Stuff will get screwy if there are multiple Player()s with different
        # seeds, but that is an eventuality that seems unlikely to occur.
        # (Famous last words.)
        self.seed = seed
        random.seed(seed)
        self.game = game
        self.log = []
        self.playing = True
        self.location = None
        self.name = "Player"
        self.items = []
        self.health = 50
        self.maxhealth = 50
        self.xp = 0
        self.condition = {}
        self.weapon = None
        self.armor = None
        self.weightlimit = 10
        self.groan_threshold = 2
        self.alive = True
        self.level = 1
        self.skill = [0, 0, 0, 0] #base scores for dexterity, strength, constitution, and intelligence
        self.sneak = False
        updater.register(self)
    def update(self):
        self.effectsOccur()
    def levelUpHelper(self):
        self.log.append("level")
        if self.xp < 100:
            print("You are " + str(100 - self.xp) + " xp away from levelling up")
        while self.xp >= 100:
            self.xp -= 100
            self.levelUp()
            
    def levelUp(self):
        self.level += 1
        print("You have enough xp to level up!")
        self.showStats()
        print("What stat would you like to improve?")
        notdone = True
        while notdone:
            if self.game.replay:
                        cmdstr   = self.game.replay[0]
                        self.game.replay   = self.game.replay[1:]
                        self.game.rep_flag = True
            else:
                if self.game.rep_flag:
                    print("-------------------- Save loaded.")
                    commands.pause()
                    self.game.rep_flag = False
                cmdstr = input("> ")
            d = "dexterity"
            s = "strength"
            c = "constitution"
            m = "intelligence"
            notdone = False
            if cmdstr.lower() == d[0:len(cmdstr)]: #primitive version of the command parser
                print("Dexterity increased!")
                self.skill[0] += 1
            elif cmdstr.lower() == s[0:len(cmdstr)]:
                print("Strength increased!")
                self.skill[1] += 1
            elif cmdstr.lower() == c[0:len(cmdstr)]:
                print("Constitution increased!")
                self.skill[2] += 1
                self.maxhealth += 10
            elif cmdstr.lower() == m[0:len(cmdstr)]:
                print("Intelligence increased!")
                self.skill[3] += 1
            else:
                print("Error: Stat not found")
                notdone = True
        self.log.append(cmdstr)
            
    def goDirection(self, direction):
        newloc = self.location.getDestination(direction)
        if newloc is None:
            raise CmdRunError("no such location")
        else:
            self.location = newloc
    def isDetected(self):
        for x in self.location.getAggro():
            if random.random() < (x.perception * (.3 - (self.skill[0] / 15))):
                print("You have been detected by " + x.name + "!")
                self.sneak = False
                self.attackMonster(x)
    def pickup(self, item, updater):
        total_weight = sum([i.weight for i in self.items])
        if total_weight+item.weight>self.weightlimit:
            raise CmdRunError("item too heavy to put in inventory")
        else:
            if item.weight >= self.groan_threshold:
                for i in range(item.weight//self.groan_threshold+1):
                    updater.updateAll()
                    print("You strain yourself")
            self.items.append(item)
            item.loc = self
            self.location.removeItem(item)
    def equip(self, name):
        item = self.getItemByName(name)
        if item:
            if item.weapon:
                if self.weapon == None:
                    self.weapon = item
                    self.items.remove(item)
                    print(item.name + " equipped!")
                else:
                    print("You have a weapon already equipped! What are you, ambidexterous?")
            elif item.armor:
                if self.armor == None:
                    self.armor = item
                    self.items.remove(item)
                    print(item.name + " equipped!")
                else:
                    print("You can't wear two suits of armor at once!")
            else:
                print("That is not a weapon or armor!")
        else:
            print("Item Not In Inventory")
    def inspect(self, name):
        item = self.location.getItemByName(name)
        if not item:
            item = self.getItemByName(name) #checks room before inventory
        
        if item:
            item.describe()
        else:
            print("Error: Item not found!")
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
    def drink(self, name):
        item = self.getItemByName(name)
        if item:
            if item.potion:
                print("You drink the " + name)
                item.drink(self)
                self.items.remove(item)
            else:
                print("You can't drink your " + name + "!")
        else:
            print("Item Not In Inventory")
    def getItemByName(self, name):
        for i in self.items: #note- to be improved later so exact names aren't needed
            if i.name.lower() == name.lower():
                return i
        return False
    def heal(self, amount):
        self.health += amount
        if self.health > self.maxhealth:
            self.health = self.maxhealth
            print("Healed to full health (" + str(self.maxhealth) + " hp)")
        else:
            print("Healed by " + str(amount) + " hp")
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
        print("Level: " + str(self.level))
        print("Experience to next level: " + str(100 - self.xp))
        print("Current Health: " + str(self.health) + " out of " + str(self.maxhealth))
        print("Dexterity: +" + str(self.skill[0]))
        print("Strength: +" + str(self.skill[1]))
        print("Constitution: +" + str(self.skill[2]))
        print("Intelligence: +" + str(self.skill[3]))
        print()
    def getItemByName(self, name):
        for i in self.items:
            if i.name.lower() == name.lower():
                return i
        return False
    def removeItem(self, item):
        if item in self.items:
            self.items.remove(item)
    def takeDamage(self, amt, ignorearmor=False):
        dam = int(random.random() * amt) + 1
        if not ((self.armor == None) or ignorearmor):
            dam = int(dam / self.armor.stren)
        self.health -= dam
        if self.health <= 0:
            print("You have died.")
            self.alive = False
        return dam
    def applyEffects(self, effex):
        for x in effex:
            self.applyEffect(x[0], x[1])
    def applyEffect(self, effect, amount=0):
        if effect == "poison":
            if "poison" in self.condition:
                self.condition["poison"] = self.condition["poison"] + amount
                print("You are poisoned (even more than before)")
            else:
                self.condition["poison"] = amount
                print("You are poisoned!")
        elif effect == "antidote":
            if "poison" in self.condition:
                print("All poison has been removed from your bloodstream")
                self.condition.pop("poison")
            else:
                print("There wasn't any poison in your bloodstream to remove")
        elif effect == "heal":
            self.heal(amount)
        elif effect == "fire":
            if "fire" in self.condition:
                self.condition["fire"] = self.condition["fire"] + amount
                print("You are inflamed with more fire!")
            else:
                self.condition["fire"] = amount
                print("You are set on fire!")
        elif effect == "regeneration":
            if "regeneration" in self.condition:
                self.condition["regeneration"] = self.condition["regeneration"] + amount
                print("The magical regeneration is boosted")
            else:
                self.condition["regeneration"] = amount
                print("Magical regeneration heals your body")
        elif effect == "water":
            if "fire" in self.condition:
                print("The fire was extinguished")
            self.condition.pop("fire")
    def effectsOccur(self):
        if "poison" in self.condition:
            dam = int(random.random() * self.condition["poison"])
            print("You take " + str(dam) + " points of poison damage")
            self.takeDamage(dam, True)    
        if "fire" in self.condition:
            dam = int(random.random() * self.condition["fire"])
            print("You take " + str(dam) + " damage from the fire")
            self.takeDamage(dam, True)
            self.condition["fire"] -= 2
            if self.condition["fire"] < 0:
                print("The fire is extinguished")
                self.condition.pop("fire")
        if "regeneration" in self.condition:
            hal = int(random.random() * self.condition["regeneration"])
            print("You regenerate " + str(hal) " hp")
            self.heal(hal)
            self.condition["regenerate"] -= 2
            if self.condition["regenerate"] < 0:
                print("The regeneration wears off")
    def attackMonster(self, mon, attacked=False):
        mon.agg = True
        if not attacked:
            self.log.append("attack " + mon.name)
        while (len(self.location.getAggro()) > 0) and self.alive and self.playing:
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
            try: 
                if self.game.replay:
                    cmdstr   = self.game.replay[0]
                    self.game.replay   = self.game.replay[1:]
                    self.game.rep_flag = True
                else:
                    if self.game.rep_flag:
                        print("-------------------- Save loaded.")
                        commands.pause()
                        self.game.rep_flag = False
                    cmdstr = input("> ")

                if cmdstr:
                    cmd_split = good_split_spc(cmdstr)
                    cmd_obj   = attackcommands[abbrev_cmd(attackcommands.keys(),
                                            cmd_split[0],
                                            CmdParseError("ambiguous command"),
                                            CmdParseError("invalid commandx"))]
                    cmd_obj.func(self, updater, cmdstr)
                    if cmd_obj.sideeffects:
                        self.log.append(cmdstr)
                        self.effectsOccur()
                        for k in self.location.getAggro():
                            k.effectsOccur()
                            if k.health <= 0:
                                if k.isDead():
                                    xp0 = int(k.xp / self.level)
                                    k.die()
                                    if xp0 > 0:
                                        print("You gain " + str(xp0) + " xp")
                                        self.xp += xp0
                        for j in self.location.getAggro():
                            attk = j.findAttack()
                            if not (attk == None):
                                if random.random() < attk[3]:
                                        print(j.name + attk[0] + " for " + str(self.takeDamage(attk[2])) + " damage!") #TODO: add effects
                                        if not (attk[6] == None):
                                            self.applyEffects(attk[6])
                                else:
                                    print(j.name + attk[1])
                                
                    
                else:
                    print("Well I guess you're doing nothing (type Help for battle-commands)")
                        
            except CmdParseError as e: # Pass all other errors through, I guess.
                print("Error parsing command: " + str(e))
            except CmdRunError as e:
                print("Error running command: " + str(e))
            except EOFError:
                print("End-Of_File Error")
                

                

class Flee(Command):
    desc = "Flees the battle"
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
        commands.printSituation(player)



        
class WaitCmd(Command):
    args = [None]
    desc = "Waits for time to pass"
    sideeffects = True

    def func_ap(self, _p, u, useless):
        print("You do nothing in battle")
        
class Disarm(Command):
    args = [None, Arg("monster", False, False, True)]
    desc = "Attempt to disarm a monster's weapons"
    sideeffects = True       
    
    def func_ap(self, player, _updater, args_parsed):
        targetName = args_parsed["monster"]
        target = player.location.getMonsterByName(targetName)
        if target:
            target.disarm(player.skill[1])
        else:
            raise CmdRunError("no such monster")

class Hit(Command):
    args = [None, Arg("monster", False, False, True)]
    desc = "Hit the monster."
    sideeffects = True

    def func_ap(self, player, _updater, args_parsed):
        targetName = args_parsed["monster"]
        target = player.location.getMonsterByName(targetName)
        if target:
            if random.random() < (.3 + (player.skill[0] / 15)):
                if player.weapon == None:
                    print("You punch " + targetName + " with your fists for " + str(target.takeDamage(1 + player.skill[1])) + " damage")
                else:
                    print("You hit " + targetName + " with " + player.weapon.name + " for " + str(target.takeDamage(player.weapon.damage + player.skill[1])) + " damage")
            else:
                print("You try to hit " + targetName + " but miss")
        else:
            raise CmdRunError("no such monster")

attackcommands = {
    "flee": Flee(None), #flee differs from  go in that flee doesn't update monster positions
    "north": Flee("north"),
    "n": Flee("north"),
    "south": Flee("south"),
    "s": Flee("south"),
    "east": Flee("east"),
    "e": Flee("east"),
    "west": Flee("west"),
    "w": Flee("west"),


    #Commands imported from commands.py
    "look": commands.LookCmd(),
    "pickup": commands.PickupCmd(),
    "drop": commands.DropCmd(),
    "drink": commands.DrinkCmd(),
    "inventory": commands.Inventory(),
    "inspect": commands.InspectCmd(),
    "equip": commands.Equip(),
    "unequip": commands.UnEquip(),
    "me": commands.Me(),
    "exit": commands.Exit(),
    "save": commands.SaveCmd(),
    
    
    "wait": WaitCmd(),
    "hit": Hit(),
    "disarm": Disarm(),
    
}
attackcommands["help"] = commands.Help(attackcommands) 

