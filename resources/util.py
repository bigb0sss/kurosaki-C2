import sys

# Colors
colors={
    'red'     : '\u001b[31m',
    'green'   : '\u001b[32m',
    'yellow'  : '\u001b[33m',
    'blue'    : '\u001b[34m',
    'magenta' : '\u001b[35m',
    'cyan'    : '\u001b[36m',
    'reset'   : '\u001b[0m',
    'bold'    : '\033[1m'
}

red     = colors['red']
green   = colors['green']
yellow  = colors['yellow']
blue    = colors['blue']
magenta = colors['magenta']
cyan    = colors['cyan']
reset   = colors['reset']
bold    = colors['bold']

# Error message
def error(message):
    output = f'{red}[ERROR] {message}{reset}'
    print(output)

# Success message
def success(message):
    output = f'{green}[INFO] {message}{reset}'
    print(output)

# Progress message
def progress(message):
    output = f'{yellow}[INFO] {message}{reset}'
    print(output)

# Prompt
def prompt(name):
    output = f'{bold}{blue}[ {name} ] > {reset}'
    return output


