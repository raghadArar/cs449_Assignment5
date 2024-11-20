import customtkinter as ctk
from tkinter import Canvas, Scrollbar, VERTICAL, HORIZONTAL
import cv2
import mediapipe as mp
import math

# Initialize MediaPipe hand detector
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils

# Initialize CustomTkinter GUI
ctk.set_appearance_mode("dark")
root = ctk.CTk()
root.title("Gesture-Controlled Pomodoro Timer")
root.geometry("500x700")
root.configure(bg="black")

# Scrollable container
main_frame = ctk.CTkFrame(root, fg_color="black", bg_color="black")
main_frame.pack(fill="both", expand=True)

canvas = Canvas(main_frame, bg="black", highlightthickness=0)
canvas.pack(side="left", fill="both", expand=True)

scrollbar_y = Scrollbar(main_frame, orient=VERTICAL, command=canvas.yview)
scrollbar_y.pack(side="right", fill="y")

scrollable_frame = ctk.CTkFrame(canvas, fg_color="black")
scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar_y.set)

# Timer Section
timer_frame = ctk.CTkFrame(scrollable_frame, fg_color="darkgray", corner_radius=10)
timer_frame.pack(pady=10, padx=10, fill="x")

timer_label = ctk.CTkLabel(timer_frame, text="Pomodoro Timer", font=("Helvetica", 16, "bold"), text_color="white")
timer_label.pack(pady=10)

timer_canvas = Canvas(timer_frame, width=400, height=400, bg="black", highlightthickness=0)
timer_canvas.pack()

timer_radius = 150
center_x, center_y = 200, 200
default_session_time = 25  # in minutes
remaining_time = default_session_time * 60  # in seconds
is_running = False

timer_circle = timer_canvas.create_oval(
    center_x - timer_radius, center_y - timer_radius,
    center_x + timer_radius, center_y + timer_radius,
    fill="darkgray", outline="lightgray", width=2
)
timer_text = timer_canvas.create_text(
    center_x, center_y - 20, text=f"{default_session_time}:00",
    font=("Helvetica", 32, "bold"), fill="white"
)
status_text = timer_canvas.create_text(
    center_x, center_y + 50, text="Paused", font=("Helvetica", 16), fill="yellow"
)

# Tasks Section
tasks_frame = ctk.CTkFrame(scrollable_frame, fg_color="darkgray", corner_radius=10)
tasks_frame.pack(pady=10, padx=10, fill="x")

tasks_label = ctk.CTkLabel(tasks_frame, text="Tasks", font=("Helvetica", 16, "bold"), text_color="white")
tasks_label.pack(pady=10)

task_list = ["Task 1", "Task 2", "Task 3", "Task 4"]
for task in task_list:
    task_label = ctk.CTkLabel(tasks_frame, text=f"• {task}", font=("Helvetica", 14), text_color="white")
    task_label.pack(anchor="w", padx=20, pady=5)

# OpenCV Camera Initialization
cap = cv2.VideoCapture(0)

# Timer Functions
def update_timer():
    global remaining_time, is_running

    if is_running and remaining_time > 0:
        remaining_time -= 1
        minutes, seconds = divmod(remaining_time, 60)
        timer_canvas.itemconfig(timer_text, text=f"{minutes:02}:{seconds:02}")
    elif remaining_time == 0:
        timer_canvas.itemconfig(status_text, text="Time's Up!", fill="red")
        is_running = False

    if is_running:
        root.after(1000, update_timer)

def start_timer():
    global is_running
    is_running = True
    timer_canvas.itemconfig(status_text, text="Running", fill="green")
    update_timer()

def pause_timer():
    global is_running
    is_running = False
    timer_canvas.itemconfig(status_text, text="Paused", fill="yellow")

def reset_timer():
    global remaining_time, is_running
    is_running = False
    remaining_time = default_session_time * 60
    minutes, seconds = divmod(remaining_time, 60)
    timer_canvas.itemconfig(timer_text, text=f"{minutes:02}:{seconds:02}")
    timer_canvas.itemconfig(status_text, text="Paused", fill="yellow")

def extend_timer():
    global remaining_time
    remaining_time += 5 * 60
    minutes, seconds = divmod(remaining_time, 60)
    timer_canvas.itemconfig(timer_text, text=f"{minutes:02}:{seconds:02}")

# Gesture Detection
def detect_gesture():
    success, frame = cap.read()
    if not success:
        root.after(10, detect_gesture)
        return

    frame = cv2.flip(frame, 1)
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(image)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Extract relevant landmarks
            index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
            middle_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
            pinky_tip = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP]

            # Check gestures
            if index_tip.y < middle_tip.y < pinky_tip.y:  # "Peace" gesture for pause
                pause_timer()
            elif all(landmark.y > middle_tip.y for landmark in [index_tip, thumb_tip]):  # Fist for stop
                reset_timer()
            elif index_tip.y < thumb_tip.y:  # Extend timer gesture
                extend_timer()
            elif middle_tip.y < index_tip.y:  # All fingers up for start
                start_timer()

    # Show webcam feed for debugging
    cv2.imshow("Gesture Detection", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        root.quit()
        return

    root.after(10, detect_gesture)

# Start gesture detection loop
root.after(10, detect_gesture)

# Run the application
root.mainloop()
cap.release()
cv2.destroyAllWindows()
