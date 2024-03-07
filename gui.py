import tkinter as tk
import customtkinter as ctk
import mediapipe as mp
import threading
import pyautogui
import cv2
import datetime
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

SENSITIVITY_FACTOR = 4

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Alora")
        self.geometry(f"{800}x{450}")
        self.iconbitmap("alora_logo.ico")

        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=0)

        self.state_var = ctk.BooleanVar()
        self.state_var.set(False)
        self.voice_check_interval = 100  

        self.sidebar_frame = ctk.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Alora", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

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

        self.canvas = ctk.CTkCanvas(self, width=640, height=480)
        self.canvas.grid(row=0, column=1, padx=(20, 20), pady=(20, 0), sticky="nsew")

        self.canvas.configure(bg="black")

        self.appearance_mode_optionemenu.set("Dark")

        self.hand_tracking_mode_active = False
        self.eye_tracking_mode_active = False

        self.img_tk = None

        self.clock = ctk.CTkLabel(self, font=("Arial", 12), width=15, text="")
        self.clock.grid(row=1, column=1, padx=(20, 20), pady=(10, 0), sticky="ne")

        self.date_label = ctk.CTkLabel(self, font=("Arial", 12), width=15, text="")
        self.date_label.grid(row=1, column=1, padx=(20, 20), pady=(10, 0), sticky="nw")

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.update_clock()
        self.update_date()

    def update_date(self):
        now = datetime.datetime.now()
        self.date_label.configure(text=now.strftime("%m/%d/%Y"))
        self.after(1000, self.update_date)

    def update_clock(self):
        now = datetime.datetime.now()
        self.clock.configure(text=now.strftime("%H:%M"))
        self.after(1000, self.update_clock)

    def change_appearance_mode_event(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)

    def toggleVoiceRecognition(self):
        global capture_audio
        self.state_var.set(not self.state_var.get())
        capture_audio = self.state_var.get()  
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

        self.after(100, self.check_voice_command)

    def start_video_thread(self):
        video_thread = threading.Thread(target=self.update_frame)
        video_thread.daemon = True
        video_thread.start()

    def toggleHandTracking(self):
        if self.eye_tracking_mode_active:
            self.toggleEyeTracking()

        self.hand_tracking_mode_active = not self.hand_tracking_mode_active

        if self.hand_tracking_mode_active:
            speak("Hand tracking mode activated")
            global cap
            cap = cv2.VideoCapture(0)
            self.start_video_thread()
        else:
            speak("Hand tracking mode deactivated")
            cap.release()
            self.canvas.delete("all")

    def update_frame(self):
        if not self.hand_tracking_mode_active:
            return
        ret, frame = cap.read()
        if ret:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = holistic_model.process(rgb_frame)
            mp_drawing.draw_landmarks(frame, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS)
            mp_drawing.draw_landmarks(frame, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS)
            
            # position of the index finger
            if results.right_hand_landmarks:
                index_tip = results.right_hand_landmarks.landmark[mp_holistic.HandLandmark.INDEX_FINGER_TIP]
                height, width, _ = frame.shape
                finger_x, finger_y = int(index_tip.x * width), int(index_tip.y * height)
                finger_x_scaled = finger_x * SENSITIVITY_FACTOR
                finger_y_scaled = finger_y * SENSITIVITY_FACTOR
                # mouse cursor
                pyautogui.moveTo(finger_x_scaled, finger_y_scaled)

            img = Image.fromarray(frame)
            img_tk = ImageTk.PhotoImage(image=img)
            self.canvas.create_image(0, 0, anchor=ctk.NW, image=img_tk)
            self.canvas.img_ctk = img_tk
        root.after(10, self.update_frame)

    def update_eye_frame(self):
        if not self.eye_tracking_mode_active:
            return
        ret, frame = cam.read()

        if not ret:
            print("Error capturing frame. Exiting.")
            return

        # flip the fram
        frame = cv2.flip(frame, 1)
        # BGR frame to RGB
        rgbframe = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        output = face_mesh.process(rgbframe)
        landmark_points = output.multi_face_landmarks
        frame_h, frame_w = frame.shape[:2]

        if landmark_points:
            landmarks = landmark_points[0].landmark
            for id, landmark in enumerate(landmarks[474:478]):
                x = int(landmark.x * frame_w)
                y = int(landmark.y * frame_h)
                cv2.circle(frame, (x, y), 3, (0, 255, 0))
                if id == 1:
                    # mouse cursor 
                    screen_x = screen_w * landmark.x
                    screen_y = screen_h * landmark.y
                    pyautogui.moveTo(screen_x, screen_y)

            left = [landmarks[145], landmarks[159]]
            for landmark in left:
                x = int(landmark.x * frame_w)
                y = int(landmark.y * frame_h)
                cv2.circle(frame, (x, y), 3, (0, 255, 255))

            # mouse click
            if (left[0].y - left[1].y) < 0.004:
                pyautogui.click()
                pyautogui.sleep(1)

        img = Image.fromarray(frame)
        img_tk = ImageTk.PhotoImage(image=img)

        self.canvas.create_image(0, 0, anchor=tk.NW, image=img_tk)
        self.canvas.img_tk = img_tk

        if cv2.waitKey(1) & 0xFF == 27:
            self.eye_tracking_mode_active = False
            cam.release()
            self.canvas.delete("all")
            return

        self.after(10, self.update_eye_frame)

    def toggleEyeTracking(self):
        if self.hand_tracking_mode_active:
            self.toggleHandTracking()

        self.eye_tracking_mode_active = not self.eye_tracking_mode_active

        if self.eye_tracking_mode_active:
            speak("Eye tracking mode activated")
            global cam
            cam = cv2.VideoCapture(0)
            self.update_eye_frame()
        else:
            speak("Eye tracking mode deactivated")
            cam.release()
            self.canvas.delete("all")

    def eyeTracking(self):
        while self.eye_tracking_mode_active:
            ret, frame = cam.read()

            if not ret:
                print("Error capturing frame. Exiting.")
                break

            frame = cv2.flip(frame, 1)
            rgbframe = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            output = face_mesh.process(rgbframe)
            landmark_points = output.multi_face_landmarks
            frame_h, frame_w = frame.shape[:2]

            if landmark_points:
                landmarks = landmark_points[0].landmark
                for id, landmark in enumerate(landmarks[474:478]):
                    x = int(landmark.x * frame_w)
                    y = int(landmark.y * frame_h)
                    cv2.circle(frame, (x, y), 3, (0, 255, 0))
                    if id == 1:
                        # mouse cursor
                        screen_x = screen_w * landmark.x
                        screen_y = screen_h * landmark.y
                        pyautogui.moveTo(screen_x, screen_y)

                # left eye landmar
                left = [landmarks[145], landmarks[159]]
                for landmark in left:
                    x = int(landmark.x * frame_w)
                    y = int(landmark.y * frame_h)
                    cv2.circle(frame, (x, y), 3, (0, 255, 255))

                if (left[0].y - left[1].y) < 0.004:
                    pyautogui.click()
                    pyautogui.sleep(1)

            img = Image.fromarray(frame)
            img_tk = ImageTk.PhotoImage(image=img)

            self.canvas.create_image(0, 0, anchor=tk.NW, image=img_tk)
            self.canvas.img_tk = img_tk

            if cv2.waitKey(1) & 0xFF == 27:
                break


root = App()
root.mainloop()
