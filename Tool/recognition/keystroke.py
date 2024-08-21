import keyboard
import time
import json
from win32gui import GetWindowText, GetForegroundWindow
from threading import Timer

line_count = 0
stop_program = False

def count_newline(event):
    global line_count
    # Check if the active window is Visual Studio Code
    if "Visual Studio Code" in GetWindowText(GetForegroundWindow()):
        if event.name == 'enter':
            line_count += 1

def stop_collection():
    global stop_program
    stop_program = True
    keyboard.unhook_all()  # Unhook all keyboard events

def save_data_to_file():
    # Save the line count to a JSON file
    data = {"lines_of_code": line_count}
    with open("keystroke_data.json", "w") as json_file:
        json.dump(data, json_file, indent=4)

keyboard.on_press(count_newline)

# Set a timer to stop data collection after 5 minutes (300 seconds)
timer = Timer(300, stop_collection)
timer.start()

# Keep the program running until `stop_program` is True
while not stop_program:
    time.sleep(1)

# Save the data when the program ends
print(f"Lines of code typed: {line_count}")
save_data_to_file()

