import cv2
import mediapipe as mp
import tkinter as tk
from tkinter import ttk
import numpy as np

# Initialize MediaPipe hand detector
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils

# Initialize Tkinter GUI
root = tk.Tk()
root.title("Gesture-Based Interactive Interface")
root.geometry("400x600")

# Frame for scrollable area
frame_main = tk.Frame(root)
frame_main.pack(fill=tk.BOTH, expand=True)

# Adding Canvas for scrollable area
canvas = tk.Canvas(frame_main)
scrollbar = ttk.Scrollbar(frame_main, orient="vertical", command=canvas.yview)
scrollable_frame = ttk.Frame(canvas)

# Configure scroll behavior
scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)
canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# Add interactive buttons in scrollable frame
buttons = []
for i in range(10):
    button = ttk.Button(scrollable_frame, text=f"Button {i+1}")
    button.pack(pady=5, padx=5)
    buttons.append(button)

# Functions to handle scroll and button actions
def scroll_up():
    canvas.yview_scroll(-1, "units")

def scroll_down():
    canvas.yview_scroll(1, "units")

def simulate_button_click(button_id):
    buttons[button_id].invoke()

# OpenCV Video Capture for Gesture Recognition
cap = cv2.VideoCapture(0)

def detect_gesture():
    _, frame = cap.read()
    frame = cv2.flip(frame, 1)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)
    
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            # Get coordinates of thumb and index finger for pinch detection
            thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
            index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            
            # Calculate pixel coordinates
            thumb_coords = (int(thumb_tip.x * frame.shape[1]), int(thumb_tip.y * frame.shape[0]))
            index_coords = (int(index_tip.x * frame.shape[1]), int(index_tip.y * frame.shape[0]))

            # Distance between thumb and index to detect pinch
            distance = np.sqrt((thumb_coords[0] - index_coords[0]) ** 2 + (thumb_coords[1] - index_coords[1]) ** 2)
            
            # Define gesture actions based on distance and hand position
            if distance < 30:
                # Pinch gesture detected - Simulate a button click
                simulate_button_click(0)  # Replace 0 with logic to detect which button to click

            # Use hand y-coordinate to control scrolling
            if thumb_coords[1] < frame.shape[0] // 3:
                scroll_up()
            elif thumb_coords[1] > 2 * frame.shape[0] // 3:
                scroll_down()
    
    # Display the frame
    cv2.imshow("Gesture Control", frame)
    cv2.waitKey(1)
    
    # Re-run this function after a short delay
    root.after(10, detect_gesture)

# Start gesture detection loop
root.after(10, detect_gesture)

# Run Tkinter main loop
root.mainloop()

# Release the capture after GUI is closed
cap.release()
cv2.destroyAllWindows()