import keyboard
import time
import json
from win32gui import GetWindowText, GetForegroundWindow
from threading import Timer
import requests

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

def send_data_to_api():
    # Save the line count to a JSON file
    data = {"lines_of_code": line_count}
    try:
        response = requests.post("http://127.0.0.1:8000/update-keystrokes", json=data)
        #print(f"Keystroke data sent to API: {response.status_code}")
    except Exception as e:
        print(f"Failed to send data to API: {e}")

keyboard.on_press(count_newline)

# Set a timer to stop data collection after 5 minutes (300 seconds)
timer = Timer(30, stop_collection)
timer.start()

# Keep the program running until `stop_program` is True
while not stop_program:
    time.sleep(1)

# Save the data when the program ends
#print(f"Lines of code typed: {line_count}")
send_data_to_api()

