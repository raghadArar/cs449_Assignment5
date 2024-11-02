import customtkinter as ctk
import cv2
import mediapipe as mp
import numpy as np
import math

# Initialize MediaPipe hand detector
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils

# Initialize CustomTkinter GUI
ctk.set_appearance_mode("dark")
root = ctk.CTk()
root.title("Gesture-Based Radial Menu")
root.geometry("500x500")

# Set background color of the root
root.configure(bg="black")

# Canvas for radial menu
canvas = ctk.CTkCanvas(root, width=500, height=500, bg="black", highlightthickness=0)
canvas.pack()

# Text options for radial menu buttons
options = [
    "Elephant", "Monkey", "Cat",
    "Lion", "Dog", "Cow",
    "Duck", "Sheep"
]

# Radial menu settings
center_x, center_y = 250, 250
radius = 150
num_options = len(options)

# Add text options in circular layout with rounded backgrounds
buttons = []
button_backgrounds = []
for i, option in enumerate(options):
    angle = 2 * math.pi * i / num_options
    option_x = center_x + radius * math.cos(angle)
    option_y = center_y + radius * math.sin(angle)
    
    # Draw a rounded circle as button background with shadow effect
    rect = canvas.create_oval(option_x - 40, option_y - 40, option_x + 40, option_y + 40, 
                               fill="lightgray", outline="gray", width=2)
    button_backgrounds.append(rect)
    
    # Button text
    button = canvas.create_text(option_x, option_y, text=option, font=("Helvetica", 12, "bold"), fill="black")
    buttons.append(button)

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

cursor_radius = 5
cursor = canvas.create_oval(-cursor_radius, -cursor_radius, cursor_radius, cursor_radius, fill="cyan", outline="")

cap = cv2.VideoCapture(0)

def detect_gesture():
    global current_volume
    success, frame = cap.read()
    if not success:
        print("Ignoring empty camera frame.")
        return

    # Flip the frame horizontally for a later selfie-view display
    frame = cv2.flip(frame, 1)

    # Convert the BGR image to RGB
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process the image and find hands
    results = hands.process(image)

    # Draw the hand annotations on the image
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    # Clear previous cursor position
    canvas.itemconfig(cursor, fill="cyan")

    if results.multi_hand_landmarks:
        for hand_index, hand_landmarks in enumerate(results.multi_hand_landmarks):
            # Draw landmarks and connections on the frame
            mp_drawing.draw_landmarks(
                frame, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=2),
                mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2, circle_radius=2)
            )

            # Get the index finger tip coordinates for each hand
            index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            canvas_width = canvas.winfo_width()
            canvas_height = canvas.winfo_height()

            canvas_x = int(index_tip.x * canvas_width)
            canvas_y = int(index_tip.y * canvas_height)

            # Update the cursor position
            canvas.coords(cursor, canvas_x - cursor_radius, canvas_y - cursor_radius, 
                          canvas_x + cursor_radius, canvas_y + cursor_radius)

            # Check if the index finger is hovering over any text option
            for i, button in enumerate(button_backgrounds):
                button_bbox = canvas.bbox(button)
                
                if button_bbox:
                    # Calculate center of the button
                    button_x = (button_bbox[0] + button_bbox[2]) / 2  
                    button_y = (button_bbox[1] + button_bbox[3]) / 2
                    
                    hand_to_button_distance = np.sqrt((button_x - canvas_x) ** 2 + (button_y - canvas_y) ** 2)

                    # If hovering within a certain distance, change background color
                    if hand_to_button_distance < 50:
                        canvas.itemconfig(button, fill="cyan")
                    else:
                        canvas.itemconfig(button, fill="lightgray")

            # Use thumb y-coordinate to control volume (scroll effect)
            thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
            thumb_coords = (int(thumb_tip.x * frame.shape[1]), int(thumb_tip.y * frame.shape[0]))
            
            if thumb_coords[1] < frame.shape[0] // 3:
                current_volume = min(100, current_volume + 1)
            elif thumb_coords[1] > 2 * frame.shape[0] // 3:
                current_volume = max(0, current_volume - 1)
            
            # Update volume text and circular indicator
            canvas.itemconfig(volume_text, text=f"Volume\n{current_volume}%")
            update_volume_indicator(current_volume)
    else:
        print("No hand landmarks detected")
    
    # Display the frame with landmarks in OpenCV window
    cv2.imshow("Gesture Control", frame)
    cv2.waitKey(1)
    
    root.after(10, detect_gesture)

# Start gesture detection loop
root.after(10, detect_gesture)
root.mainloop()
cap.release()
cv2.destroyAllWindows()
