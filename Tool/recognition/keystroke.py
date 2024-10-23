import keyboard
import time
import json
from win32gui import GetWindowText, GetForegroundWindow
from threading import Timer, Thread
import requests

line_count = 0
stop_program = False
send_interval = 30  # 30 seconds

def count_keypress(event):
    global line_count
    # Check if the active window is Visual Studio Code
    window_title = GetWindowText(GetForegroundWindow())
    if "Visual Studio Code" in window_title:
        if event.name == 'enter':
            line_count += 1  # Increment for 'enter'
        elif event.name == 'backspace':
            line_count -= 1  # Decrement for 'backspace'
        else:
            # List of keys to ignore
            ignore_keys = ['tab', 'caps lock', 'ctrl', 'windows', 'alt', 'esc', 
                           'shift', 'left shift', 'right shift', 'up', 'down', 
                           'left', 'right', 'page up', 'page down', 'home', 
                           'end', 'fn','space']
            
            # Count other keypresses as characters typed, excluding specified keys
            if len(event.name) == 1 and event.name not in ignore_keys:
                line_count += 1

def stop_collection():
    global stop_program
    stop_program = True
    keyboard.unhook_all()  # Unhook all keyboard events

def send_data_to_api():
    global line_count
    # Prepare the data to be sent
    data = {"lines_of_code": line_count}
    try:
        response = requests.post("http://127.0.0.1:8000/update-keystrokes", json=data)
        if response.status_code == 200:
            print(f"Keystroke data sent to API: {line_count} characters")
        else:
            print(f"Failed to send data to API: {response.status_code}")
    except Exception as e:
        print(f"Failed to send data to API: {e}")
    line_count = 0  # Reset the line count after sending

def collect_data():
    while not stop_program:
        time.sleep(send_interval)  # Wait for 30 seconds
        send_data_to_api()  # Send the collected data every 30 seconds

# Start the data collection process
if __name__ == "__main__":
    # Hook the keyboard events
    keyboard.on_press(count_keypress)

    # Start the thread to send data every 30 seconds
    data_thread = Thread(target=collect_data)
    data_thread.start()

    # Set a timer to stop data collection after a certain period if needed
    timer = Timer(60, stop_collection)  # Stop after 30 seconds (adjust as needed)
    timer.start()

    # Keep the program running until `stop_program` is True
    while not stop_program:
        time.sleep(1)

    #print(line_count)
    # Send the remaining data before stopping
    #send_data_to_api()
