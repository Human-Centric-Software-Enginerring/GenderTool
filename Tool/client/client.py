import platform
import subprocess
import asyncio
import websockets
import json
import os
import threading

def get_device_id():
    system = platform.system()

    if system == "Windows":
        return get_windows_device_id()
    elif system == "Linux" or system == "Darwin":
        return get_unix_device_id()
    else:
        raise Exception("Unsupported OS")

def get_windows_device_id():
    try:
        output = subprocess.check_output("wmic csproduct get uuid", shell=True).decode().strip()
        device_id = output.split("\n")[1].strip()
        return device_id
    except Exception as e:
        print(f"Error getting Windows device ID: {e}")
        return None

def get_unix_device_id():
    try:
        if platform.system() == "Linux":
            output = subprocess.check_output("cat /sys/class/dmi/id/product_uuid", shell=True).decode().strip()
        elif platform.system() == "Darwin":
            output = subprocess.check_output("system_profiler SPHardwareDataType | grep 'Hardware UUID:'", shell=True).decode().split(':')[1].strip()
        return output
    except Exception as e:
        print(f"Error getting Unix device ID: {e}")
        return None

async def connect_to_server(device_id, session_id):
    uri = "ws://localhost:8765"
    print(f"Connecting to server at {uri}...")
    try:
        async with websockets.connect(uri, close_timeout=10) as websocket:
            print(f"Connected to server")
            
            # Send device_id and session_id to the server
            data = {"device_id": device_id, "session_id": session_id}
            await websocket.send(json.dumps(data))
            print("Device ID and Session ID sent to server")
            response = await websocket.recv()
            print(f"Response from server: {response}")
            # Parse the JSON response
            parsed_response = json.loads(response)
            # Extract and store the user_id
            user_id = parsed_response.get("user_id")
            # Now, you can use the user_id variable later in your script
            print(f"Stored user_id: {user_id}")
            trigger_scripts()
            # Use the generated data
            process_generated_data()
    except websockets.exceptions.ConnectionClosedError as e:
        print(f"WebSocket connection closed with error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

def trigger_scripts():
    # Function to run scripts and wait for them to complete
    base_dir = "D:\\HCI_Research\\GenderTool\\Tool\\recognition"
    def run_script(script_name):
        script_path = os.path.join(base_dir, script_name)
        os.system(f"python {script_path}")

    # Start the scripts in separate threads
    threads = []
    for script in ["utterances.py", "face_detection.py","keystroke.py"]:
        thread = threading.Thread(target=run_script, args=(script,))
        thread.start()
        threads.append(thread)

    # Wait for all scripts to complete
    for thread in threads:
        thread.join()

def process_generated_data():
    # Load and process keystroke data
    with open("keystroke_data.json", "r") as f:
        keystroke_data = json.load(f)
    # Load and process utterances data
    with open("utterance_data.json", "r") as f:
        utterances_data = json.load(f)
    # Load and process face detection data
    with open("face_detection_data.json", "r") as f:
        face_detection_data = json.load(f)
        print(f"\nFace Detection Data: {face_detection_data}")

def main():
    device_id = get_device_id()
    if device_id:
        print(f"Device ID: {device_id}")
    else:
        print("Failed to obtain device ID.")
        return

    session_id = "001" #will take session_id from user
    asyncio.get_event_loop().run_until_complete(connect_to_server(device_id, session_id))

if __name__ == "__main__":
    main()
