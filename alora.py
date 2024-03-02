#import tkinter
import tkinter.messagebox
import customtkinter as ctk
import speech_recognition as sr
import keyboard
import pyttsx3
import threading
#import time
import cv2
import mediapipe as mp
import pyautogui
from PIL import Image, ImageTk

# Global variables and configurations
keyboard_mode = False
web_mode = False
universal_mode = True
last_written_text = ""

# Define a flag to control whether to capture audio or not
capture_audio = False
# Create a global variable to store the recognized text
recognized_text = ""
# Initialize the TTS engine 
engine = pyttsx3.init()

# Set properties for the TTS engine
voices = engine.getProperty('voices')
# Female voice usually has index 1, but you can verify this by printing the voices list
engine.setProperty('voice', voices[1].id)

# Define a flag to control whether to capture audio or not
capture_audio = False
# Create a global variable to store the recognized text
recognized_text = ""
# Initialize the TTS engine 
engine = pyttsx3.init()

# Set properties for the TTS engine
voices = engine.getProperty('voices')
# Female voice usually has index 1, but you can verify this by printing the voices list
engine.setProperty('voice', voices[1].id)

# Define a function to speak a given message 
def speak(message):
    engine.say(message)
    engine.runAndWait()

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

mp_holistic = mp.solutions.holistic
holistic_model = mp_holistic.Holistic(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

mp_drawing = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)
SENSITIVITY_FACTOR = 3

cam = cv2.VideoCapture(0)
face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)
screen_w, screen_h = pyautogui.size()

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

web_commands = {
        "search youtube": "https://www.youtube.com/?app",
        "search facebook": "https://www.facebook.com/?app",
        "search google": "https://www.google.com/?app",
        "search instagram": "https://www.instagram.com/?app",
    }

# Start listening for voice commands
def get_audio():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Microphone initialized")
        r.adjust_for_ambient_noise(source, duration=1)  # Adjust for 1 second
        audio = r.listen(source, timeout=None)  # Set timeout=None to ensure continuous listening
        print("Audio recorded")
        try:
            text = r.recognize_google(audio)
            return text.lower()
        except sr.UnknownValueError:
            speak("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))

# Function to press a character key 
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

 # Function to handle universal mode commands
def handle_universal_mode(user_input):
    global keyboard_mode, web_mode, universal_mode
    if user_input == "alora universal mode":
        universal_mode, keyboard_mode, web_mode = True, False, False
        speak("Universal mode activated")
    elif user_input == "alora universal mode off":
        universal_mode = False
        speak("Universal mode deactivated")

# Function to handle the speech recognition
def recognize_speech(recognizer, audio):
        global recognized_text
        try:
            recognized_text = recognizer.recognize_google(audio).lower()
        except sr.UnknownValueError:
            pass  # Ignore if speech cannot be recognized
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))

    # Function to handle special commands in universal mode  hellohello
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

    # Function to handle alphanumeric character commands
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

    # Main function to handle voice commands
def handle_voice_command(user_input):
    if user_input is not None:
        handle_keyboard_mode(user_input)
        # handle_direct_mode(user_input)
        handle_universal_mode(user_input)
        handle_special_commands(user_input)
        handle_alphanumeric_commands(user_input)

# Function to handle keyboard mode commands
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
            
class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # configure window
        self.title("Alora")
        self.geometry(f"{800}x{450}")

        # configure grid layout (4x4)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=0)

        self.state_var = ctk.BooleanVar()
        self.state_var.set(False)
        self.voice_check_interval = 100  # Set the interval in milliseconds

        # create sidebar frame with widgets
        self.sidebar_frame = ctk.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Alora", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        #voice recog button
        self.sidebar_button_1 = ctk.CTkButton(self.sidebar_frame, text="Voice Recognition On", command=self.toggleVoiceRecognition)
        self.sidebar_button_1.grid(row=1, column=0, padx=20, pady=10)

        self.sidebar_button_2 = ctk.CTkButton(self.sidebar_frame, text="Hand Tracking Mode",  command=self.toggleHandTracking)
        self.sidebar_button_2.grid(row=2, column=0, padx=20, pady=10)

        self.sidebar_button_3 = ctk.CTkButton(self.sidebar_frame, text="Eye Tracking Mode", command=self.toggleEyeTracking)
        self.sidebar_button_3.grid(row=3, column=0, padx=20, pady=10)

        self.appearance_mode_label = ctk.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))

        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"],
                                                                       command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 10))

        # create textbox
        self.canvas = ctk.CTkCanvas(self, width=640, height=480)
        self.canvas.grid(row=0, column=1, padx=(20, 20), pady=(20, 0), sticky="nsew")

        # Set the background color to black
        self.canvas.configure(bg="black")

        # set default values
        self.appearance_mode_optionemenu.set("Dark")

        self.hand_tracking_mode_active = False
        self.eye_tracking_mode_active = False


    def sidebar_button_event(self):
        print("clicked")


    def change_appearance_mode_event(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)

    def toggleVoiceRecognition(self):
        global capture_audio
        self.state_var.set(not self.state_var.get())
        capture_audio = self.state_var.get()  # Update capture_audio based on the current state
        if capture_audio:
            speak("Voice recognition activated")
            self.check_voice_command()
        else:
            speak("Voice recognition deactivated.")
    
    def check_voice_command(self):
        if self.state_var.get() and capture_audio:
            user_input = get_audio()
            if user_input:
                handle_voice_command(user_input)

        self.start_video_thread()

    def start_video_thread(self):
        video_thread = threading.Thread(target=self.update_frame)
        video_thread.daemon = True
        video_thread.start()

    def toggleHandTracking(self):
        if self.eye_tracking_mode_active:
            self.toggleEyeTracking()

        # Toggle the hand tracking mode state
        self.hand_tracking_mode_active = not self.hand_tracking_mode_active

        if self.hand_tracking_mode_active:
            speak("Hand tracking mode activated")
            # If activated, start the video capture in a separate thread
            video_thread = threading.Thread(target=self.update_frame)
            video_thread.daemon = True
            video_thread.start()
        else:
            speak("Hand tracking mode deactivated")
            # If deactivated, release video capture
            cap.release()
            cv2.destroyAllWindows()
            # Clear the canvas
            self.canvas.delete("all")

    def update_frame(self):
        if not self.hand_tracking_mode_active:
            return
        # Captures the frame and checks if the frame was successfully read.
        ret, frame = cap.read()
        # If successfully read, it will run this block of code
        if ret:
            # Converts the color from BLUE-RED-GREEN to RED-GREEN-BLUE
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # Displays the result of the video with the corresponding color schemas
            results = holistic_model.process(rgb_frame)
            # Draws a landmark for both left and right hands
            mp_drawing.draw_landmarks(frame, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS)
            mp_drawing.draw_landmarks(frame, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS)
            
            # Get the position of the index finger tip
            if results.right_hand_landmarks:
                index_tip = results.right_hand_landmarks.landmark[mp_holistic.HandLandmark.INDEX_FINGER_TIP]
                height, width, _ = frame.shape
                finger_x, finger_y = int(index_tip.x * width), int(index_tip.y * height)
                # Scale the coordinates for increased sensitivity
                finger_x_scaled = finger_x * SENSITIVITY_FACTOR
                finger_y_scaled = finger_y * SENSITIVITY_FACTOR
                # Move the mouse cursor to the scaled position of the index finger tip
                pyautogui.moveTo(finger_x_scaled, finger_y_scaled)

            # Converts the processed BGR format image to PIL format
            img = Image.fromarray(frame)
            # Creates a Tk image from the PIL image using CTKPhotoImage
            img_tk = ImageTk.PhotoImage(image=img)
            # Sets the coordinates of the PhotoImage
            self.canvas.create_image(0, 0, anchor=ctk.NW, image=img_tk)
            # Updates the image displayed in the canvas
            self.canvas.img_ctk = img_tk
        root.after(10, self.update_frame)

    def toggleEyeTracking(self):
        if self.hand_tracking_mode_active:
            self.toggleHandTracking()
        # Toggle the hand tracking mode state
        self.eye_tracking_mode_active = not self.eye_tracking_mode_active

        if self.eye_tracking_mode_active:
            speak("Eye tracking mode activated")
            # If activated, start the video capture in a separate thread
            video_thread = threading.Thread(target=self.eyeTracking)
            video_thread.daemon = True
            video_thread.start()
        else:
            speak("Eye tracking mode deactivated")
            # If deactivated, release video capture
            cam.release()
            cv2.destroyAllWindows()
            # Clear the canvas
            self.canvas.delete("all")

    def eyeTracking(self):
        
        while self.eye_tracking_mode_active:
            # Capture a frame from the camera
            ret, frame = cam.read()
            if not ret:
                print("Error capturing frame. Exiting.")
                break

            # Flip the frame horizontally for better user experience
            frame = cv2.flip(frame, 1)

            # Convert the BGR frame to RGB
            rgbframe = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Process the frame with face mesh to detect landmarks
            output = face_mesh.process(rgbframe)
            landmark_points = output.multi_face_landmarks

            # Get frame dimensions
            frame_h, frame_w = frame.shape[:2]

            if landmark_points:
                landmarks = landmark_points[0].landmark
                for id, landmark in enumerate(landmarks[474:478]):
                    x = int(landmark.x * frame_w)
                    y = int(landmark.y * frame_h)
                    cv2.circle(frame, (x, y), 3, (0, 255, 0))
                    if id == 1:
                        # Move the mouse cursor based on the detected landmark
                        screen_x = screen_w * landmark.x
                        screen_y = screen_h * landmark.y
                        pyautogui.moveTo(screen_x, screen_y)

                # Additional processing for left eye landmarks
                left = [landmarks[145], landmarks[159]]
                for landmark in left:
                    x = int(landmark.x * frame_w)
                    y = int(landmark.y * frame_h)
                    cv2.circle(frame, (x, y), 3, (0, 255, 255))

                # Trigger a mouse click if the vertical distance is below a threshold
                if (left[0].y - left[1].y) < 0.004:
                    pyautogui.click()
                    pyautogui.sleep(1)

            # Display the annotated frame
            cv2.imshow('Eye Controlled Mouse', frame)

            # Convert the processed BGR format image to PIL format
            img = Image.fromarray(frame)
            # Creates a Tk image from the PIL image using CTKPhotoImage
            img_tk = ImageTk.PhotoImage(image=img)

            # Sets the coordinates of the PhotoImage
            self.canvas.create_image(0, 0, anchor=ctk.NW, image=img_tk)
            # Updates the image displayed in the canvas
            self.canvas.img_tk = img_tk

            # Check for the 'Esc' key press to exit the application
            if cv2.waitKey(1) & 0xFF == 27:
                break

# Create a root window
root = App()

# Start the main loop 
root.mainloop()

