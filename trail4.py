import customtkinter as ctk
import cv2
import mediapipe as mp
import numpy as np
import math
from PIL import Image, ImageTk

# Initialize MediaPipe hand detector
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils

# Initialize CustomTkinter GUI
ctk.set_appearance_mode("light")  # Set light mode to match white background
root = ctk.CTk()
root.title("Gesture-Based Radial Menu")
root.geometry("500x500")
root.configure(bg="white")  # Set background color to white

# Canvas for radial menu
canvas = ctk.CTkCanvas(root, width=500, height=500, bg="white", highlightthickness=0)
canvas.pack()

# Radial menu settings
center_x, center_y = 250, 250
radius_outer = 200
radius_inner = 100
options = [
    "elephant.png", "lion.png", "monkey.png", "elephant.png", 
    "lion.png", "monkey.png", "elephant.png", "lion.png"
]
num_options = len(options)

# Load images for each segment and keep references
icon_images = [ImageTk.PhotoImage(Image.open(icon_path).resize((40, 40))) for icon_path in options]

# Draw segments for the radial menu
segments = []
for i in range(num_options):
    start_angle = i * 360 / num_options
    extent = 360 / num_options
    # Create each segment as an arc (slice)
    segment = canvas.create_arc(center_x - radius_outer, center_y - radius_outer,
                                center_x + radius_outer, center_y + radius_outer,
                                start=start_angle, extent=extent, fill="lightgray", outline="white", width=2)
    segments.append(segment)

    # Calculate icon position within each segment
    angle_rad = math.radians(start_angle + extent / 2)
    icon_x = center_x + (radius_inner + (radius_outer - radius_inner) / 2) * math.cos(angle_rad)
    icon_y = center_y - (radius_inner + (radius_outer - radius_inner) / 2) * math.sin(angle_rad)

    # Place icon at calculated position
    canvas.create_image(icon_x, icon_y, image=icon_images[i])

# Central volume control with a circular indicator
volume_radius = 50
canvas.create_oval(center_x - volume_radius, center_y - volume_radius, 
                   center_x + volume_radius, center_y + volume_radius, 
                   fill="darkgray", outline="lightgray", width=2)
volume_text = canvas.create_text(center_x, center_y, text="Volume\n62%", font=("Helvetica", 12, "bold"), fill="black")

# Track the volume level and volume indicator arc ID
current_volume = 62
volume_arc_id = None  # To keep track of the arc ID for the circular indicator

# Function to update the volume indicator
def update_volume_indicator(volume_level):
    global volume_arc_id
    # Clear the previous arc
    if volume_arc_id:
        canvas.delete(volume_arc_id)
    
    # Calculate angle based on volume
    angle_end = (volume_level / 100) * 360
    
    # Draw new arc for the current volume level
    volume_arc_id = canvas.create_arc(center_x - volume_radius, center_y - volume_radius, 
                                      center_x + volume_radius, center_y + volume_radius,
                                      start=0, extent=angle_end, style="arc", outline="cyan", width=6)

# Initial volume display
update_volume_indicator(current_volume)
# Custom cursor icon
cursor_icon = ImageTk.PhotoImage(Image.open("cursor-icon.png").resize((30, 30)))  # Load and resize cursor icon
cursor = canvas.create_image(-100, -100, image=cursor_icon)  # Initially place cursor off-screen

# Initialize OpenCV capture
cap = cv2.VideoCapture(0)
current_volume = 62

# Function to update the volume display
def update_volume_display(volume_level):
    canvas.itemconfig(volume_label, text=f"Volume\n{volume_level}%")

# Function to detect gestures and interact with radial menu
def detect_gesture():
    global current_volume
    success, frame = cap.read()
    if not success:
        print("Ignoring empty camera frame.")
        return

    # Flip the frame horizontally for selfie-view
    frame = cv2.flip(frame, 1)

    # Convert the BGR image to RGB
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process the image and find hands
    results = hands.process(image)

    if results.multi_hand_landmarks:
        for hand_index, hand_landmarks in enumerate(results.multi_hand_landmarks):
            mp_drawing.draw_landmarks(
                frame, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=2),
                mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2, circle_radius=2)
            )

            # Get the index finger tip coordinates for each hand
            index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            canvas_width, canvas_height = root.winfo_width(), root.winfo_height()

            # Calculate the position of the fingertip on the radial menu canvas
            canvas_x = int(index_tip.x * canvas_width)
            canvas_y = int(index_tip.y * canvas_height)

            # Update the cursor position
            canvas.coords(cursor, canvas_x, canvas_y)

            # Check if the index finger is hovering over any segment
            for i, segment in enumerate(segments):
                start_angle = i * 360 / num_options
                end_angle = start_angle + 360 / num_options

                # Calculate angle of the finger relative to center
                rel_x, rel_y = canvas_x - center_x, center_y - canvas_y  # inverted y-axis for Tkinter
                angle = (math.degrees(math.atan2(rel_y, rel_x)) + 360) % 360  # normalize angle to [0, 360]

                # Calculate distance from the center
                distance = math.sqrt(rel_x ** 2 + rel_y ** 2)

                # Check if the angle and distance place the finger within this segment
                if start_angle <= angle < end_angle and radius_inner < distance < radius_outer:
                    canvas.itemconfig(segment, fill="cyan")  # Highlight segment
                else:
                    canvas.itemconfig(segment, fill="lightgray")  # Reset segment color

            # Use thumb y-coordinate to control volume
            thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
            thumb_y = thumb_tip.y * frame.shape[0]
            
            if thumb_y < frame.shape[0] // 3:
                current_volume = min(100, current_volume + 1)
            elif thumb_y > 2 * frame.shape[0] // 3:
                current_volume = max(0, current_volume - 1)
            
            # Update volume display
            update_volume_display(current_volume)

    # Show the frame with landmarks in OpenCV window
    cv2.imshow("Gesture Control", frame)
    cv2.waitKey(1)

    # Call the function again to keep the gesture detection loop running
    root.after(10, detect_gesture)

# Start gesture detection loop
root.after(10, detect_gesture)
root.mainloop()
cap.release()
cv2.destroyAllWindows()
