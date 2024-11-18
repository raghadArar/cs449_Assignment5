import customtkinter as ctk
import cv2
import mediapipe as mp
import numpy as np
import math
import time
import webbrowser  # For opening URLs

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

# SUCourse button settings
button_x, button_y = 450, 50  # Top-right corner position
button_width, button_height = 80, 30

# Draw the SUCourse button
button_rect = canvas.create_rectangle(
    button_x - button_width // 2, button_y - button_height // 2,
    button_x + button_width // 2, button_y + button_height // 2,
    fill="blue", outline="white"
)
button_text = canvas.create_text(
    button_x, button_y, text="SUCourse", font=("Helvetica", 12, "bold"), fill="white"
)

# Timer functions
last_update_time = time.time()  # Track the last time the timer was updated

def update_timer():
    global remaining_time, is_running, last_update_time

    if is_running:
        # Calculate elapsed time since the last update
        current_time = time.time()
        elapsed_time = current_time - last_update_time
        last_update_time = current_time

        # Reduce remaining time by the elapsed time
        remaining_time = max(0, remaining_time - elapsed_time)
        minutes, seconds = divmod(int(remaining_time), 60)  # Use int() to truncate seconds
        canvas.itemconfig(timer_text, text=f"{minutes:02}:{seconds:02}")

        if remaining_time <= 0:
            # Timer has ended
            is_running = False
            canvas.itemconfig(status_text, text="Time's Up!", fill="red")
            return

    # Schedule the next update
    root.after(50, update_timer)  # Check every 50ms for smoother updates

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
    minutes, seconds = divmod(int(remaining_time), 60)
    canvas.itemconfig(timer_text, text=f"{minutes:02}:{seconds:02}")
    canvas.itemconfig(status_text, text="Paused", fill="yellow")

def adjust_time(amount):
    global remaining_time
    remaining_time = max(0, remaining_time + amount * 60)
    minutes, seconds = divmod(int(remaining_time), 60)
    canvas.itemconfig(timer_text, text=f"{minutes:02}:{seconds:02}")


# Variables to track SUCourse button interaction state
sucourse_opened = False  # Tracks whether the link has been opened
finger_hovered = False   # Tracks whether the finger is currently hovering

# Gesture detection
def detect_gesture():
    global remaining_time, sucourse_opened, finger_hovered

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

            # Middle finger tip
            middle_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
            middle_coords = (int(middle_tip.x * canvas_width), int(middle_tip.y * canvas_height))

            # Debugging: Log the positions of the index and middle fingers
            print(f"Index finger position: {index_tip.x}, {index_tip.y}")
            print(f"Middle finger position: {middle_tip.x}, {middle_tip.y}")

            # SUCourse button interaction
            button_bbox = canvas.bbox(button_rect)
            if button_bbox[0] <= canvas_x <= button_bbox[2] and button_bbox[1] <= canvas_y <= button_bbox[3]:
                canvas.itemconfig(button_rect, fill="cyan")  # Highlight button
                print("Cursor is over the button.")

                # Check if middle finger is near or above the index finger (allowing some flexibility)
                threshold = 0.05  # Allowing some flexibility in y-coordinate comparison
                if middle_coords[1] < index_tip.y + threshold and middle_coords[1] < canvas_y:
                    print("Middle finger is raised above the index finger.")
                    if not sucourse_opened:  # Only open once per hover
                        if not finger_hovered:  # Trigger only on first hover
                            print("Opening SUCourse...")
                            # Open the URL
                            webbrowser.open("https://sucourse.sabanciuniv.edu/")
                            time.sleep(1)  # Wait a moment to ensure the browser opens
                            sucourse_opened = True
                            print("SUCourse link opened.")
                finger_hovered = True  # Indicate finger is on the button
            else:
                canvas.itemconfig(button_rect, fill="blue")  # Reset button color
                finger_hovered = False  # Reset hover state
                sucourse_opened = False  # Allow re-opening when hovered again
                print("Cursor is off the button.")

    else:
        print("No hands detected.")

    cv2.imshow("Gesture Control", frame)
    cv2.waitKey(1)
    root.after(10, detect_gesture)

# Start gesture detection loop
root.after(10, detect_gesture)
root.mainloop()
cap.release()
cv2.destroyAllWindows()
