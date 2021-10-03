import sys
import os

sys.path.append("./resources")

from menu import *
from db import *
from util import *

def main():
    # Creating local storages
    dbLocalStorage()

    # Checking active beacons
    activeBeacons()

    # Main menu
    home()

if __name__ == '__main__':
    main()
