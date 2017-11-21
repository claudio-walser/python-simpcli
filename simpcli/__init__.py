import os
import re
import readline
import subprocess

class CliException(Exception):
    pass

class Interface(object):

    # style
    HEADER = '\033[95m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    # good
    INFO = '\033[96m'
    OK = '\033[92m'

    # not so good
    WARNING = '\033[93m'
    ERROR = '\033[91m'

    # closing character
    ENDC = '\033[0m'

    def writeOut(self, msg: str):
        print(msg)
        return True

    def error(self, msg: str):
        # some cli colors
        self.writeOut(self.ERROR + "Error: " + self.ENDC)
        return self.writeOut(msg)

    def warning(self, msg: str):
        # some cli colors
        return self.writeOut(self.WARNING + msg + self.ENDC)

    def header(self, msg: str):
        # some cli colors
        return self.writeOut(self.BOLD + self.HEADER + msg + self.ENDC)

    def info(self, msg: str):
        # some cli colors
        return self.writeOut(self.INFO + msg + self.ENDC)

    def red(self, msg: str):
        return self.writeOut(self.ERROR + msg + self.ENDC)

    def ok(self, msg: str):
        # some cli colors
        return self.writeOut(self.OK + msg + self.ENDC)

    def askFor(self, prompt: str, options=False, default: str=False):
        self.info(prompt)

        completer = InputCompleter()
        readline.set_completer_delims(' \t\n;')
        readline.parse_and_bind("tab: complete")

        # given options completer
        if isinstance(options, list):
            self.writeOut(
                self.BOLD + "Possibilities: " + self.ENDC +
                "[" + ", ".join(options) + "]"
            )
            completer.setOptions(options)
            readline.set_completer(completer.completeOptions)

        # directory completer
        if isinstance(options, str) and options == "os.directory":
            # just here to clarify, do nothing is perfect for
            # /folder/completion if readline is parsed and bound
            pass

        # if no options set, use an empty completer as default
        if options is False:
            readline.set_completer(completer.completeNothing)
        if default:
            self.writeOut(self.BOLD + "Default: " + self.ENDC + default)

        value = input("")

        # reset all completers after user input is happen
        readline.set_completer()

        if isinstance(value, str):
            value = value.strip()

        if value == "" and default is not False:
            value = default

        if isinstance(options, list) and value not in options:
            self.error(
                "Value <" +
                value +
                "> not allowed! Choose one of " +
                ", ".join(options)
            )
            return self.askFor(prompt, options, default)
        return value


class InputCompleter(object):

    options = []

    re = re.compile('.*\s+$', re.M)

    def setOptions(self, options: list):
        self.options = options
        return True

    def completeNothing(self, text, state):
        return False

    def completeOptions(self, text, state):
        # need to simplify this much more
        buffer = readline.get_line_buffer()
        line = readline.get_line_buffer().split()
        # show all commands
        if not line:
            return [c + ' ' for c in self.options][state]

        # account for last argument ending in a space
        if self.re.match(buffer):
            line.append('')

        # resolve command to the implementation function
        cmd = line[0].strip()
        if cmd in self.options:
            args = line[1:]
            if args:
                return False
            return [cmd + ' '][state]
        results = [c + ' ' for c in self.options if c.startswith(cmd)] + [None]
        return results[state]


class Command(object):

    verbose = False
    interface = Interface()

    def __init__(self, verbose: bool = False):
        self.verbose = verbose

    def execute(self, command: str, ignoreReturnCode: bool = False):
        if self.verbose is True:
            self.interface.warning("Executing: %s" % command)

        process = subprocess.Popen(
            command,
            shell=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        output, err = process.communicate()
        if process.returncode != 0 and ignoreReturnCode == False:
            if self.verbose is True:
                raise CliException(err.decode("utf-8").strip())            
            return False

        output = output.decode("utf-8").strip()
        if self.verbose is True:
            self.interface.writeOut(output)

        return output
