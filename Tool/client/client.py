import platform
import subprocess
import asyncio
import websockets
import json

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
    async with websockets.connect(uri) as websocket:
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
