import tkinter as tk
import customtkinter as ctk
import mediapipe as mp
import threading
import pyautogui
import cv2
from voice_utils import get_audio, handle_voice_command, speak
from PIL import Image, ImageTk

cap = cv2.VideoCapture(0)
cam = cv2.VideoCapture(0)
face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)

screen_w, screen_h = pyautogui.size()
mp_holistic = mp.solutions.holistic
holistic_model = mp_holistic.Holistic(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

mp_drawing = mp.solutions.drawing_utils

SENSITIVITY_FACTOR = 3

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

        # Create a variable to hold the Tkinter PhotoImage object
        self.img_tk = None

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

        # Schedule check_voice_command to be called again after 100 milliseconds
        self.after(100, self.check_voice_command)

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
            # Create a new camera capture object
            global cap
            cap = cv2.VideoCapture(0)
            # Start the video thread directly
            self.start_video_thread()
        else:
            speak("Hand tracking mode deactivated")
            # If deactivated, release video capture
            cap.release()
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

    def update_eye_frame(self):
        if not self.eye_tracking_mode_active:
            return
        # Capture a frame from the camera
        ret, frame = cam.read()
        if not ret:
            print("Error capturing frame. Exiting.")
            return

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

        # Convert the processed BGR format image to PIL format
        img = Image.fromarray(frame)
        # Creates a Tk image from the PIL image using CTKPhotoImage
        img_tk = ImageTk.PhotoImage(image=img)

        # Sets the coordinates of the PhotoImage
        self.canvas.create_image(0, 0, anchor=tk.NW, image=img_tk)
        # Updates the image displayed in the canvas
        self.canvas.img_tk = img_tk

        # Check for the 'Esc' key press to exit the application
        if cv2.waitKey(1) & 0xFF == 27:
            self.eye_tracking_mode_active = False
            cam.release()
            self.canvas.delete("all")
            return

        # Schedule the next frame update
        self.after(10, self.update_eye_frame)

    def toggleEyeTracking(self):
        if self.hand_tracking_mode_active:
            self.toggleHandTracking()

        # Toggle the eye tracking mode state
        self.eye_tracking_mode_active = not self.eye_tracking_mode_active

        if self.eye_tracking_mode_active:
            speak("Eye tracking mode activated")
            # Create a new camera capture object
            global cam
            cam = cv2.VideoCapture(0)
            # Start the eye tracking directly
            self.update_eye_frame()
        else:
            speak("Eye tracking mode deactivated")
            # If deactivated, release video capture
            cam.release()
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

            # Convert the processed BGR format image to PIL format
            img = Image.fromarray(frame)
            # Creates a Tk image from the PIL image using CTKPhotoImage
            img_tk = ImageTk.PhotoImage(image=img)

            # Sets the coordinates of the PhotoImage
            self.canvas.create_image(0, 0, anchor=tk.NW, image=img_tk)
            # Updates the image displayed in the canvas
            self.canvas.img_tk = img_tk

            # Check for the 'Esc' key press to exit the application
            if cv2.waitKey(1) & 0xFF == 27:
                break

root = App()
root.mainloop()
