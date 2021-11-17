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

class PickupCmd(Command):
    args = [None, Arg("up", True, False, False), Arg("item", False, False, True)]
    desc = "Picks up an item"
    sideeffects = True

    def func_ap(self, player, _updater, args_parsed):
        targetName = args_parsed["item"]
        target = player.location.getItemByName(targetName)
        if target:
            player.pickup(target)
            return True
        else:
            raise CmdRunError("no such item")

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
            raise CmdRunError("no sun item in inventory")

class Inventory(Command):
    args = []
    desc = "Prints the player's inventory"
    sideeffects = False

    def func(self, p, _u, _cmdstr):
        return p.showInventory()

class Me(Command)
    args = []
    desc = "gives a summary of your condition"
    sideeffects = False
    
    def func(self, player, _updater, args_passed):
        return player.showStats()
    
class Help(Command):
    args = []
    desc = "Prints a summary of all commands"
    sideeffects = False

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
    sideeffects = False # Well, really it does but we don't want it recorded in
                        # the save nevertheless

    def func(self, p, _u, _cmdstr):
        p.playing = False

class Attack(Command):
    args = [None, Arg("monster", False, False, True)]
    desc = "Attacks a monster"
    sideeffects = True

    def func_ap(self, player, _updater, args_parsed):
        targetName = args_parsed["monster"]
        target = player.location.getMonsterByName(targetName)
        if target:
            player.attackMonster(target)
            return True
        else:
            raise CmdRunError("no such monster")

class LookCmd(Command):
    args = []
    desc = "Look around"
    sideeffects = False

    def func(self, player, _updater, _cmdstr):
        printSituation(player)

class ClearScreenCmd(Command):
    args = []
    desc = "Clear the screen"
    sideeffects = False

    def func(self, _player, _updater, _cmdstr):
        clear()

class PauseCmd(Command):
    args = []
    desc = "Pause for user input"
    sideeffects = False

    def func_ap(self, p, _u, _args_parsed):
        pause()

class EchoCmd(Command):
    args = [None, Arg("string", False, False, True)]
    desc = "Echo a string"
    sideeffects = False

    # To-do: re-write the parser to make infinite args actually capture
    # strings instead of split strings
    def func_ap(self, _p, _u, args_parsed):
        print(" ".join(args_parsed["string"]))

class SleepCmd(Command):
    args = [None, Arg("time", False, False, False)]
    desc = "Wait for a specific time in seconds"
    sideeffects = False

    def func_ap(self, _p, _u, args_parsed):
        time.sleep(float(args_parsed["time"]))

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

class WaitCmd(Command):
    args = [None, Arg("for", True, True, False),
            Arg("time", False, True, False), Arg("seconds", True, True, False)]
    desc = "Waits for time to pass"

    def func_ap(self, _p, u, args_parsed):
        if "time" in args_parsed:
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
    "pickup": PickupCmd(),
    "drop": DropCmd(),
    "inventory": Inventory(),
    "me": Me(),
    "exit": Exit(),
    "attack": Attack(),
    "wait": WaitCmd(),

    "save": SaveCmd(),
}
commands["help"] = Help(commands) # Recursion!
