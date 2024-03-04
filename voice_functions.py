import keyboard

alpha_numeric_characters = {
        "letter a": 'a',
        "letter b": 'b',
        "letter c": 'c',
        "letter d": 'd',
        "letter e": 'e',
        "letter f": 'f',
        "letter g": 'g',
        "letter h": 'h',
        "letter i": 'i',
        "letter j": 'j',
        "letter k": 'k',
        "letter l": 'l',
        "letter m": 'm',
        "letter n": 'n',
        "letter o": 'o',
        "letter p": 'p',
        "letter q": 'q',
        "letter r": 'r',
        "letter s": 's',
        "letter t": 't',
        "letter u": 'u',
        "letter v": 'v',
        "letter w": 'w',
        "letter x": 'x',
        "letter y": 'y',
        "letter z": 'z',

        "number one": '1',
        "number two": '2',
        "number three": '3',
        "number four": '4',
        "number five": '5',
        "number six": '6',
        "number seven": '7',
        "number eight": '8',
        "number nine": '9',
        "number zero": '0',
    }

def press_key(character):
    keyboard.press_and_release(character)

# Function to press both Enter and Spacebar keys
def press_enter():
    keyboard.press_and_release('enter')

def press_space():
    keyboard.press_and_release('space')

def press_capital():
    keyboard.press_and_release('caps')

# Function to press both Enter and Spacebar keys
def press_delete():
    keyboard.press_and_release('delete')

def press_backspace():
    keyboard.press_and_release('backspace')

# Function to press Ctrl + key combination
def press_ctrl_key(key):
    keyboard.press('ctrl')
    keyboard.press_and_release(key)
    keyboard.release('ctrl')
