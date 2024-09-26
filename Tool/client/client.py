import platform
import subprocess
import asyncio
import websockets
import json
import os
import threading
import argparse
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from rapport_score import rapport_scorer

timeframe = 0 
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

# Helper functions
def rapport_score(utterances):
    score = rapport_scorer(utterances)
    return score

def processed_utterance_data(utterances):
    processed_data = []
    for utterance in utterances:
        processed_utterance = {
            "start_timestamp": utterance["start_timestamp"],
            "end_timestamp": utterance["end_timestamp"],
            "event": utterance["event"],
            "words":utterance["words"]
        }
        processed_data.append(processed_utterance)
    return processed_data

#processing interval data
def determine_user_role(loc1, loc2):
    X1 = loc1 / (loc1 + loc2)
    X2 = loc2 / (loc1 + loc2)
    if X1 > X2:
        return "Driver"
    else:
        return "Navigator"

#need speech_data from database
def interruptions(utterances1, utterances2):
    user1_interruptions = 0
    for event2 in utterances2:
        start2 = event2['start_timestamp']
        end2 = event2['end_timestamp']
        for event1 in utterances1:
            start1 = event1['start_timestamp']
            if event1['event'] == 'speech' and event2['event'] == 'speech' and start2 <= start1 <= end2:
                #print(event1)
                user1_interruptions += 1
    return user1_interruptions

#need to update implementation logic    
def communication_style(emotions,utterances):
    verbal_time = 0
    for event in utterances:
        if event["event"].lower() == "speech":
            verbal_time += event['end_timestamp']-event['start_timestamp']
    #total interval time is 300 seconds, if speaks more than 50% time,communication style is verbal.
    if verbal_time > 15:
        return "Verbal"
    else:
        return "Non Verbal"

def self_efficacy(emotions):
    #return proportions (high/high+low) line graph between 0-1
    positive = ["happy", "neutral", "surprise"]
    # negative = ["sad", "fear", "angry"]
    high, low = 0, 0
    for event in emotions:
        emotion = event['emotion'].lower()
        #print(emotion)
        if emotion in positive:
            high += 1
        else:
            low += 1
    return (high/(high+low)), (low/(low+high))

def leadership(loc1,loc2,utterances1,utterances2):
    words1 = 0
    words2 =0
    for event1 in utterances1:
        if event1['event'] == "speech":
            words1 += event1['words']
    for event2 in utterances2:
         if event2['event'] == "speech":
            words2 += event2['words']
    L1 = (loc1/(loc1+loc2)) + (words1/(words1+words2))
    L2 = (loc2/(loc1+loc2)) + ((words2/words1+words2))
    if (L1-L2) > 1:
        return "Authoritative"
    else:
        return "Democratic"

# Processes
async def connect_to_server(device_id, session_id):
    # uri = "ws://localhost:8000"
    uri = "ws://localhost:8000/ws"
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
    # Function to run scripts
    base_dir = "D:\\HCI_Research\\GenderTool\\Tool\\recognition"
    def run_script(script_name):
        script_path = os.path.join(base_dir, script_name)
        os.system(f"python {script_path}")
    
    scripts = ["keystroke.py", "face_detection.py", "utterances.py"]

    # Use ThreadPoolExecutor to run scripts concurrently
    with ThreadPoolExecutor(max_workers=len(scripts)) as executor:
        futures = {executor.submit(run_script, script): script for script in scripts}
        
        for future in as_completed(futures):
            script_name = futures[future]
            try:
                future.result()  # This will raise an exception if the script failed
                print(f"{script_name} completed successfully.")
            except Exception as e:
                print(f"{script_name} failed with error: {e}")

async def process_generated_data(websocket, device_id):
    global timeframe
    print("timeframe = ", timeframe)
    keystroke_data = requests.get("http://127.0.0.1:8000/get-keystrokes").json()
    face_detection_data = requests.get("http://127.0.0.1:8000/get-emotions").json()
    utterances_data = requests.get("http://127.0.0.1:8000/get-utterances").json()
    print("Keystroke data: " ,keystroke_data)
    print("Emotion data: " ,face_detection_data)
    print("Utterance data: ",utterances_data)

    rapport = rapport_score(utterances_data)
    processed_utterances = processed_utterance_data(utterances_data)
    data_to_send = {
        "LOC": keystroke_data['lines_of_code'],
        "rapport_score": rapport,
        "utterances_data": processed_utterances
    }
    print("data_to_send: ",data_to_send["LOC"],data_to_send["rapport_score"])
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
    timeframe += 1
    
    role_user1= determine_user_role(loc1, loc2)
    user1_interruptions = interruptions(utterances1, utterances2)
    comm_style_user1 = communication_style(emotions1, utterances1)
    self_efficacy_user1 = self_efficacy(emotions1)
    leadership_style = leadership(loc1, loc2, utterances1, utterances2)
    
    # Store results in the corresponding user's interval data
    user1_data['intervals'].append({
        "timeframe": timeframe, 
        "loc": loc1,
        "rapport_score" : rapport,
        "role": role_user1,
        "communication_style": comm_style_user1,
        "self_efficacy": self_efficacy_user1,
        "interruptions": user1_interruptions,
        "leadership": leadership_style
    })
    updated_data = {
        "device_id": user1_data['device_id'],
        "interval_data": [user1_data]
    }
    await websocket.send(json.dumps(updated_data))
    print("Updated interval data sent to the server")
    await websocket.recv()
    print("ping received from websocket")
    interval_data = await websocket.recv()
    intData = json.loads(interval_data)
    print("Interval data")
    print(intData)

def main():
    parser = argparse.ArgumentParser(description='Process session ID.')
    parser.add_argument('session_id', type=str, help='The session ID to use')
    args = parser.parse_args() 
    device_id = get_device_id()
    if device_id:
        print(f"Device ID: {device_id}")
    else:
        print("Failed to obtain device ID.")
        return

    session_id = args.session_id
    asyncio.get_event_loop().run_until_complete(connect_to_server(device_id, session_id))

if __name__ == "__main__":
    main()
