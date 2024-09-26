# import asyncio
# import websockets
# import json
# from pymongo import MongoClient
# from datetime import datetime
# from config import MONGO_URI
# import logging
# import os
# import uuid

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

# # Dictionary to store WebSocket connections
# connected_clients = {}
# client_sessions = {}

# async def handle_connection(websocket, path):
#     logging.info("Client connected")
#     connection_id = str(uuid.uuid4())
#     connected_clients[connection_id] = websocket
#     print(connected_clients)

#     try:
#         # First message to identify client and store connection
#         message = await websocket.recv()
#         logging.info("Message received from client")
#         data = json.loads(message)

#         if 'device_id' in data and 'session_id' in data:
#             device_id = data['device_id']
#             session_id = data['session_id']
#             client_sessions[connection_id] = (device_id, session_id)
#             logging.info(f"Client identified with connection_id: {connection_id}, device_id: {device_id}, session_id: {session_id}")
            
#             # Check if session_id already exists in MongoDB
#             session = db.sessions.find_one({"session_id": session_id})
            
#             if session:
#                 logging.info("Session found, updating existing session")
#                 user_id = max([user['user_id'] for user in session['users']], default=-1) + 1
#                 if not any(user['device_id'] == device_id for user in session['users']):
#                     db.sessions.update_one(
#                         {"session_id": session_id},
#                         {"$push": {"users": {"device_id": device_id, "user_id": user_id, "intervals": []}}}
#                     )
#                 response_message = "Session updated successfully"
#             else:
#                 logging.info("Session not found, creating a new session")
#                 user_id = 1
#                 new_session = {
#                     "session_id": session_id,
#                     "session_start": datetime.now().isoformat(),
#                     "session_end": None,
#                     "users": [
#                         {"device_id": device_id, "user_id": user_id, "intervals": []}
#                     ]
#                 }
#                 db.sessions.insert_one(new_session)
#                 response_message = "Session created successfully"

#             response = {
#                 "status": "success", 
#                 "message": response_message,
#                 "user_id": user_id
#             }
#             await websocket.send(json.dumps(response))
#             logging.info("Response sent to client with user_id: %s", response.get("user_id", "N/A"))

#         elif 'message' in data and data['message'] == "Hello Server":
#             logging.info("Received Hello Server message from extension")
#             # Mark this connection as extension
#             connected_clients[connection_id] = {"type": "extension", "websocket": websocket}
#             response = {
#                 "status": "success",
#                 "message": "Hello from server"
#             }
#             await websocket.send(json.dumps(response))
#             logging.info("Response sent to extension")

#         else:
#             logging.error("Unexpected message format")
#             response = {
#                 "status": "error",
#                 "message": "Unexpected message format"
#             }
#             await websocket.send(json.dumps(response))

#         while True:
#             message = await websocket.recv()
#             logging.info("Data message received from client")
#             data = json.loads(message)

#             if 'LOC' in data and 'rapport_score' in data and 'utterances_data' in data:
#                 LOC = data['LOC']
#                 rapport_score = data['rapport_score']
#                 utterances_data = data['utterances_data']

#                 device_id, session_id = client_sessions.get(connection_id, (None, None))

#                 if not device_id or not session_id:
#                     logging.error("Missing device_id or session_id for client")
#                     break

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
#                 logging.info("Update result: %s", update_result.raw_result)

#                 start_time = asyncio.get_event_loop().time()
#                 timeout = 300  # 5 minute timeout

#                 while True:
#                     try:
#                         session = db.sessions.find_one({"session_id": session_id})
#                         if session:
#                             users_data = session.get("users", [])
#                             user2_data = next((user for user in users_data if user.get("device_id") != device_id), None)

#                             if user2_data:
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
#                             response = {
#                                 "status": "error",
#                                 "message": "Session not found"
#                             }
#                             await websocket.send(json.dumps(response))
#                             logging.error("Session not found")
#                             break

#                         elapsed_time = asyncio.get_event_loop().time() - start_time
#                         if elapsed_time >= timeout:
#                             response = {
#                                 "status": "error",
#                                 "message": "Timeout waiting for user2 data"
#                             }
#                             await websocket.send(json.dumps(response))
#                             logging.error("Timeout reached while waiting for user2 data")
#                             break

#                         await asyncio.sleep(5)  # Check every 5 seconds

#                     except Exception as e:
#                         logging.error("Error in inner while loop: %s", e)
#                         break

#             elif 'interval_data' in data:
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
#                                 "users.$.intervals": user_data.get('intervals', [])[-1]
#                             }}
#                         )
#                         break

#                 response = {
#                     "status": "success",
#                     "message": "Interval data updated successfully"
#                 }
#                 await websocket.send(json.dumps(response))
#                 logging.info("Interval data updated in MongoDB and confirmation sent to client")

#                 session = db.sessions.find_one({"session_id": session_id})
#                 if session:
#                     users = session.get("users", [])
#                     current_user = next((user for user in users if user["device_id"] == device_id), None)
#                     other_user = next((user for user in users if user["device_id"] != device_id), None)
                    
#                     if current_user and other_user:
#                         interval_data = [
#                             {
#                                 "intervals": current_user["intervals"][-1:] if current_user["intervals"] else []
#                             },
#                             {
#                                 "intervals": other_user["intervals"][-1:] if other_user["intervals"] else []
#                             }
#                         ]

#                         # Send interval data to extension
#                         for conn_id, client in connected_clients.items():
#                             if client.get("type") == "extension":
#                                 ws = client["websocket"]
#                                 response = {
#                                     "status": "intervalData",
#                                     "message": "Latest interval data fetched and sent to extension",
#                                     "interval_data": interval_data
#                                 }
#                                 await ws.send(json.dumps(response))
#                                 logging.info("Latest interval data sent to extension")

#                 logging.info("Closing connection with the client")
#                 await websocket.close()
#                 break

#             else:
#                 logging.error("Unexpected message format")
#                 break

#     except websockets.exceptions.ConnectionClosedError as e:
#         logging.error("Client connection closed with error: %s", e)
#     except Exception as e:
#         logging.error("Error in connection handler: %s", e)
#     finally:
#         if connection_id in connected_clients:
#             del connected_clients[connection_id]
#         if not websocket.closed:
#             logging.info("Closing connection with the client")
#             await websocket.close()

# async def main():
#     print("Starting server...")  # Debugging print
#     logging.info("Starting server...")
#     server = await websockets.serve(handle_connection, "localhost", 8765, ping_timeout=3000)
#     logging.info("WebSocket server started")
#     await server.wait_closed()

# asyncio.run(main())


#merging FASTAPI and ws_server.py

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import List, Dict, Any
import uvicorn
import asyncio
import json
from pymongo import MongoClient
from datetime import datetime
from config import MONGO_URI  # Ensure you have a config.py with MONGO_URI defined
import logging
import os
import uuid

# Initialize FastAPI app
app = FastAPI()

# Configure logging
log_file_path = os.path.abspath('server.log')
logging.basicConfig(
    filename=log_file_path,  # Absolute log file path
    level=logging.INFO,      # Log level
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# MongoDB Connection
try:
    client = MongoClient(MONGO_URI)
    db = client["websocket_sessions"]
    print("Server Started. Database Connection Successful")
    logging.info("Database connection successful")
except Exception as e:
    logging.error(f"Failed to connect to MongoDB: {e}")
    exit(1)

# Pydantic Models for HTTP Endpoints
class KeystrokeData(BaseModel):
    lines_of_code: int

class UtteranceData(BaseModel):
    start_timestamp: float
    end_timestamp: float
    event: str
    transcription: str = None
    words: float = None

class EmotionData(BaseModel):
    emotion: str
    start_timestamp: float
    end_timestamp: float

# Initialize data storage for HTTP endpoints
keystroke_data = {}
utterance_data: List[UtteranceData] = []
emotion_data: List[EmotionData] = []

@app.post("/update-keystrokes")
def update_keystrokes(data: KeystrokeData):
    keystroke_data['lines_of_code'] = data.lines_of_code
    return {"message": "Keystroke data updated"}

@app.post("/update-utterances")
def update_utterances(data: List[UtteranceData]):
    global utterance_data
    utterance_data = data
    return {"message": "Utterance data updated"}

@app.post("/update-emotions")
def update_emotions(data: List[EmotionData]):
    global emotion_data
    emotion_data = data
    return {"message": "Emotion data updated"}

@app.get("/get-keystrokes")
def get_keystrokes():
    return keystroke_data

@app.get("/get-utterances")
def get_utterances():
    return utterance_data

@app.get("/get-emotions")
def get_emotions():
    return emotion_data

# WebSocket Connection Storage
connected_clients: Dict[str, WebSocket] = {}
client_sessions: Dict[str, Any] = {}

# WebSocket Endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connection_id = str(uuid.uuid4())
    connected_clients[connection_id] = websocket
    logging.info(f"Client connected: {connection_id}")
    print(connected_clients)

    try:
        # First message to identify client and store connection
        message = await websocket.receive_text()
        logging.info("Message received from client")
        data = json.loads(message)

        if 'device_id' in data and 'session_id' in data:
            device_id = data['device_id']
            session_id = data['session_id']
            client_sessions[connection_id] = (device_id, session_id)
            logging.info(f"Client identified with connection_id: {connection_id}, device_id: {device_id}, session_id: {session_id}")

            # Check if session_id already exists in MongoDB
            session = db.sessions.find_one({"session_id": session_id})

            if session:
                logging.info("Session found, updating existing session")
                user_id = max([user['user_id'] for user in session['users']], default=-1) + 1
                if not any(user['device_id'] == device_id for user in session['users']):
                    db.sessions.update_one(
                        {"session_id": session_id},
                        {"$push": {"users": {"device_id": device_id, "user_id": user_id, "intervals": []}}}
                    )
                response_message = "Session updated successfully"
            else:
                logging.info("Session not found, creating a new session")
                user_id = 1
                new_session = {
                    "session_id": session_id,
                    "session_start": datetime.now().isoformat(),
                    "session_end": None,
                    "users": [
                        {"device_id": device_id, "user_id": user_id, "intervals": []}
                    ]
                }
                db.sessions.insert_one(new_session)
                response_message = "Session created successfully"

            response = {
                "status": "success",
                "message": response_message,
                "user_id": user_id
            }
            await websocket.send_text(json.dumps(response))
            logging.info(f"Response sent to client with user_id: {response.get('user_id', 'N/A')}")

        elif 'message' in data and data['message'] == "Hello Server":
            logging.info("Received Hello Server message from extension")
            # Mark this connection as extension
            connected_clients[connection_id] = {"type": "extension", "websocket": websocket}
            response = {
                "status": "success",
                "message": "Hello from server"
            }
            await websocket.send_text(json.dumps(response))
            logging.info("Response sent to extension")

        else:
            logging.error("Unexpected message format")
            response = {
                "status": "error",
                "message": "Unexpected message format"
            }
            await websocket.send_text(json.dumps(response))

        while True:
            message = await websocket.receive_text()
            logging.info("Data message received from client")
            data = json.loads(message)

            if 'LOC' in data and 'rapport_score' in data and 'utterances_data' in data:
                LOC = data['LOC']
                rapport_score = data['rapport_score']
                utterances_data = data['utterances_data']

                device_id, session_id = client_sessions.get(connection_id, (None, None))

                if not device_id or not session_id:
                    logging.error("Missing device_id or session_id for client")
                    break

                update_result = db.sessions.update_one(
                    {"session_id": session_id, "users.device_id": device_id},
                    {"$set": {
                        "users.$.data": {
                            "LOC": LOC,
                            "rapport_score": rapport_score,
                            "utterances": utterances_data
                        }
                    }}
                )
                logging.info(f"Update result: {update_result.raw_result}")

                start_time = asyncio.get_event_loop().time()
                timeout = 60  # 5 minute timeout

                while True:
                    try:
                        session = db.sessions.find_one({"session_id": session_id})
                        if session:
                            users_data = session.get("users", [])
                            user2_data = next((user for user in users_data if user.get("device_id") != device_id), None)

                            if user2_data:
                                response_data = [user for user in users_data]
                                response = {
                                    "status": "success",
                                    "message": "Data updated successfully",
                                    "users_data": response_data
                                }
                                await websocket.send_text(json.dumps(response))
                                logging.info("Data updated in MongoDB and response sent to client")
                                break
                        else:
                            response = {
                                "status": "error",
                                "message": "Session not found"
                            }
                            await websocket.send_text(json.dumps(response))
                            logging.error("Session not found")
                            break

                        elapsed_time = asyncio.get_event_loop().time() - start_time
                        if elapsed_time >= timeout:
                            response = {
                                "status": "error",
                                "message": "Timeout waiting for user2 data"
                            }
                            await websocket.send_text(json.dumps(response))
                            logging.error("Timeout reached while waiting for user2 data")
                            break

                        await asyncio.sleep(5)  # Check every 5 seconds

                    except Exception as e:
                        logging.error(f"Error in inner while loop: {e}")
                        break

            elif 'interval_data' in data:
                device_id = data.get('device_id')
                users_data = data.get('interval_data', [])

                if not isinstance(users_data, list):
                    logging.error("Error: Invalid format for users_data")
                    continue

                for user_data in users_data:
                    if user_data.get('device_id') == device_id:
                        db.sessions.update_one(
                            {"session_id": session_id, "users.device_id": device_id},
                            {"$push": {
                                "users.$.intervals": user_data.get('intervals', [])[-1]
                            }}
                        )
                        break

                response = {
                    "status": "success",
                    "message": "Interval data updated successfully"
                }
                await websocket.send_text(json.dumps(response))
                logging.info("Interval data updated in MongoDB and confirmation sent to client")

                session = db.sessions.find_one({"session_id": session_id})
                if session:
                    users = session.get("users", [])
                    current_user = next((user for user in users if user["device_id"] == device_id), None)
                    other_user = next((user for user in users if user["device_id"] != device_id), None)

                    if current_user and other_user:
                        interval_data = [
                            {
                                "intervals": current_user["intervals"][-1:] if current_user["intervals"] else []
                            },
                            {
                                "intervals": other_user["intervals"][-1:] if other_user["intervals"] else []
                            }
                        ]

                        # Send interval data to extension
                        for conn_id, client in connected_clients.items():
                            if isinstance(client, dict) and client.get("type") == "extension":
                                ws = client["websocket"]
                                response = {
                                    "status": "intervalData",
                                    "message": "Latest interval data fetched and sent to extension",
                                    "interval_data": interval_data
                                }
                                await ws.send_text(json.dumps(response))
                                logging.info("Latest interval data sent to extension")

                logging.info("Closing connection with the client")
                await websocket.close()
                break

            else:
                logging.error("Unexpected message format")
                break

    except WebSocketDisconnect:
        logging.error("Client disconnected")
    except Exception as e:
        logging.error(f"Error in connection handler: {e}")
    finally:
        if connection_id in connected_clients:
            del connected_clients[connection_id]
        # Always close the websocket if it is still open
        try:
            await websocket.close()
            logging.info("Connection closed with the client")
        except Exception as e:
            logging.error(f"Error closing websocket: {e}")

# Run the FastAPI app with WebSocket support
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000,ws_ping_timeout=60000)
