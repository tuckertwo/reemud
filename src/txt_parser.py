def good_split_spc(string, limit=-1):
    return list(filter(lambda x: len(x) > 0, string.split(' ', limit)))


# This is really just a struct.
class Arg():
    def __init__(self, name, nonsense=False, optional=False, infinite=False):
        self.name = name
        self.nonsense = nonsense
        self.optional = optional
        self.infinite = infinite

    def __repr__(self):
        r = self.name
        if self.nonsense:
            r = "({})".format(r)
        if self.optional:
            r = "[{}]".format(r)
        if self.infinite:
            r = "{}+".format(r)
        return r

class CmdRunError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value

class CmdParseError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value

class Command():
    def __init__(self):
        if not hasattr(self, "args_hr"):
            if self.args is not None and len(self.args) >= 2:
                self.args_hr = " ".join([str(x) for x in self.args[1:]])
            else:
                self.args_hr = ""

    def func(self, p, u, cmdstr):
        return self.func_ap(p, u, self.cmdparse(cmdstr))

    def cmdparse(self, cmdstr):
        # Awful mutable data stuff ahead
        def parser(args_parsed, cmdstr, args_to_fill):
            # If out of stuff to parse
            if len(cmdstr) == 0:
                # Premature end?
                if len(args_to_fill) == 0 or args_to_fill[0].optional or \
                    (args_to_fill[0].infinite and
                     args_to_fill[0].name in args_parsed):
                    return args_parsed
                else:
                    raise CmdParseError("not enough arguments")
            # Out of buckets and still more arguments exist?
            elif len(args_to_fill) == 0:
                raise CmdParseError("too many arguments")
            else:
                # Defer setting convenience variables until we are sure that
                # the queues are not empty
                tofill = args_to_fill[0]
                toproc = args_inp[0]
                if tofill is None: # Ignore this argument
                    return parser(args_parsed, args_inp[1:], args_to_fill[1:])
                # Handle placeholder/nonsense arguments, used to make commands
                # appear more English-like
                # (*e.g.* `kill troll with axe` as opposed to `kill troll axe`)
                elif tofill.nonsense:
                    if toproc == tofill.name:
                        return parser(args_parsed, args_inp[1:],
                                      args_to_fill[1:])
                    else:
                        return parser(args_parsed, args_inp, args_to_fill[1:])
                # Infinite arguments are placed at the end of a string of
                # args to capture the remainder of the command.
                elif tofill.infinite:
                    if tofill.name in args_parsed:
                        args_parsed[tofill.name].append(toproc)
                        return parser(args_parsed, args_inp[1:],
                                      args_to_fill[1:])
                    else:
                        args_parsed[tofill.name] = [toproc]
                        return parser(args_parsed, args_inp[1:],
                                      args_to_fill[1:])
                # Normal (non-infinite, non-nonsense) arguments
                else:
                    args_parsed[tofill.name] = toproc
                    return parser(args_parsed, args_inp[1:],
                                    args_to_fill[1:])

        # Bail out if argument processing is unneeded
        if not self.args:
            return None
        # Otherwise, start the process
        else:
            return parser({}, good_split_spc(cmdstr), self.args)
