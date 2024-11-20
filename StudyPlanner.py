import customtkinter as ctk
from tkinter import Canvas, Scrollbar, VERTICAL

# Initialize CustomTkinter GUI
ctk.set_appearance_mode("dark")
root = ctk.CTk()
root.title("Study Planner")
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

# -----------------------------------
# Frame 1: Study Planner Timer
# -----------------------------------
frame1 = ctk.CTkFrame(scrollable_frame, fg_color="darkgray", corner_radius=10)
frame1.pack(pady=10, padx=10, fill="x")

# Title
title_label = ctk.CTkLabel(frame1, text="Study Planner", font=("Helvetica", 20, "bold"), text_color="white")
title_label.pack(pady=10)

# Timer
timer_canvas = Canvas(frame1, width=200, height=200, bg="black", highlightthickness=0)
timer_canvas.pack(pady=10)
timer_radius = 90
center_x, center_y = 100, 100

timer_circle = timer_canvas.create_oval(
    center_x - timer_radius, center_y - timer_radius,
    center_x + timer_radius, center_y + timer_radius,
    fill="darkgray", outline="lightgray", width=2
)
timer_text = timer_canvas.create_text(
    center_x, center_y, text="25:00", font=("Helvetica", 24, "bold"), fill="white"
)

# Timer Controls
controls_frame = ctk.CTkFrame(frame1, fg_color="black", corner_radius=5)
controls_frame.pack(pady=10)

start_button = ctk.CTkButton(controls_frame, text="▶ Start", command=lambda: print("Start Timer"))
start_button.pack(side="left", padx=5)

pause_button = ctk.CTkButton(controls_frame, text="⏸ Pause", command=lambda: print("Pause Timer"))
pause_button.pack(side="left", padx=5)

reset_button = ctk.CTkButton(controls_frame, text="⏹ Reset", command=lambda: print("Reset Timer"))
reset_button.pack(side="left", padx=5)

# Tasks Section (Frame 1)
tasks_frame = ctk.CTkFrame(frame1, fg_color="darkgray", corner_radius=10)
tasks_frame.pack(pady=10, fill="x")

tasks_label = ctk.CTkLabel(tasks_frame, text="Tasks", font=("Helvetica", 16, "bold"), text_color="white")
tasks_label.pack(pady=5)

add_task_button = ctk.CTkButton(tasks_frame, text="+ Add Task", command=lambda: print("Add Task"))
add_task_button.pack(pady=5)

# -----------------------------------
# Frame 2: Tasks & Music
# -----------------------------------
frame2 = ctk.CTkFrame(scrollable_frame, fg_color="darkgray", corner_radius=10)
frame2.pack(pady=10, padx=10, fill="x")

# Tasks Section (Frame 2)
tasks_label_frame2 = ctk.CTkLabel(frame2, text="Tasks", font=("Helvetica", 16, "bold"), text_color="white")
tasks_label_frame2.pack(pady=10)

task_list_frame2 = ctk.CTkFrame(frame2, fg_color="black", corner_radius=5)
task_list_frame2.pack(fill="x", padx=10)

task_list = ["Task 1", "Task 2", "Task 3", "Task 4"]
for task in task_list:
    task_label = ctk.CTkLabel(task_list_frame2, text=f"• {task}", font=("Helvetica", 14), text_color="white")
    task_label.pack(anchor="w", padx=10, pady=5)

# Music Section (Frame 2)
music_frame = ctk.CTkFrame(frame2, fg_color="darkgray", corner_radius=10)
music_frame.pack(pady=10, fill="x")

music_label = ctk.CTkLabel(music_frame, text="Music", font=("Helvetica", 16, "bold"), text_color="white")
music_label.pack(pady=5)

# Music Controls
music_controls_frame = ctk.CTkFrame(music_frame, fg_color="black", corner_radius=5)
music_controls_frame.pack(pady=5)

music_buttons = ["Music 1", "Music 2", "Music 3", "Music 4"]
for music in music_buttons:
    music_button = ctk.CTkButton(music_controls_frame, text=music, command=lambda m=music: print(f"Playing {m}"))
    music_button.pack(side="left", padx=5, pady=5)

# -----------------------------------
# Run the Application
# -----------------------------------
root.mainloop()
