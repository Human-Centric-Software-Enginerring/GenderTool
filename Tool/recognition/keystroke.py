#1 : This script keeps taking in Lines of code typed based on how often Enter key is pressed. Stops on pressing Esc key.
# from pynput import keyboard
# line_count = 0
# def on_press(key):
#     global line_count
#     try:
#         if key.char == '\n':  # For newline character
#             line_count += 1
#     except AttributeError:
#         if key == keyboard.Key.enter:  # For Enter key
#             line_count += 1
#     print(f"Lines of code typed: {line_count}")
# def on_release(key):
#     if key == keyboard.Key.esc:  # Stop listener
#         return False
# with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
#     listener.join()


#2. Script performs same task but lighter and more efficient. Better if we don't require mouse events
import keyboard
line_count = 0
def count_newline(event):
    global line_count
    if event.name == 'enter':
        line_count += 1
        print(f"Lines of code typed: {line_count}")

keyboard.on_press(count_newline)
# Keep the program running
keyboard.wait('esc')  # Press 'esc' to stop the program

