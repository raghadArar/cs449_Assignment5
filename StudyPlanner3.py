#cannot see camera but camera is on, the pause button dont work and the reset button works as pause
import customtkinter as ctk
from tkinter import Canvas, Scrollbar, HORIZONTAL, VERTICAL
import cv2
import mediapipe as mp
import threading
import time
from PIL import Image, ImageTk
import pygame

# Initialize MediaPipe hand detector
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils

# Initialize CustomTkinter GUI
ctk.set_appearance_mode("dark")
root = ctk.CTk()
root.title("Pomodoro Timer with Tasks and Music")
root.geometry("500x650")
root.configure(bg="grey")

# Scrollable container
main_frame = ctk.CTkFrame(root, fg_color="white", bg_color="white")
main_frame.pack(fill="both", expand=True)

canvas = Canvas(main_frame, bg="white", highlightthickness=0)
canvas.pack(side="left", fill="both", expand=True)

scrollbar_y = Scrollbar(main_frame, orient=VERTICAL, command=canvas.yview)
scrollbar_y.pack(side="right", fill="y")

scrollbar_x = Scrollbar(root, orient=HORIZONTAL, command=canvas.xview)
scrollbar_x.pack(side="bottom", fill="x")

scrollable_frame = ctk.CTkFrame(canvas, fg_color="white")
scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

# Timer Section
timer_frame = ctk.CTkFrame(scrollable_frame, fg_color="darkgray", corner_radius=10)
timer_frame.pack(pady=10, padx=10, fill="x")

timer_label = ctk.CTkLabel(timer_frame, text="Study Timer", font=("Helvetica", 16, "bold"), text_color="white")
timer_label.pack(pady=10)

timer_canvas = Canvas(timer_frame, width=400, height=400, bg="darkgray", highlightthickness=0)
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

# Timer Controls
# controls_frame = ctk.CTkFrame(scrollable_frame, fg_color="white", corner_radius=5)
# controls_frame.pack(pady=10)

# start_button = ctk.CTkButton(controls_frame, text="▶ Start",width=100,height=50, command=lambda: start_timer())
# start_button.pack(side="left", padx=5)

# pause_button = ctk.CTkButton(controls_frame, text="⏸ Pause", width=100,height=50,command=lambda: pause_timer())
# pause_button.pack(side="left", padx=5)

# reset_button = ctk.CTkButton(controls_frame, text="⏹ Reset", width=100,height=50,command=lambda: reset_timer())
# reset_button.pack(side="left", padx=5)

# Function to log timer control actions
def log_timer_action(action):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    print(f"[{timestamp}] {action} button pressed")

# Timer Controls (Updated with logging)
controls_frame = ctk.CTkFrame(scrollable_frame, fg_color="white", corner_radius=5)
controls_frame.pack(pady=10)

start_button = ctk.CTkButton(
    controls_frame, 
    text="▶ Start",
    width=100, 
    height=50, 
    command=lambda: (log_timer_action("Start"), start_timer())
)
start_button.pack(side="left", padx=5)

pause_timer_button = ctk.CTkButton(
    controls_frame, 
    text="⏸ Pause",
    width=100, 
    height=50, 
    command=lambda: (log_timer_action("Pause"), pause_timer())
)
pause_timer_button.pack(side="left", padx=5)

reset_button = ctk.CTkButton(
    controls_frame, 
    text="⏹ Reset",
    width=100, 
    height=50, 
    command=lambda: (log_timer_action("Reset"), reset_timer())
)
reset_button.pack(side="left", padx=5)


# Function to add a new task
def add_task():
    task_number = len(task_list) + 1  
    new_task = f"Task {task_number}"
    task_list.append(new_task)

    # Dynamically create a new label for the task
    task_label = ctk.CTkLabel(tasks_frame_inner, text=f"• {new_task}", font=("Helvetica", 14), text_color="white")
    task_label.pack(anchor="w", padx=20, pady=5)

    # Adjust the height of the tasks_frame dynamically
    current_height = tasks_frame.cget("height")
    new_height = current_height + 30  # Increase height for each new task 
    tasks_frame.configure(height=new_height)

# Tasks Section
tasks_frame = ctk.CTkFrame(scrollable_frame, fg_color="darkgray", corner_radius=10, height=50)
tasks_frame.pack(pady=10, padx=10, fill="x")

# Header frame for title and button
header_frame = ctk.CTkFrame(tasks_frame, fg_color="darkgray", height=20)
header_frame.pack(fill="x", padx=30, pady=5, ipady=5)  

# Tasks Label (Centered)
tasks_label = ctk.CTkLabel(header_frame, text="Tasks", font=("Helvetica", 16, "bold"), text_color="white")
tasks_label.place(relx=0.5, rely=0.5, anchor="center")  

# Add Button (Top-right)
add_button = ctk.CTkButton(header_frame, text="+", width=30, height=30, corner_radius=5,
                           fg_color=start_button._fg_color,  
                           text_color="white", command=add_task)
add_button.place(relx=0.95, rely=0.5, anchor="e")  # Top-right corner

# Frame for task items
tasks_frame_inner = ctk.CTkFrame(tasks_frame, fg_color="darkgray", height=0)  
tasks_frame_inner.pack(fill="x", padx=20, pady=10)

# Task List
task_list = []

# Music Section (with Sound Controls)
music_frame = ctk.CTkFrame(scrollable_frame, fg_color="darkgray", corner_radius=10)
music_frame.pack(pady=10, padx=10, fill="x")

music_label = ctk.CTkLabel(music_frame, text="Music", font=("Helvetica", 16, "bold"), text_color="white")
music_label.pack(pady=10)

# Sound Controls
sound_controls = ctk.CTkFrame(music_frame, fg_color="darkgray", corner_radius=5)
sound_controls.pack(pady=10)

play_button = ctk.CTkButton(sound_controls, text="▶ Play", command=lambda: print("Play clicked"))
play_button.pack(side="left", padx=5)

pause_button = ctk.CTkButton(sound_controls, text="⏸ Pause", command=lambda: print("Pause clicked"))
pause_button.pack(side="left", padx=5)

stop_button = ctk.CTkButton(sound_controls, text="⏹ Stop", command=lambda: print("Stop clicked"))
stop_button.pack(side="left", padx=5)

# Spacer to add space between controls and the music list
spacer = ctk.CTkFrame(music_frame, fg_color="darkgray", height=5)
spacer.pack(fill="x", pady=5)

# Music List Section

music_canvas = Canvas(music_frame, height=200, bg="darkgray", highlightthickness=0)
music_canvas.pack(fill="x")

music_scrollbar = Scrollbar(music_frame, orient=HORIZONTAL, command=music_canvas.xview)
music_scrollbar.pack(fill="x")
music_canvas.configure(xscrollcommand=music_scrollbar.set)

music_inner_frame = ctk.CTkFrame(music_canvas, fg_color="darkgray")
music_canvas.create_window((0, 0), window=music_inner_frame, anchor="nw")

# Initialize the mixer for music playback
pygame.mixer.init()

# Dictionary to map music button names to file paths
music_files = {
    "Music 1": "relaxing-piano-lo-fi-music-268029.mp3",  # Replace with actual file paths
    "Music 2": "winter-music-relaxing-piano-268028.mp3",
    "Music 3": "black-box-the-crew-129428.mp3",
    "Music 4": "lofi-study-calm-peaceful-chill-hop-112191.mp3",
    "Music 5": "study-music-181044.mp3",
}

# Function to play selected music
def play_music(music_name):
    if music_name in music_files:
        pygame.mixer.music.stop()  # Stop any currently playing music
        pygame.mixer.music.load(music_files[music_name])  # Load the selected music
        pygame.mixer.music.play()  # Play the music
        print(f"Playing: {music_name}")
    else:
        print(f"Music file for {music_name} not found!")

# Function to pause music
def pause_music():
    if pygame.mixer.music.get_busy():  # Check if music is playing
        pygame.mixer.music.pause()
        print("Music paused")

# Function to resume music
def resume_music():
    pygame.mixer.music.unpause()
    print("Music resumed")

# Function to stop music
def stop_music():
    pygame.mixer.music.stop()
    print("Music stopped")

# Update Music Buttons Section
music_options = ["Music 1", "Music 2", "Music 3", "Music 4", "Music 5"]
for music in music_options:
    music_button = ctk.CTkButton(
        music_inner_frame, text=music, width=100, height=100,
        corner_radius=10, font=("Helvetica", 12),
        command=lambda m=music: play_music(m)  # Play music on button click
    )
    music_button.pack(side="left", padx=5, pady=5)

# Update Sound Controls Section
play_button.configure(command=lambda: resume_music())  # Resume playback
pause_button.configure(command=lambda: pause_music())  # Pause playback
stop_button.configure(command=lambda: stop_music())  # Stop playback

music_inner_frame.update_idletasks()
music_canvas.configure(scrollregion=music_canvas.bbox("all"))
# Cursor overlay on the main GUI
cursor_canvas = Canvas(root, bg="grey", highlightthickness=0, width=20, height=20)
cursor_canvas.place(x=0, y=0)  # Start at the top-left corner

# Draw the cursor (a circle)
cursor_id = cursor_canvas.create_rectangle(2, 2, 18, 18, fill="red", outline="black")

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
    timer_canvas.itemconfig(status_text, text="Reset Successful", fill="green")



# Initialize OpenCV capture
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Camera not accessible")
    root.quit()

# Global variables for gesture debouncing
last_invoked_button = None
gesture_cooldown_active = False

def update_camera_feed():
    """Update the camera feed and process gestures in the background."""
    global last_invoked_button, gesture_cooldown_active

    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to capture frame")
        close_resources()
        return

    # Flip and process the frame
    frame = cv2.flip(frame, 1)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)

    cv2.imshow("Camera Feed", frame)

    gui_cursor_x = gui_cursor_y = None  # Initialize GUI cursor variables

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
            index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]

            # Calculate cursor position
            cursor_x = int(index_tip.x * frame.shape[1])
            cursor_y = int(index_tip.y * frame.shape[0])
            gui_cursor_x = int(cursor_x / frame.shape[1] * root.winfo_width())
            gui_cursor_y = int(cursor_y / frame.shape[0] * root.winfo_height())

            # Gesture: Pinch Detection
            pinch_distance = ((thumb_tip.x - index_tip.x) ** 2 + (thumb_tip.y - index_tip.y) ** 2) ** 0.5
            pinch_threshold = 0.05

            if pinch_distance < pinch_threshold and not gesture_cooldown_active:
                for button in [start_button, pause_timer_button, reset_button, add_button, play_button, pause_button, stop_button] + [
                    music_button for music_button in music_inner_frame.winfo_children()]:
                    x1, y1, x2, y2 = get_button_bbox(button)
                    if x1 <= gui_cursor_x <= x2 and y1 <= gui_cursor_y <= y2:
                        if last_invoked_button != button:  # Prevent repeated invocations
                            last_invoked_button = button
                            button.invoke()  # Simulate a button click
                            start_gesture_cooldown()  # Start cooldown period
                        break

    # Update the cursor position dynamically in Tkinter
    if gui_cursor_x is not None and gui_cursor_y is not None:
        cursor_canvas.place(x=gui_cursor_x, y=gui_cursor_y)

    # Schedule the next frame update
    root.after(10, update_camera_feed)

def start_gesture_cooldown():
    """Activate cooldown for gestures to avoid repeated invocations."""
    global gesture_cooldown_active
    gesture_cooldown_active = True
    root.after(1000, reset_gesture_cooldown)  # Cooldown of 1 second

def reset_gesture_cooldown():
    """Reset gesture cooldown to allow new gestures."""
    global gesture_cooldown_active, last_invoked_button
    gesture_cooldown_active = False
    last_invoked_button = None


def get_button_bbox(button):
    """Calculate the bounding box of a button."""
    x1 = button.winfo_rootx() - root.winfo_rootx()
    y1 = button.winfo_rooty() - root.winfo_rooty()
    x2 = x1 + button.winfo_width()
    y2 = y1 + button.winfo_height()
    return x1, y1, x2, y2

def close_resources():
    """Release resources and close the application."""
    hands.close()
    cap.release()
    cv2.destroyAllWindows()
    root.quit()

# Close resources when the window is closed
root.protocol("WM_DELETE_WINDOW", close_resources)

# Start the camera feed
update_camera_feed()

# Run the Tkinter main loop
root.mainloop()
cap.release()
cv2.destroyAllWindows()
