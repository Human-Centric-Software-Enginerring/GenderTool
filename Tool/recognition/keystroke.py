import keyboard
import time
from win32gui import GetWindowText, GetForegroundWindow

line_count = 0

def count_newline(event):
    global line_count
    # Check if the active window is Visual Studio Code
    if "Visual Studio Code" in GetWindowText(GetForegroundWindow()):
        if event.name == 'enter':
            line_count += 1
            print(f"Lines of code typed: {line_count}")

keyboard.on_press(count_newline)

# Keep the program running
keyboard.wait('esc')  # Press 'esc' to stop the program
