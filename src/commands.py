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

class ClearScreenCmd(Command):
    args = None
    desc = "Clear the screen"

    def func(self, _player, _updater, _cmdstr):
        clear()

class PauseCmd(Command):
    args = None
    desc = "Pause for user input"

    def func_ap(self, p, _u, _args_parsed):
        pause()

class EchoCmd(Command):
    args = [None, Arg("string", False, False, True)]
    desc = "Echo a string"

    # To-do: re-write the parser to make infinite args actually capture
    # strings instead of split strings
    def func_ap(self, _p, _u, args_parsed):
        print(" ".join(args_parsed["string"]))

class SleepCmd(Command):
    args = [None, Arg("time", False, False, False)]
    desc = "Wait for a specific time in seconds"

    def func_ap(self, _p, _u, args_parsed):
        time.sleep(float(args_parsed["time"]))

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
    "inventory": Inventory(),
    "exit": Exit(),
    "attack": Attack(),
}
commands["help"] = Help(commands) # Recursion!
