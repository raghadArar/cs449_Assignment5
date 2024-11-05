
import customtkinter as ctk
import cv2
import mediapipe as mp
import math
from PIL import Image, ImageTk

# Initialize MediaPipe hand detector
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils

# Initialize CustomTkinter GUI
ctk.set_appearance_mode("light")
root = ctk.CTk()
root.title("Gesture-Based Radial Menu")
root.geometry("500x600")  # Increased height to accommodate the selection panel below
root.configure(bg="white")

# Canvas for radial menu and selection panel
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
segment_angle = 360 / num_options

# Load images for each segment and keep references
icon_images = [ImageTk.PhotoImage(Image.open(icon_path).resize((40, 40))) for icon_path in options]

# Draw segments for the radial menu
segments = []
for i in range(num_options):
    start_angle = i * segment_angle
    segment = canvas.create_arc(
        center_x - radius_outer, center_y - radius_outer,
        center_x + radius_outer, center_y + radius_outer,
        start=start_angle, extent=segment_angle, fill="lightgray", outline="darkgray", width=2
    )
    segments.append(segment)

    # Calculate icon position within each segment
    angle_rad = math.radians(start_angle + segment_angle / 2)
    icon_x = center_x + (radius_inner + (radius_outer - radius_inner) / 2) * math.cos(angle_rad)
    icon_y = center_y - (radius_inner + (radius_outer - radius_inner) / 2) * math.sin(angle_rad)
    canvas.create_image(icon_x, icon_y, image=icon_images[i])

# Divider Circle (white ring) between volume and main sectors
divider_radius = 75
canvas.create_oval(
    center_x - divider_radius, center_y - divider_radius,
    center_x + divider_radius, center_y + divider_radius, fill="white",
    outline="white", width=4
)

# Central volume control
volume_radius = 50
canvas.create_oval(center_x - volume_radius, center_y - volume_radius, 
                   center_x + volume_radius, center_y + volume_radius, 
                   fill="darkgray", outline="lightgray", width=2)
volume_text = canvas.create_text(center_x, center_y, text="Volume\n62%", font=("Helvetica", 12, "bold"), fill="black")

# Initialize volume
current_volume = 62

# Initialize OpenCV capture
cap = cv2.VideoCapture(0)

# Load the custom cursor icon
cursor_icon = ImageTk.PhotoImage(Image.open("cursor-icon.png").resize((30, 30)))
cursor = canvas.create_image(-100, -100, image=cursor_icon)  # Initially place cursor off-screen

# Global variable to track the last selected sector
last_selected_sector = None
selection_frame_count = 0  # Counter for stable selection

# Selection panel items (initially hidden)
selection_panel_items = []

# Function to draw the selection panel as an extension of the selected segment, divided into three sections
def draw_selection_panel(selected_option_index):
    # Calculate the angle for the selected segment
    start_angle = selected_option_index * segment_angle
    extent = segment_angle

    # Define outer radius for the extended segment
    panel_radius_outer = radius_outer + 50  # Slightly larger than the main menu radius
    panel_radius_inner = radius_inner / 2  # Smaller inner radius to avoid covering the main canvas

    # Draw the extended portion of the selected segment as the selection panel, divided into three parts
    sub_arc_extent = extent / 3  # Divide the arc into three equal parts
    button_labels = ["Origin", "Info", "Sound"]

    for i, label in enumerate(button_labels):
        # Calculate the start angle for each sub-arc
        sub_arc_start_angle = start_angle + i * sub_arc_extent

        # Draw each sub-arc segment (without borders around each "button" section)
        sub_arc = canvas.create_arc(
            center_x - panel_radius_outer, center_y - panel_radius_outer,
            center_x + panel_radius_outer, center_y + panel_radius_outer,
            start=sub_arc_start_angle, extent=sub_arc_extent, fill="darkgray", outline="black", width=2
        )

        # Calculate the position for the label in the center of each sub-arc
        label_angle = math.radians(sub_arc_start_angle + sub_arc_extent / 2)
        label_x = center_x + (panel_radius_inner + (panel_radius_outer - panel_radius_inner) / 2) * math.cos(label_angle)
        label_y = center_y - (panel_radius_inner + (panel_radius_outer - panel_radius_inner) / 2) * math.sin(label_angle)

        # Add the label text at the center of each sub-arc
        label_text = canvas.create_text(
            label_x, label_y, text=label, font=("Helvetica", 10, "bold"), fill="black"
        )

        # Bind each sub-arc segment to a click event
        def on_button_click(event, option=label):
            print(f"{option} clicked for segment {selected_option_index + 1}")

        # Make the sub-arc clickable by binding it to the event
        canvas.tag_bind(sub_arc, "<Button-1>", on_button_click)

    # Redraw all original segments to overlay and mask the inner part of the selection panel
    for i in range(num_options):
        segment_color = "lightgray" if i != selected_option_index else "darkgray"  # Highlight selected segment
        segment_outline = "darkgray" if i != selected_option_index else "black"
        
        # Draw each segment
        segment = canvas.create_arc(
            center_x - radius_outer, center_y - radius_outer,
            center_x + radius_outer, center_y + radius_outer,
            start=i * segment_angle, extent=segment_angle, fill=segment_color, outline=segment_outline, width=2
        )

        # Draw the animal icon for each segment
        angle_rad = math.radians(i * segment_angle + segment_angle / 2)
        icon_x = center_x + (radius_inner + (radius_outer - radius_inner) / 2) * math.cos(angle_rad)
        icon_y = center_y - (radius_inner + (radius_outer - radius_inner) / 2) * math.sin(angle_rad)
        canvas.create_image(icon_x, icon_y, image=icon_images[i])
    # Divider Circle (white ring) between volume and main sectors
    divider_radius = 75
    canvas.create_oval(
        center_x - divider_radius, center_y - divider_radius,
        center_x + divider_radius, center_y + divider_radius, fill="white",
        outline="white", width=4
    )
    # Central volume control
    volume_radius = 50
    canvas.create_oval(center_x - volume_radius, center_y - volume_radius, 
                    center_x + volume_radius, center_y + volume_radius, 
                    fill="darkgray", outline="lightgray", width=2)
    volume_text = canvas.create_text(center_x, center_y, text="Volume\n62%", font=("Helvetica", 12, "bold"), fill="black")
    ##how to maintain volume numbers?

# Function to hide the selection panel by clearing the items
def hide_selection_panel():
    global selection_panel_items
    for item in selection_panel_items:
        canvas.delete(item)
    selection_panel_items.clear()

# Updated detect_gesture function
def detect_gesture():
    global current_volume, last_selected_sector, selection_frame_count
    success, frame = cap.read()
    if not success:
        print("Ignoring empty camera frame.")
        root.after(10, detect_gesture)
        return

    # Flip and process the frame
    frame = cv2.flip(frame, 1)
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(image)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(
                frame, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=2),
                mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2, circle_radius=2)
            )

            # Index finger tip's position on the canvas
            index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            canvas_x_index = int(index_tip.x * canvas.winfo_width())
            canvas_y_index = int(index_tip.y * canvas.winfo_height())
            canvas.coords(cursor, canvas_x_index, canvas_y_index)

            # Check if only index and middle fingers are raised, or if index, middle, and ring are raised
            finger_tips = [hand_landmarks.landmark[f] for f in [
                mp_hands.HandLandmark.THUMB_TIP,
                mp_hands.HandLandmark.INDEX_FINGER_TIP,
                mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
                mp_hands.HandLandmark.RING_FINGER_TIP,
                mp_hands.HandLandmark.PINKY_TIP
            ]]
            only_index_middle_raised = (
                finger_tips[1].y < finger_tips[0].y and finger_tips[2].y < finger_tips[0].y and
                finger_tips[1].y < finger_tips[3].y and finger_tips[2].y < finger_tips[4].y and
                finger_tips[3].y > finger_tips[0].y  # Ring finger is down
            )

            index_middle_ring_raised = (
                finger_tips[1].y < finger_tips[0].y and finger_tips[2].y < finger_tips[0].y and
                finger_tips[3].y < finger_tips[0].y  # Index, middle, and ring fingers are up
            )

            if index_middle_ring_raised:
                # Hide selection if index, middle, and ring fingers are raised
                hide_selection_panel()
                last_selected_sector = None  # Reset selection
                selection_frame_count = 0  # Reset frame count

            elif only_index_middle_raised:
                for i, segment in enumerate(segments):
                    start_angle = i * segment_angle
                    end_angle = start_angle + segment_angle

                    rel_x_index = canvas_x_index - center_x
                    rel_y_index = center_y - canvas_y_index
                    angle_index = (math.degrees(math.atan2(rel_y_index, rel_x_index)) + 360) % 360
                    distance_index = math.sqrt(rel_x_index ** 2 + rel_y_index ** 2)
                    if start_angle <= angle_index < end_angle and radius_inner < distance_index < radius_outer:
                        selection_frame_count += 1
                        canvas.itemconfig(segment, fill="cyan")
                        draw_selection_panel(i)
                        # if selection_frame_count > 5 and last_selected_sector != options[i]:
                        #     last_selected_sector = options[i]
                        #     draw_selection_panel(options[i])
                        #     selection_frame_count = 0
                    else:
                        canvas.itemconfig(segment, fill="lightgray")
                        selection_frame_count = 0  # Reset frame count when fingers are not stable

    # Show frame and update loop
    cv2.imshow("Gesture Control", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        root.quit()
        return
    
    root.after(10, detect_gesture)

# Start gesture detection loop
root.after(10, detect_gesture)
root.mainloop()
cap.release()
cv2.destroyAllWindows()
