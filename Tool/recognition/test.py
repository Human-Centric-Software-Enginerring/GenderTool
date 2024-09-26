# import asyncio
# import websockets
# import json
# from pymongo import MongoClient
# from datetime import datetime
# from config import MONGO_URI
# import logging
# import os

# # Set absolute path for log file
# log_file_path = os.path.abspath('websocket_server.log')

# # Configure logging
# logging.basicConfig(
#     filename=log_file_path,  # Absolute log file path
#     level=logging.INFO,      # Log level
#     format='%(asctime)s - %(levelname)s - %(message)s'
# )

# # MongoDB Connection
# try:
#     client = MongoClient(MONGO_URI)
#     db = client["websocket_sessions"]
#     print("Server Started. Database Connection Successful")
#     logging.info("Database connection successful")
# except Exception as e:
#     logging.error(f"Failed to connect to MongoDB: {e}")
#     exit(1)

# connected_clients = set()


# async def handle_connection(websocket, path):
#     logging.info("Client connected")
    
#     try:
#         # Receive the device_id and session_id from client
#         message = await websocket.recv()
#         logging.info("Message received from client")
#         print("Message recieved from client")
        
#         data = json.loads(message)
#         device_id = data.get('device_id')
#         session_id = data.get('session_id')
#         logging.info(f"Device ID: {device_id}, Session ID: {session_id}")

        
#         # Check if session_id already exists in MongoDB
#         session = db.sessions.find_one({"session_id": session_id})
        
#         if session:
#             logging.info("Session found, updating existing session")
#             # Generate a new user_id for the new device/user
#             user_id = max([user['user_id'] for user in session['users']], default=-1) + 1

#             # Append device_id to the users list if it does not exist
#             if not any(user['device_id'] == device_id for user in session['users']):
#                 db.sessions.update_one(
#                     {"session_id": session_id},
#                     {"$push": {"users": {"device_id": device_id, "user_id": user_id, "intervals": []}}}
#                 )
#             response_message = "Session updated successfully"
#         else:
#             logging.info("Session not found, creating a new session")
#             # Create a new session entry with user_id starting at 1
#             user_id = 1
#             new_session = {
#                 "session_id": session_id,
#                 "session_start": datetime.now().isoformat(),
#                 "session_end": None,
#                 "users": [
#                     {"device_id": device_id, "user_id": user_id, "intervals": []}
#                 ]
#             }
#             db.sessions.insert_one(new_session)
#             response_message = "Session created successfully"

#         # Send response to the client
#         response = {
#             "status": "success", 
#             "message": response_message,
#             "user_id": user_id  # Include user_id in the response
#         }

#         await websocket.send(json.dumps(response))
#         logging.info("Response sent to client with user_id: %s", response.get("user_id", "N/A"))

#         # Wait for further data from the client
#         while True:
#             try:
#                 message = await websocket.recv()
#                 logging.info("Data message received from client")
#                 data = json.loads(message)

#                 # Extract the relevant data
#                 LOC = data.get('LOC')
#                 rapport_score = data.get('rapport_score')
#                 utterances_data = data.get('utterances_data')

#                 if LOC is None or rapport_score is None or utterances_data is None:
#                     logging.error("Error: Missing required fields in data message")
#                     continue

#                 # Update the user's data in MongoDB
#                 update_result = db.sessions.update_one(
#                     {"session_id": session_id, "users.device_id": device_id},
#                     {"$set": {
#                         "users.$.data": {
#                             "LOC": LOC,
#                             "rapport_score": rapport_score,
#                             "utterances": utterances_data
#                         }
#                     }}
#                 )
#                 logging.info("Update result: %s", update_result.raw_result)  # Log update result

#                 # Wait and check if user2_data is present
#                 start_time = asyncio.get_event_loop().time()
#                 timeout = 300  # 5 minute timeout

#                 while True:
#                     try:
#                         # Retrieve data for the session from MongoDB
#                         session = db.sessions.find_one({"session_id": session_id})
#                         if session:
#                             users_data = session.get("users", [])
#                             # Identify if there is any other user's data in the session
#                             user2_data = next((user for user in users_data if user.get("device_id") != device_id), None)

#                             if user2_data:
#                                 # User2 data is present, proceed to retrieve data for the users
#                                 response_data = [user for user in users_data]
#                                 response = {
#                                     "status": "success",
#                                     "message": "Data updated successfully",
#                                     "users_data": response_data
#                                 }
#                                 await websocket.send(json.dumps(response))
#                                 logging.info("Data updated in MongoDB and response sent to client")
#                                 break
#                         else:
#                             # Handle the case where the session is not found
#                             response = {
#                                 "status": "error",
#                                 "message": "Session not found"
#                             }
#                             await websocket.send(json.dumps(response))
#                             logging.error("Session not found")
#                             break

#                         # Check if timeout has been reached
#                         elapsed_time = asyncio.get_event_loop().time() - start_time
#                         if elapsed_time >= timeout:
#                             # Timeout reached, send an error message or handle accordingly
#                             response = {
#                                 "status": "error",
#                                 "message": "Timeout waiting for user2 data"
#                             }
#                             await websocket.send(json.dumps(response))
#                             logging.error("Timeout reached while waiting for user2 data")
#                             break

#                         # Wait for a short period before checking again
#                         await asyncio.sleep(5)  # Check every 5 seconds

#                     except Exception as e:
#                         logging.error("Error in inner while loop: %s", e)
#                         break

#             except Exception as e:
#                 logging.error("Error receiving or processing data: %s", e)
#                 break

#             # Receive and process interval data
#             try:
#                 message = await websocket.recv()
#                 logging.info("Interval data message received from client")
#                 data = json.loads(message)
#                 device_id = data.get('device_id')
#                 users_data = data.get('users', [])
                
#                 if not isinstance(users_data, list):
#                     logging.error("Error: Invalid format for users_data")
#                     continue
                
#                 for user_data in users_data:
#                     if user_data.get('device_id') == device_id:
#                         db.sessions.update_one(
#                             {"session_id": session_id, "users.device_id": device_id},
#                             {"$push": {
#                                 "users.$.intervals": user_data.get('intervals', [])[-1]  # Append the new interval data
#                             }}
#                         )
#                         break

#                 # Send a confirmation back to the client
#                 response = {
#                     "status": "success",
#                     "message": "Interval data updated successfully"
#                 }
#                 await websocket.send(json.dumps(response))
#                 logging.info("Interval data updated in MongoDB and confirmation sent to client")

#                  # Fetch the updated session data from MongoDB
#                 session = db.sessions.find_one({"session_id": session_id})
#                 if session:
#                     users = session.get("users", [])
#                     # Reorder users to have the current device first
#                     current_user = next((user for user in users if user["device_id"] == device_id), None)
#                     other_user = next((user for user in users if user["device_id"] != device_id), None)
                    
#                     if current_user and other_user:
#                         # Prepare interval data to send back
#                         interval_data = [
#                             {
#                                 "intervals": current_user["intervals"][-1:] if current_user["intervals"] else []
#                             },
#                             {
#                                 "intervals": other_user["intervals"][-1:] if other_user["intervals"] else []
#                             }
#                         ]

#                         # Send the interval data to the client
#                         response = {
#                             "status": "intervalData",
#                             "message": "Latest interval data fetched and sent to client",
#                             "interval_data": interval_data
#                         }
#                         await websocket.send(json.dumps(response))
#                         logging.info("Latest interval data sent to client")

#                 # Ensure the connection is closed after processing interval data
#                 logging.info("Closing connection with the client")
#                 await websocket.close()
#                 break

#             except Exception as e:
#                 logging.error("Error processing interval data: %s", e)
#                 break

#     except websockets.exceptions.ConnectionClosedError as e:
#         logging.error("Client connection closed with error: %s", e)
#     except Exception as e:
#         logging.error("Error in connection handler: %s", e)
#     finally:
#         if not websocket.closed:
#             logging.info("Closing connection with the client")
#             await websocket.close()

# def print_clients():
#     print("Connected Clients:", connected_clients)
#     logging.info(f"Current Connected Clients: {len(connected_clients)}")

# async def main():
#     print("Starting server...")  # Debugging print
#     logging.info("Starting server...")
#     server = await websockets.serve(handle_connection, "localhost", 8765, ping_timeout=3000)
#     logging.info("WebSocket server started on ws://localhost:8765")
#     await server.wait_closed()

# # Run the WebSocket server
# try:
#     asyncio.run(main())
# except Exception as e:
#     logging.error(f"Error running the server: {e}")
#     print(f"Error running the server: {e}")


utterances = [
    {
        "start_timestamp": 0.0,
        "end_timestamp": 0.5,
        "event": "Crunch"
    },
    {
        "start_timestamp": 0.1,
        "end_timestamp": 2.8,
        "event": "speech",
        "transcription": " replacement"
    },
    {
        "start_timestamp": 0.5,
        "end_timestamp": 1.0,
        "event": "Crunch"
    },
    {
        "start_timestamp": 1.0,
        "end_timestamp": 1.5,
        "event": "Crunch"
    },
    {
        "start_timestamp": 5.0,
        "end_timestamp": 5.5,
        "event": "Crunch"
    },
    {
        "start_timestamp": 5.5,
        "end_timestamp": 6.0,
        "event": "Crunch"
    },
    {
        "start_timestamp": 6.0,
        "end_timestamp": 6.5,
        "event": "Crunch"
    },
    {
        "start_timestamp": 6.5,
        "end_timestamp": 7.0,
        "event": "Crunch"
    },
    {
        "start_timestamp": 8.0,
        "end_timestamp": 8.5,
        "event": "Crunch"
    },
    {
        "start_timestamp": 8.5,
        "end_timestamp": 9.0,
        "event": "Crunch"
    },
    {
        "start_timestamp": 9.5,
        "end_timestamp": 10.0,
        "event": "Crunch"
    },
    {
        "start_timestamp": 10.0,
        "end_timestamp": 10.5,
        "event": "Crunch"
    },
    {
        "start_timestamp": 10.5,
        "end_timestamp": 12.5,
        "event": "speech",
        "transcription": " \u062a\u0633\u0631 \u0627\u0646\u06af\u0632 \u0645\u0626\u06cc\u062f\u0645 \u062f predict"
    },
    {
        "start_timestamp": 12.5,
        "end_timestamp": 13.0,
        "event": "Crunch"
    },
    {
        "start_timestamp": 12.82,
        "end_timestamp": 12.94,
        "event": "pause"
    },
    {
        "start_timestamp": 13.0,
        "end_timestamp": 13.5,
        "event": "Crunch"
    },
    {
        "start_timestamp": 13.5,
        "end_timestamp": 14.0,
        "event": "Crunch"
    },
    {
        "start_timestamp": 14.0,
        "end_timestamp": 14.5,
        "event": "Crunch"
    },
    {
        "start_timestamp": 14.5,
        "end_timestamp": 15.0,
        "event": "Crunch"
    },
    {
        "start_timestamp": 15.0,
        "end_timestamp": 15.5,
        "event": "Crunch"
    },
    {
        "start_timestamp": 15.25,
        "end_timestamp": 15.38,
        "event": "pause"
    },
    {
        "start_timestamp": 16.5,
        "end_timestamp": 17.0,
        "event": "Crunch"
    },
    {
        "start_timestamp": 17.0,
        "end_timestamp": 17.5,
        "event": "Crunch"
    },
    {
        "start_timestamp": 18.5,
        "end_timestamp": 19.0,
        "event": "Crunch"
    },
    {
        "start_timestamp": 19.0,
        "end_timestamp": 19.5,
        "event": "Crunch"
    },
    {
        "start_timestamp": 19.5,
        "end_timestamp": 20.0,
        "event": "Wail, moan"
    },
    {
        "start_timestamp": 20.0,
        "end_timestamp": 20.5,
        "event": "Crunch"
    },
    {
        "start_timestamp": 20.3,
        "end_timestamp": 24.5,
        "event": "speech",
        "transcription": " \u0648\u0627\u0632 \u0648 \u0631\u062e\u0631 \u03c4\u03bf\u03bd \u062f\u06c1 \u0644\u0627 Jet"
    },
    {
        "start_timestamp": 24.5,
        "end_timestamp": 25.0,
        "event": "Crunch"
    },
    {
        "start_timestamp": 26.0,
        "end_timestamp": 26.5,
        "event": "Crunch"
    },
    {
        "start_timestamp": 26.5,
        "end_timestamp": 27.0,
        "event": "Fowl"
    },
    {
        "start_timestamp": 27.5,
        "end_timestamp": 28.0,
        "event": "Crunch"
    },
    {
        "start_timestamp": 28.0,
        "end_timestamp": 28.5,
        "event": "Crunch"
    },
    {
        "start_timestamp": 28.5,
        "end_timestamp": 29.0,
        "event": "Crunch"
    },
    {
        "start_timestamp": 29.0,
        "end_timestamp": 29.5,
        "event": "Crunch"
    },
    {
        "start_timestamp": 30.0,
        "end_timestamp": 30.01,
        "event": "speech",
        "transcription": " \u0627\u064f\u0633\u06cc \u0627\u064f\u0633\u06cc \u0627\u064f\u0633\u06cc \u0627\u064f\u0633\u06cc \u0627\u064f\u0633\u06cc \u0627\u064f\u0633\u06cc \u0627\u064f\u0633\u06cc \u0627\u064f\u0633\u06cc \u0627\u064f\u0633\u06cc \u0627\u064f\u0633\u06cc \u0627\u064f\u0633\u06cc \u0627\u064f\u0633\u06cc \u0627\u064f\u0633\u06cc \u0627\u064f\u0633\u06cc \u0627\u064f\u0633\u06cc \u0627\u064f\u0633\u06cc \u0627\u064f\u0633\u06cc \u0627\u064f\u0633\u06cc \u0627\u064f\u0633\u06cc \u0627\u064f\u0633\u06cc \u0627\u064f\u0633\u06cc \u0627\u064f\u0633\u06cc \u0627\u064f\u0633\u06cc \u0627\u064f\u0633\u06cc \u0627\u064f\u0633\u06cc \u0627\u064f\u0633\u06cc \u0627\u064f\u0633\u06cc \u0627\u064f\u0633\u06cc \u0627\u064f\u0633\u06cc \u0627\u064f\u0633\u06cc \u0627\u064f\u0633\u06cc \u0627\u064f\u0633\u06cc \u0627\u064f\u0633\u06cc \u0627\u064f\u0633\u06cc \u0627\u064f\u0633\u06cc \u0627\u064f\u0633\u06cc \u0627\u064f\u0633\u06cc \u0627\u064f\u0633\u06cc \u0627\u064f\u0633\u06cc \u0627\u064f\u0633\u06cc \u0627\u064f\u0633\u06cc \u0627\u064f\u0633\u06cc \u0627\u064f\u0633\u06cc \u0627\u064f\u0633\u06cc \u0627\u064f\u0633\u06cc \u0627\u064f\u0633\u06cc \u0627\u064f\u0633\u06cc \u0627\u064f\u0633\u06cc \u0627\u064f\u0633\u06cc \u0627\u064f\u0633\u06cc \u0627\u064f\u0633\u06cc \u0627\u064f\u0633\u06cc \u0627\u064f\u0633\u06cc \u0627\u064f\u0633\u06cc \u0627\u064f\u0633\u06cc \u0627\u064f\u0633"
    },
    {
        "start_timestamp": 30.0,
        "end_timestamp": 30.5,
        "event": "Crunch"
    }
]

def rapport_score(utterances):
    import re
    score = 0
    keywords = [r"hm",r"um",r"ha",r"uh",r"oh"]
    for event in utterances:
        if event["event"].lower() not in ["speech","pause"]:
            print(event["event"])
            score += 1
        elif event["event"].lower() in ["speech"]:
            for keyword in keywords:
                if re.search(keyword, event["transcription"].lower()):
                    print(event["transcription"])
                    score += 1
    return score

def processed_data(utterances):
    processed_data = []
    for utterance in utterances:
        processed_utterance = {
            "start_timestamp": utterance["start_timestamp"],
            "end_timestamp": utterance["end_timestamp"],
            "event": utterance["event"]
        }
        processed_data.append(processed_utterance)
    return processed_data

#print(rapport_score(utterances))
#print(processed_data(utterances))
# import json
# with open("keystroke_data.json", "r") as f:
#         keystroke_data = json.load(f)
# print(keystroke_data['lines_of_code'])

print("inside test.py")

import shutil
import os

cache_dir = os.path.expanduser('~\\AppData\\Local\\Temp\\tfhub_modules')
if os.path.exists(cache_dir):
    shutil.rmtree(cache_dir)
    print("Cache cleared.")
else:
    print("Cache directory does not exist.")
