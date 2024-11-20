import customtkinter as ctk
from tkinter import Canvas, Scrollbar, HORIZONTAL, VERTICAL
import cv2
import mediapipe as mp

# Initialize MediaPipe hand detector
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils

# Initialize CustomTkinter GUI
ctk.set_appearance_mode("dark")
root = ctk.CTk()
root.title("Pomodoro Timer with Tasks and Music")
root.geometry("500x700")
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
controls_frame = ctk.CTkFrame(scrollable_frame, fg_color="white", corner_radius=5)
controls_frame.pack(pady=10)

start_button = ctk.CTkButton(controls_frame, text="▶ Start", command=lambda: start_timer())
start_button.pack(side="left", padx=5)

pause_button = ctk.CTkButton(controls_frame, text="⏸ Pause", command=lambda: pause_timer())
pause_button.pack(side="left", padx=5)

reset_button = ctk.CTkButton(controls_frame, text="⏹ Reset", command=lambda: reset_timer())
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

music_options = ["Music 1", "Music 2", "Music 3", "Music 4", "Music 5"]
for music in music_options:
    music_button = ctk.CTkButton(
        music_inner_frame, text=music, width=100, height=100,
        corner_radius=10, font=("Helvetica", 12),
        command=lambda m=music: print(f"{m} selected")
    )
    music_button.pack(side="left", padx=5, pady=5)

music_inner_frame.update_idletasks()
music_canvas.configure(scrollregion=music_canvas.bbox("all"))


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

# Gesture Detection (Optional, Placeholder for now)
def detect_gesture():
    root.after(100, detect_gesture)

# Start gesture detection loop
root.after(100, detect_gesture)

# Run the application
root.mainloop()
