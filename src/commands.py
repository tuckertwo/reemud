from txt_parser import good_split_spc, Arg, Command, CmdRunError
import time
import os

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

class Attack(Command):
    args = [None, Arg("monster", False, False, True)]
    desc = "Attacks a monster"
    sideeffects = False #appended in a different way

    def func_ap(self, player, _updater, args_parsed):
        targetName = args_parsed["monster"]
        target = player.location.getMonsterByName(targetName)
        if target:
            player.attackMonster(target)
            return True
        else:
            raise CmdRunError("no such monster")

class ApplyTo(Command):
    args = [None, Arg("x to y", False, False, True)]
    desc = "applies a potion or spell scroll to a weapon"
    sideeffects = True
    
    def func_ap(self, player, _updater, args_parsed):
        targetName = args_parsed["x to y"] 
        objex = targetName.lower().split(" to ")
        if len(objex) == 2:
            target = player.getItemByName(objex[0])
            if target:
                if target.potion or target.scroll:
                    weapon = player.getItemByName(objex[1])
                    if weapon:
                        if weapon.weapon:
                            target.applyTo(weapon)
                            player.removeItem(target)
                        else:
                            raise CmdRunError(objex[1] + " is not a weapon")
                    else:
                        raise CmdRunError("you don't have " + objex[1] + " in inventory")
                else:
                    raise CmdRunError(objex[0] + " is not a potion or spell scroll")
            else:
                raise CmdRunError("you don't have " + objex[0] + " in inventory")
        else:
            raise CmdRunError("Incorrect number of arguments")

class Cast(Command):
    args = [None, Arg("spell scroll", False, False, True)]
    desc = "Cast a spell scroll"
    sideeffects = True
    
    def func_ap(self, player, _updater, args_parsed):
        ssname = args_parsed["spell scroll"]
        sscroll = player.getItemByName(ssname)
        if sscroll:
            if sscroll.effect[0] == "heal":
                player.heal(9999999)
                player.removeItem(sscroll)
            elif sscroll.effect[0] == "fire":
                print("You scorch the ground with a huge (but useless) fireball!")
                player.location.desc = player.location.desc + " The ground is scorched and blackened."
                player.removeItem(sscroll)
            else:
                print("You have no opponents to use this spell scroll against")

        else:
            raise CmdRunError("you don't have any such spell scroll")
        


class ClearScreenCmd(Command):
    args = []
    desc = "Clear the screen"
    sideeffects = False

    def func(self, _player, _updater, _cmdstr):
        clear()

class DrinkCmd(Command):
    args = [None, Arg("item", False, False, True)]
    desc = "Drinks a potion"
    sideeffects = True
    
    def func_ap(self, player, _updater, args_parsed):
        targetName = args_parsed["item"]
        player.drink(targetName)

class DropCmd(Command):
    args = [None, Arg("item", False, False, True)]
    desc = "Drops an item"
    sideeffects = True
    
    def func_ap(self, player, _updater, args_parsed):
        targetName = args_parsed["item"] 
        target = player.getItemByName(targetName)
        if target:
            player.location.addItem(target)
            player.removeItem(target)
            return True
        else:
            raise CmdRunError("no such item in inventory")

class EchoCmd(Command):
    args = [None, Arg("string", False, False, True)]
    desc = "Echo a string"
    sideeffects = False

    # To-do: re-write the parser to make infinite args actually capture
    # strings instead of split strings
    def func_ap(self, _p, _u, args_parsed):
        print(" ".join(args_parsed["string"]))

class Equip(Command):
    args = [None, Arg("item", False, False, True)]
    desc = "Equips a Weapon or Armour Suit"
    sideeffects = True

    def func_ap(self, player, _updater, args_parsed):
        targetName = args_parsed["item"]
        player.equip(targetName)
     

class Exit(Command):
    args = []
    desc = "Exits the game"
    sideeffects = False # Well, really it does but we don't want it recorded in
                        # the save nevertheless

    def func(self, p, _u, _cmdstr):
        p.playing = False

class GoCmd(Command):
    sideeffects = True

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

class Help(Command):
    args = []
    desc = "Prints a summary of all commands"
    sideeffects = False

    def __init__(self, commands):
        Command.__init__(self)
        self.commands = commands

    def func(self, _p, _u, _cmdstr):
        commands_full = {}
        commands_full.update(self.commands)
        commands_full.update({"help": self}) # Recursion has its limits
        helptext = "{:>10}   {:15}       {}\n".format("Command",
                                                     "Arguments", "Description")
        for k, v in commands_full.items():
            helptext += "{:>10}:  {:15}       {}\n".format(k, v.args_hr, v.desc)
        print(helptext)


class InspectCmd(Command):
    args = [None, Arg("item", False, False, True)]
    desc = "Inspects an item"
    sideeffects = False

    def func_ap(self, player, updater, args_parsed):
        targetName = args_parsed["item"]
        player.inspect(targetName)

class Inventory(Command):
    args = []
    desc = "Prints the player's inventory"
    sideeffects = False

    def func(self, p, _u, _cmdstr):
        return p.showInventory()

class LevelUpCmd(Command):
    args = [None, Arg("up", True, True, True)]
    desc = "Levels up, if you have enough xp"
    sideeffects = False #appended in a different way

    def func(self, player, _updater, _cmdstr):
        player.levelUpHelper()

class Lock(Command):
    args = [None, Arg("object", False, False, True)]
    desc = "Lock a container"
    sideeffects = True
    
    def func_ap(self, player, _updater, args_parsed):
        targetName = args_parsed["object"] 
        target = player.location.getItemByName(targetName)
        if target:
            if target.container:
                keys = []
                for x in player.items:
                    if x.key:
                        keys.append(x)
                target.lock(keys, player)
            else:
                raise CmdRunError("This is not a container!")
        else:
            raise CmdRunError("no such thing in room")


class LookCmd(Command):
    args = []
    desc = "Look around"
    sideeffects = False

    def func(self, player, _updater, _cmdstr):
        printSituation(player)

class Me(Command):
    args = []
    desc = "gives a summary of your condition"
    sideeffects = False
    
    def func(self, player, _updater, args_passed):
        return player.showStats()

class PauseCmd(Command):
    args = []
    desc = "Pause for user input"
    sideeffects = False

    def func_ap(self, p, _u, _args_parsed):
        pause()

class PickupCmd(Command):
    args = [None, Arg("up", True, False, False), Arg("item", False, False, True)]
    desc = "Picks up an item"
    sideeffects = True

    def func_ap(self, player, updater, args_parsed):
        targetName = args_parsed["item"]
        target = player.location.getItemByName(targetName)
        if target:
            player.pickup(target, updater)
        else:
            raise CmdRunError("no such item")
          

class PutinCmd(Command):
    args = [None, Arg("x in y", False, False, True)]
    desc = "puts an item in a container"
    sideeffects = True
    
    def func_ap(self, player, _updater, args_parsed):
        targetName = args_parsed["x in y"] 
        objex = targetName.lower().split(" in ")
        if len(objex) == 2:
            target = player.getItemByName(objex[0])
            if target:
                container = player.location.getItemByName(objex[1])
                if container:
                    if container.container:
                        if not container.locked:
                            container.putInside(target)
                            player.removeItem(target)
                        else:
                            print("The " + container.name + " is locked!")
                else:
                    raise CmdRunError("no such container")
            else:
                raise CmdRunError("no such item in inventory")
        else:
            raise CmdRunError("Incorrect number of arguments")


class SaveCmd(Command):
    # Attention: this saves a complete log of every salient action taken
    # by the player.
    # This means that a save file can be used for later analysis of games.
    # This *also* means that save files aren't compatible between versions.
    args = [None, Arg("file", False, False, False)]
    desc = "Save the game to a file on disk."
    sideeffects = False

    def func_ap(self, p, _u, args_parsed):
        with open(args_parsed["file"], "w") as f:
            f.write(repr((p.seed, p.log)))
            f.write("\n")

class SleepCmd(Command):
    args = [None, Arg("time", False, False, False)]
    desc = "Wait for a specific time in seconds"
    sideeffects = False

    def func_ap(self, _p, _u, args_parsed):
        time.sleep(float(args_parsed["time"]))

class SneakCmd(Command):
    args = []
    desc = "Begin sneaking"
    sideeffects = True

    def func(self, _player, _updater, _cmdstr):
        _player.sneak = True

class UnEquip(Command):
    args = [None, Arg("item", False, False, True)]
    desc = "Unequips a Weapon or Armour Suit"
    sideeffects = True
    
    def func_ap(self, player, _updater, args_parsed):
        targetName = args_parsed["item"]
        player.unequip(targetName)
      
class Unlock(Command):
    args = [None, Arg("object", False, False, True)]
    desc = "Unlock a container or door"
    sideeffects = True
    
    def func_ap(self, player, _updater, args_parsed):
        targetName = args_parsed["object"] 
        target = player.location.getItemByName(targetName)
        if target:
            if target.door or target.container:
                keys = []
                for x in player.items:
                    if x.key:
                        keys.append(x)
                target.unlock(keys, player)
            else:
                raise CmdRunError("This is not a container or a door!")
        else:
            raise CmdRunError("no such thing in room")


class WaitCmd(Command):
    args = [None, Arg("for", True, True, False),
            Arg("time", False, True, False), Arg("seconds", True, True, False)]
    desc = "Waits for time to pass"
    sideeffects = True

    def func_ap(self, _p, u, args_parsed):
        if "time" in args_parsed:
            if type(args_parsed["time"]) == int:
                time = args_parsed["time"]
        else:
            time = 1
        for i in range(time+1):
            u.updateAll()

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

    # Commands useful for demos
    "cls": ClearScreenCmd(),
    "clear": ClearScreenCmd(),
    "pause": PauseCmd(),
    "echo": EchoCmd(),
    "sleep": SleepCmd(),

    "look": LookCmd(),
    "sneak": SneakCmd(),
    "pickup": PickupCmd(),
    "take": PickupCmd(),
    "drop": DropCmd(),
    "put": PutinCmd(),
    "drink": DrinkCmd(),
    "cast": Cast(),
    "inventory": Inventory(),
    "inspect": InspectCmd(),
    "unlock": Unlock(),
    "lock": Lock(),
    "apply": ApplyTo(),
    "equip": Equip(),
    "unequip": UnEquip(),
    "me": Me(),
    "level": LevelUpCmd(),
    "exit": Exit(),
    "attack": Attack(),
    "wait": WaitCmd(),

    "save": SaveCmd(),
}
commands["help"] = Help(commands) # Recursion!
