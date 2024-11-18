import customtkinter as ctk
import cv2
import mediapipe as mp
import numpy as np
import math

# Initialize MediaPipe hand detector
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils

# Initialize CustomTkinter GUI
ctk.set_appearance_mode("dark")
root = ctk.CTk()
root.title("Gesture-Based Pomodoro Timer")
root.geometry("500x500")

# Set background color of the root
root.configure(bg="black")

# Canvas for displaying the timer
canvas = ctk.CTkCanvas(root, width=500, height=500, bg="black", highlightthickness=0)
canvas.pack()

# Pomodoro settings
timer_radius = 150
center_x, center_y = 250, 250
default_session_time = 25  # in minutes
remaining_time = default_session_time * 60  # in seconds
is_running = False

# Timer circle and text
canvas.create_oval(
    center_x - timer_radius, center_y - timer_radius,
    center_x + timer_radius, center_y + timer_radius,
    fill="darkgray", outline="lightgray", width=2
)
timer_text = canvas.create_text(
    center_x, center_y - 20, text=f"{default_session_time}:00", 
    font=("Helvetica", 32, "bold"), fill="white"
)
status_text = canvas.create_text(
    center_x, center_y + 50, text="Paused", font=("Helvetica", 16), fill="yellow"
)

# Variables for gesture control
cursor_radius = 5
cursor = canvas.create_oval(-cursor_radius, -cursor_radius, cursor_radius, cursor_radius, fill="red", outline="")
cap = cv2.VideoCapture(0)

# Timer functions
def update_timer():
    global remaining_time, is_running

    if is_running and remaining_time > 0:
        remaining_time -= 1
        minutes, seconds = divmod(remaining_time, 60)
        canvas.itemconfig(timer_text, text=f"{minutes:02}:{seconds:02}")
    elif remaining_time == 0:
        canvas.itemconfig(status_text, text="Time's Up!", fill="red")
        is_running = False

    if is_running:
        root.after(1000, update_timer)

def start_timer():
    global is_running
    is_running = True
    canvas.itemconfig(status_text, text="Running", fill="green")
    update_timer()

def pause_timer():
    global is_running
    is_running = False
    canvas.itemconfig(status_text, text="Paused", fill="yellow")

def reset_timer():
    global remaining_time, is_running
    is_running = False
    remaining_time = default_session_time * 60
    minutes, seconds = divmod(remaining_time, 60)
    canvas.itemconfig(timer_text, text=f"{minutes:02}:{seconds:02}")
    canvas.itemconfig(status_text, text="Paused", fill="yellow")

def adjust_time(amount):
    global remaining_time
    remaining_time = max(0, remaining_time + amount * 60)
    minutes, seconds = divmod(remaining_time, 60)
    canvas.itemconfig(timer_text, text=f"{minutes:02}:{seconds:02}")

# Gesture detection
def detect_gesture():
    global remaining_time

    success, frame = cap.read()
    if not success:
        print("Ignoring empty camera frame.")
        return

    frame = cv2.flip(frame, 1)
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(image)

    canvas_width = canvas.winfo_width()
    canvas_height = canvas.winfo_height()
    canvas.itemconfig(cursor, fill="red")

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Index finger tip
            index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            canvas_x = int(index_tip.x * canvas_width)
            canvas_y = int(index_tip.y * canvas_height)

            # Update cursor position
            canvas.coords(cursor, canvas_x - cursor_radius, canvas_y - cursor_radius,
                          canvas_x + cursor_radius, canvas_y + cursor_radius)

            # Thumb tip for volume adjustments
            thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
            thumb_coords = (int(thumb_tip.x * canvas_width), int(thumb_tip.y * canvas_height))

            # Gesture-based controls
            if canvas_y < canvas_height // 3:
                start_timer()  # Gesture to start the timer
            elif canvas_y > 2 * canvas_height // 3:
                pause_timer()  # Gesture to pause the timer

            # Thumb adjustments for time
            if thumb_coords[1] < canvas_height // 3:
                adjust_time(1)  # Gesture to increase session time
            elif thumb_coords[1] > 2 * canvas_height // 3:
                adjust_time(-1)  # Gesture to decrease session time

    cv2.imshow("Gesture Control", frame)
    cv2.waitKey(1)
    root.after(10, detect_gesture)

# Start gesture detection loop
root.after(10, detect_gesture)
root.mainloop()
cap.release()
cv2.destroyAllWindows()
