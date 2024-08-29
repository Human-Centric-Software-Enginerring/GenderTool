import platform
import subprocess
import asyncio
import websockets
import json
import os
import threading

# Helper functions
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

def rapport_score(utterances):
    import re
    score = 0
    keywords = [r"hm", r"um", r"ha", r"uh", r"oh"]
    for event in utterances:
        if event["event"].lower() not in ["speech", "pause"]:
            score += 1
        elif event["event"].lower() == "speech":
            for keyword in keywords:
                if re.search(keyword, event["transcription"].lower()):
                    score += 1
    return score

def processed_utterance_data(utterances):
    processed_data = []
    for utterance in utterances:
        processed_utterance = {
            "start_timestamp": utterance["start_timestamp"],
            "end_timestamp": utterance["end_timestamp"],
            "event": utterance["event"]
        }
        processed_data.append(processed_utterance)
    return processed_data

#processing interval data
def determine_user_role(loc1,loc2):
    X1  = loc1/(loc1 + loc2)
    X2 = loc2/(loc1+loc2)
    if X1 > X2:
        return "Driver"
    else:
        return "Navigator"

#need speech_data from database
def interruptions(utterances1,utterances2):
    user1_interruptions = 0
    user2_interruptions = 0

    # Iterate over each event in user1's data
    for event1 in utterances1:
        start1 = event1['start_timestamp']
        end1 = event1['end_timestamp']

        # Check for interruptions by user2 during user1's event
        for event2 in utterances2:
            start2 = event2['start_timestamp']
            if event1['event'] == 'speech' and event2['event'] == 'speech' and start1 <= start2 <= end1:
                print(event1,event2,"\n")
                user2_interruptions += 1
    return user1_interruptions

def communication_style(emotions,utterances):
    non_verbal = len(emotions) + sum(1 for event in utterances if event["event"].lower() not in ["speech", "pause"])
    verbal = sum(1 for event in utterances if event["event"].lower() == "speech")
    if non_verbal > verbal:
        return "Non-Verbal"
    else:
        "Verbal"

def self_efficacy(emotions):
    positive = ["happy","neutral","surprise"]
    negative = ["sad","fear","angry"]
    high,low = 0,0
    for event in emotions:
        emotion = event['emotion'].lower()
        if emotion in positive:
            high += 1
        else:
            low += 1
    return(high,low)

def leadership(loc1,loc2,utterances1,utterances2):
    L1 = loc1
    L2 = loc2
    for event1 in utterances1:
        if event1['event'] == 'speech':
            L1+= 1
    for event2 in utterances2:
        if event2['event'] == 'speech':
            L2 += 1
    if abs(L1 - L2) > 10:         
        return "Authoritative"    #This might have a negative impact on collaboration
    else:
        return "Democratic"

# Processes
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
            parsed_response = json.loads(response)
            user_id = parsed_response.get("user_id")
            print(f"Stored user_id: {user_id}")
            
            # Trigger scripts
            trigger_scripts()

            # Use the generated data
            await process_generated_data(websocket, device_id)
        
    except websockets.exceptions.ConnectionClosedError as e:
        print(f"WebSocket connection closed with error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        print("Closing the WebSocket connection")
        await websocket.close()

def trigger_scripts():
    # Function to run scripts and wait for them to complete
    base_dir = "D:\\HCI_Research\\GenderTool\\Tool\\recognition"
    def run_script(script_name):
        script_path = os.path.join(base_dir, script_name)
        os.system(f"python {script_path}")

    # Start the scripts in separate threads
    threads = []
    for script in ["keystroke.py", "face_detection.py", "utterances.py"]:
        thread = threading.Thread(target=run_script, args=(script,))
        thread.start()
        threads.append(thread)

    # Wait for all scripts to complete
    for thread in threads:
        thread.join()

async def process_generated_data(websocket, device_id):
    with open("keystroke_data.json", "r") as f:
        keystroke_data = json.load(f)
    with open("face_detection_data.json", "r") as f:
        face_detection_data = json.load(f)
    with open("utterance_data.json", "r") as f:
        utterances_data = json.load(f)
    rapport = rapport_score(utterances_data)
    processed_utterances = processed_utterance_data(utterances_data)
    data_to_send = {
        "LOC": keystroke_data['lines_of_code'],
        "rapport_score": rapport,
        "utterances_data": processed_utterances
    }
    #print(data_to_send)
    await websocket.send(json.dumps(data_to_send))
    print("Processed data sent to the server")

    response = await websocket.recv()
    print(f"Response from server after data processing")
    parsed_response = json.loads(response)
    #print(parsed_response)
    for user in parsed_response['users_data']:
        if user['device_id'] == device_id:
            user1_data = user
        else:
            user2_data = user
    
    # # Ensure we have both users' data
    if user1_data is None or user2_data is None:
        print("Error: Missing user data")
        return
    
    # Call the required functions
    loc1 = user1_data['data']['LOC']
    loc2 = user2_data['data']['LOC']
    utterances1 = user1_data['data']['utterances']
    utterances2 = user2_data['data']['utterances']
    emotions1 = face_detection_data
    
    role_user1= determine_user_role(loc1, loc2)
    user1_interruptions = interruptions(utterances1, utterances2)
    comm_style_user1 = communication_style(emotions1, utterances1)
    self_efficacy_user1 = self_efficacy(emotions1)
    leadership_style = leadership(loc1, loc2, utterances1, utterances2)
    
    # Store results in the corresponding user's interval data
    user1_data['intervals'].append({
        "timeframe": 1, 
        "role": role_user1,
        "communication_style": comm_style_user1,
        "self_efficacy": self_efficacy_user1,
        "interruptions": user1_interruptions,
        "leadership": leadership_style
    })
    updated_data = {
        "device_id": user1_data['device_id'],
        "users": [user1_data]
    }
    await websocket.send(json.dumps(updated_data))
    print("Updated interval data sent to the server")

def main():
    device_id = get_device_id()
    if device_id:
        print(f"Device ID: {device_id}")
    else:
        print("Failed to obtain device ID.")
        return

    session_id = "003"  # Will take session_id from user
    asyncio.get_event_loop().run_until_complete(connect_to_server(device_id, session_id))

if __name__ == "__main__":
    main()
