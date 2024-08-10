import asyncio
import websockets
import json
from pymongo import MongoClient
from datetime import datetime

# MongoDB Connection
try:
    client = MongoClient("mongodb+srv://manali0210:TrBaO7bfGRxSFzyy@cluster0.pjfepaj.mongodb.net/")
    db = client["websocket_sessions"]
    print("Database connection successful")
except Exception as e:
    print(f"Failed to connect to MongoDB: {e}")
    exit(1)

async def handle_connection(websocket, path):
    print("Client connected")
    
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
        # Append device_id to the users list if it does not exist
        if not any(user['user_id'] == device_id for user in session['users']):
            db.sessions.update_one(
                {"session_id": session_id},
                {"$push": {"users": {"user_id": device_id, "intervals": []}}}
            )
    else:
        print("Session not found, creating a new session")
        # Initialize a new session document
        new_session = {
            "session_id": session_id,
            "session_start": datetime.now().isoformat(),
            "session_end": None,
            "users": [
                {"user_id": device_id, "intervals": []}
            ]
        }
        db.sessions.insert_one(new_session)
    
    # Send response to the client
    response = {"status": "success", "message": "Session updated successfully"}
    await websocket.send(json.dumps(response))
    print("Response sent to client")

start_server = websockets.serve(handle_connection, "localhost", 8765)

print("Starting server...")
asyncio.get_event_loop().run_until_complete(start_server)
print("Server started successfully")
asyncio.get_event_loop().run_forever()
