import pyttsx3
import speech_recognition as sr
import keyboard
from voice_functions import alpha_numeric_characters, press_enter, press_ctrl_key, press_space, press_delete, press_backspace, press_key

engine = pyttsx3.init()

# Global variables and configurations
keyboard_mode = False
web_mode = False
universal_mode = True
last_written_text = ""

def speak(message):
    engine.say(message)
    engine.runAndWait()

def get_audio():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Microphone initialized")
        r.adjust_for_ambient_noise(source, duration=1)  # Adjust for 1 second
        try:
            print("Listening...")
            audio = r.listen(source, timeout=None)  # Set timeout=None to ensure continuous listening
            print("Audio recorded")
            text = r.recognize_google(audio)
            return text.lower()
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
            return None
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))
            return None

def handle_voice_command(user_input):
    if user_input is not None:
        handle_keyboard_mode(user_input)
        # handle_direct_mode(user_input)
        handle_universal_mode(user_input)
        handle_special_commands(user_input)
        handle_alphanumeric_commands(user_input)

def handle_universal_mode(user_input):
    global keyboard_mode, web_mode, universal_mode
    if user_input == "alora universal mode":
        universal_mode, keyboard_mode, web_mode = True, False, False
        speak("Universal mode activated")
    elif user_input == "alora universal mode off":
        universal_mode = False
        speak("Universal mode deactivated")

def handle_alphanumeric_commands(user_input):
    global last_written_text
    if keyboard_mode and user_input in alpha_numeric_characters:
        press_key(alpha_numeric_characters[user_input])
    elif user_input == "alora undo":
        press_ctrl_key('z')
    elif user_input == "alora redo":
        press_ctrl_key('y')
    elif user_input != "alora keyboard mode" and user_input != "alora keyboard mode off":
        keyboard.write(user_input)

def handle_special_commands(user_input):
    if universal_mode:
        special_commands = {
            "alora press bar": press_space,
            "alora press enter": press_enter,
            "alora press delete": press_delete,
            "alora press back space": press_backspace,
        }
    action = special_commands.get(user_input)
    if action:
        action()

def handle_keyboard_mode(user_input):
    global keyboard_mode, web_mode, universal_mode
    if user_input == "alora keyboard mode":
        if keyboard_mode:
            return speak("Keyboard mode is already activated")
        keyboard_mode, web_mode, universal_mode = True, False, False
        speak("Keyboard mode activated")
    elif user_input == "alora keyboard mode off":
        if not keyboard_mode:
            return speak("Keyboard mode is already deactivated")
        keyboard_mode = False
        speak("Keyboard mode deactivated")
