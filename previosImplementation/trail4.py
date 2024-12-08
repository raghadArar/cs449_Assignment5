import customtkinter as ctk
from tkinter import Canvas, Scrollbar, HORIZONTAL, VERTICAL
import cv2
import mediapipe as mp
import threading
import webbrowser
import pyautogui
import win32api
import win32con
from win32con import VK_MEDIA_PLAY_PAUSE, KEYEVENTF_EXTENDEDKEY

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

def send_media_key(key):
    """Sends the media key press using pywin32."""
    if key == 'play/pause':
        # Simulate the MediaPlayPause key press (Media Play / Pause)
        win32api.keybd_event(VK_MEDIA_PLAY_PAUSE, 0, KEYEVENTF_EXTENDEDKEY, 0)
    elif key == 'stop':
        # Simulate the MediaStop key press (Media Stop)
        win32api.keybd_event(0xB2, 0, win32con.KEYEVENTF_SCANCODE, 0)  # Media Stop (0xB2)
        win32api.keybd_event(0xB2, 0, win32con.KEYEVENTF_KEYUP, 0)  # Release the key

def play_pause():
    """Simulates the MediaPlayPause key."""
    send_media_key('play/pause')

def stop_video():
    """Simulates the MediaStop key."""
    send_media_key('stop')

# Sound Controls
sound_controls = ctk.CTkFrame(music_frame, fg_color="darkgray", corner_radius=5)
sound_controls.pack(pady=10)

play_button = ctk.CTkButton(sound_controls, text="▶ Play / ⏸ Pause", command=play_pause)
play_button.pack(side="left", padx=5)

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

music_options = [
    ("Never Gonna Give You Up", "https://www.youtube.com/watch?v=dQw4w9WgXcQ"),  # Rick Astley - Never Gonna Give You Up
    ("Bohemian Rhapsody", "https://www.youtube.com/watch?v=fJ9rUzIMcZQ"),  # Queen - Bohemian Rhapsody
    ("Billie Jean", "https://www.youtube.com/watch?v=Zi_XLOBDo_Y"),  # Michael Jackson - Billie Jean
    ("Smells Like Teen Spirit", "https://www.youtube.com/watch?v=hTWKbfoikeg"),  # Nirvana - Smells Like Teen Spirit
    ("Faded", "https://www.youtube.com/watch?v=60ItHLz5WEA"),  # Alan Walker - Faded
]
# Create buttons for each music option
for music, url in music_options:
    music_button = ctk.CTkButton(
        music_inner_frame, text=music, width=100, height=100,
        corner_radius=10, font=("Helvetica", 12),
        command=lambda link=url: webbrowser.open(link)  # Open the YouTube URL
    )
    music_button.pack(side="left", padx=5, pady=5)
music_inner_frame.update_idletasks()
music_canvas.configure(scrollregion=music_canvas.bbox("all"))
# Cursor overlay on the main GUI
cursor_canvas = Canvas(root, bg="grey", highlightthickness=0, width=20, height=20)
cursor_canvas.place(x=0, y=0)  # Start at the top-left corner

# Draw the cursor (a circle)
cursor_id = cursor_canvas.create_oval(2, 2, 18, 18, fill="red", outline="black")

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

def map_coordinates(cv_x, cv_y, frame_width, frame_height, gui_width, gui_height):
    gui_x = int(cv_x / frame_width * gui_width)
    gui_y = int(cv_y / frame_height * gui_height)
    return gui_x, gui_y

def detect_gesture_loop():
    global root, cap, cursor_canvas

    ret, frame = cap.read()
    if not ret:
        root.after(10, detect_gesture_loop)
        return

    frame = cv2.flip(frame, 1)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)

    cursor_position = None
    gui_width = root.winfo_width()
    gui_height = root.winfo_height()

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Retrieve landmarks for gesture detection
            thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
            index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]

            # Calculate cursor position in OpenCV coordinates
            cursor_x = int(index_tip.x * frame.shape[1])
            cursor_y = int(index_tip.y * frame.shape[0])
            cursor_position = (cursor_x, cursor_y)

            # Gesture: Pinch Detection
            pinch_distance = ((thumb_tip.x - index_tip.x) ** 2 + (thumb_tip.y - index_tip.y) ** 2) ** 0.5
            pinch_threshold = 0.05  # Adjust as needed

            if pinch_distance < pinch_threshold:
                # Scale and adjust OpenCV coordinates to GUI coordinates
                #gui_cursor_x = int(cursor_x / frame.shape[1] * gui_width)
                #gui_cursor_y = int(cursor_y / frame.shape[0] * gui_height)

                # Apply an offset if needed
                y_offset = root.winfo_rooty()  # Distance from the top of the screen to the GUI content
                x_offset = root.winfo_rootx()  # Distance from the left of the screen to the GUI content

                # Map cursor position from OpenCV to GUI
                gui_cursor_x, gui_cursor_y = map_coordinates(
                    cursor_position[0], cursor_position[1],
                    frame.shape[1], frame.shape[0],  # OpenCV frame dimensions
                    root.winfo_width(), root.winfo_height()  # GUI dimensions
                )

                # Account for offsets
                gui_cursor_x += x_offset
                gui_cursor_y += y_offset + 30

                # Update the cursor position in the GUI
                cursor_canvas.place(x=gui_cursor_x, y=gui_cursor_y)


                # Simulate a left-click
            if pinch_distance < pinch_threshold:
                # Check if the pinch overlaps with any button
                for button in [start_button, pause_button, reset_button, play_button, add_button, *music_inner_frame.winfo_children()]:
                    x1, y1, x2, y2 = get_button_bbox(button)
                    #gui_cursor_x = int(cursor_position[0] / frame.shape[1] * root.winfo_width())
                    #gui_cursor_y = int(cursor_position[1] / frame.shape[0] * root.winfo_height())
                    
                    if x1 <= gui_cursor_x <= x2 and y1 <= gui_cursor_y <= y2:
                        button.invoke()  # Simulate a button click
                        break
                print(f"Frame Size: {frame.shape[1]}x{frame.shape[0]}")
                print(f"GUI Size: {root.winfo_width()}x{root.winfo_height()}")
                print(f"Mapped Cursor Position: ({gui_cursor_x}, {gui_cursor_y})")

                print(f"Click at: ({gui_cursor_x}, {gui_cursor_y})")

    # Update the cursor position in the GUI
    if cursor_position:
        gui_cursor_x = int(cursor_position[0] / frame.shape[1] * gui_width)
        gui_cursor_y = int(cursor_position[1] / frame.shape[0] * gui_height)

        # Apply the same offset
        y_offset = 30
        gui_cursor_y += y_offset

        cursor_canvas.place(x=gui_cursor_x, y=gui_cursor_y)

    # Show the frame in OpenCV window
    cv2.imshow('Gesture Detection', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        root.destroy()
        return

    root.after(10, detect_gesture_loop)



def get_button_bbox(button):
    """Calculate the bounding box of a button in GUI coordinates."""
    x1, y1 = button.winfo_rootx(), button.winfo_rooty()
    x2, y2 = x1 + button.winfo_width(), y1 + button.winfo_height()
    return x1, y1, x2, y2



# Initialize OpenCV capture
cap = cv2.VideoCapture(0)

# Start the gesture detection loop
root.after(10, detect_gesture_loop)

# Run the application
root.mainloop()

# Release resources when the application closes
cap.release()
cv2.destroyAllWindows()
