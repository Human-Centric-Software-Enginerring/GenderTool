import asyncio
import websockets
import json
from pymongo import MongoClient
from datetime import datetime
from config import MONGO_URI

# MongoDB Connection
try:
    client = MongoClient(MONGO_URI)
    db = client["websocket_sessions"]
    print("Database connection successful")
except Exception as e:
    print(f"Failed to connect to MongoDB: {e}")
    exit(1)

async def handle_connection(websocket, path):
    print("Client connected")
    
    try:
        # Receive the device_id and session_id from client
        message = await websocket.recv()
        print("Message received from client")
        
        data = json.loads(message)
        device_id = data['device_id']
        session_id = data['session_id']
        print(f"Device ID: {device_id}, Session ID: {session_id}")
        
        # Check if session_id already exists in MongoDB
        session = db.sessions.find_one({"session_id": session_id})
        
        if session:
            print("Session found, updating existing session")
            # Generate a new user_id for the new device/user
            user_id = len(session['users']) + 1

            # Append device_id to the users list if it does not exist
            if not any(user['device_id'] == device_id for user in session['users']):
                db.sessions.update_one(
                    {"session_id": session_id},
                    {"$push": {"users": {"device_id": device_id, "user_id": user_id, "intervals": []}}}
                )
            response_message = "Session updated successfully"
        else:
            print("Session not found, creating a new session")
            # Create a new session entry with user_id starting at 1
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

        # Send response to the client
        response = {
            "status": "success", 
            "message": response_message,
            "user_id": user_id  # Include user_id in the response
        }

    except Exception as e:
        print(f"Error in connection handler: {e}")
        response = {
            "status": "error", 
            "message": str(e)
        }
    
    # Send the response back to the client
    await websocket.send(json.dumps(response))
    print("Response sent to client with user_id:", response.get("user_id", "N/A"))

start_server = websockets.serve(handle_connection, "localhost", 8765)

print("Starting server...")
asyncio.get_event_loop().run_until_complete(start_server)
print("Server started successfully")
asyncio.get_event_loop().run_forever()
