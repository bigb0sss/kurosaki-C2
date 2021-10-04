from beacon import *
from server import *
from payload import *
from util import *
from database import *

import readline

from collections import OrderedDict
from os import system

class AutoComplete(object):
    def __init__(self, options):
        self.options = sorted(options)
        return

    def complete(self, text, state):
        response = None
        if state == 0:
            if text:
                self.matches = [s 
                                for s in self.options
                                if s and s.startswith(text)]
            else:
                self.matches = self.options[:]
        try:
            response = self.matches[state]
        except IndexError:
            response = None
        return response

class Menu:
    def __init__(self, name):

        self.name = name
        self.Commands = []

        self.commands = OrderedDict()
        self.commands["help"] = ["Show help", ""]
        self.commands["home"] = ["Return to main menu", ""]
        self.commands["exit"] = ["Exit", ""]

    # Register commands
    def registerCommand(self, command, description, args):
        self.commands[command] = [description, args]

    # Show help
    def showHelp(self):
        print("-" * 105)
        print('| {:<25} | {:<30} | {:<40} |'.format("Commands", "Descriptions", "Arguments"))
        print("-" * 105)
        for i in self.commands:
            print('| {:<25} | {:<30} | {:<40} |'.format(i, self.commands[i][0], self.commands[i][1]))
        print("-" * 105)
        print(" ")

    # Clear screen
    def clearScreen(self):
        system("clear")

    # User commands
    def uCommands(self):
        for i in self.commands:
            self.Commands.append(i)

    # Parse commands
    def parse(self):
        # Auto complete implementation
        readline.set_completer(AutoComplete(self.Commands).complete)
        readline.parse_and_bind('tab: complete')

        cmd = input(prompt(self.name))
        cmd = cmd.split()
        command = cmd[0]

        args = []
        for i in range(1,len(cmd)):
            args.append(cmd[i])
        return command, args

beacon_menu     = Menu("beacons")
listener_menu   = Menu("listeners")
payload_menu    = Menu("payloads")
home_menu       = Menu("Kurosaki-C2")

# Beacon menus
beacon_menu.registerCommand("list", "List active beacons", "")
beacon_menu.registerCommand("interact", "Interact with a beacon", "<name>")
beacon_menu.registerCommand("rename", "Rename beacon", "<name> <new name>")
beacon_menu.registerCommand("remove", "Remove beacon", "<name>")

# Listener menus
listener_menu.registerCommand("list", "List active listeners", "")
listener_menu.registerCommand("start", "Start a listener", "<name> <IP> <port>")
listener_menu.registerCommand("stop", "Stop an active listener","<name>")
listener_menu.registerCommand("remove", "Remove a listener", "<name>")

# Payload menus
payload_menu.registerCommand("list", "List available payload types", "")
payload_menu.registerCommand("generate", "Generate a payload", "<type> <arch> <listener> <output>")

# Main menus
home_menu.registerCommand("listeners", "Manage listeners", "")
home_menu.registerCommand("beacons", "Manage beacons", "")
home_menu.registerCommand("payloads", "Generate payloads", "")

beacon_menu.uCommands()
listener_menu.uCommands()
payload_menu.uCommands()
home_menu.uCommands()

beacon_Commands     = beacon_menu.Commands
listener_Commands   = listener_menu.Commands
payload_Commands    = payload_menu.Commands
home_Commands       = home_menu.Commands

# Banner

def banner():
    print
    print(" _  __                         _    _        ____ ____   ")
    print("| |/ /   _ _ __ ___  ___  __ _| | _(_)      / ___|___ \  ")
    print("| ' / | | | '__/ _ \/ __|/ _` | |/ / |_____| |     __) | ")
    print("| . \ |_| | | | (_) \__ \ (_| |   <| |_____| |___ / __/  ")
    print("|_|\_\__,_|_|  \___/|___/\__,_|_|\_\_|      \____|_____| ")
    print("                                           [bigb0ss]     ")
    print                                                         

# Main menu
def home():
    home_menu.clearScreen()
    banner()
    success("Kurosaki C2 commands: ")
    home_menu.showHelp()

    while True:
        try:
            command, args = home_menu.parse()
        except:
            continue
        if command not in home_Commands:
            error("Invalid command.")
        else:
            menuHome(command, args)

def Exit():
    saveListener()
    exit()

# Listener helper
def listenersHelper():
    listener_menu.clearScreen()
    success("Listener commands: ")
    listener_menu.showHelp()
    
    while True:
        try:
            command, args = listener_menu.parse()
        except:
            continue

        if command not in listener_Commands:
            error("Invalid command.")
        elif command == "home":
            home()
        elif command == "help":
            listener_menu.showHelp()
        elif command == "exit":
            Exit()
        else:
            menuListener(command, args)

# Beacon helper
def beaconHelper():
    beacon_menu.clearScreen()
    success("Beacon commands: ")
    beacon_menu.showHelp()

    while True:
        try:
            command, args = beacon_menu.parse()
        except:
            continue
            
        if command not in beacon_Commands:
            error("Invalid command.")
        elif command == "home":
            home()
        elif command == "help":
            beacon_menu.showHelp()
        elif command == "exit":
            Exit()
        else:
            menuBeacon(command, args)

# Payload helper
def payloadsHelper():
    payload_menu.clearScreen()
    success("Payload commands: ")
    payload_menu.showHelp()    

    while True:
        try:
            command, args = payload_menu.parse()
        except:
            continue
            
        if command not in payload_Commands:
            error("Invalid command.")
        else:
            menuPayloads(command, args)

# Commands for listeners
def menuListener(command, args):
    if command == "list": 
        listListener()
    elif command == "start":
        startListener(args)
    elif command == "stop":
        stopListener(args)
    elif command == "remove":
        removeListener(args)

# Commands for beacons
def menuBeacon(command, args):
    if command == "list":
        listBeacon()
    elif command == "remove":
        removeBeacon(args)
    elif command == "rename":
        renameBeacon(args)
    elif command == "interact":
        interactBeacon(args)

# Commands for payloads
def menuPayloads(command, args):
    if command == "help":
        payload_menu.showHelp()
    elif command == "home":
        home()
    elif command == "exit":
        Exit()
    elif command == "list":
        listPayload()
    elif command == "generate":
        generatePayload(args)

# Commands for main menu
def menuHome(command, args):
    if command == "help":
        home_menu.showHelp()
    elif command == "home":
        home()
    elif command == "listeners":
        listenersHelper()
    elif command == "beacons":
        beaconHelper()
    elif command == "payloads":
        payloadsHelper()
    elif command == "exit":
        Exit()