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

# async def handle_connection(websocket, path):
#     print("Client connected")
    
#     try:
#         # Receive the device_id and session_id from client
#         message = await websocket.recv()
#         print("Message received from client")
        
#         data = json.loads(message)
#         device_id = data['device_id']
#         session_id = data['session_id']
#         print(f"Device ID: {device_id}, Session ID: {session_id}")
        
#         # Check if session_id already exists in MongoDB
#         session = db.sessions.find_one({"session_id": session_id})
        
#         if session:
#             print("Session found, updating existing session")
#             # Generate a new user_id for the new device/user
#             user_id = len(session['users'])

#             # Append device_id to the users list if it does not exist
#             if not any(user['device_id'] == device_id for user in session['users']):
#                 db.sessions.update_one(
#                     {"session_id": session_id},
#                     {"$push": {"users": {"device_id": device_id, "user_id": user_id, "intervals": []}}}
#                 )
#             response_message = "Session updated successfully"
#         else:
#             print("Session not found, creating a new session")
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
#         print("Response sent to client with user_id:", response.get("user_id", "N/A"))

#         # Wait for further data from the client
#         while True:
#             message = await websocket.recv()
#             print("Data message received from client")
#             data = json.loads(message)

#             # Extract the relevant data
#             LOC = data.get('LOC')
#             rapport_score = data.get('rapport_score')
#             utterances_data = data.get('utterances_data')

#             # Update the user's data in MongoDB
#             db.sessions.update_one(
#                 {"session_id": session_id, "users.device_id": device_id},
#                 {"$set": {
#                     "users.$.data": {
#                         "LOC": LOC,
#                         "rapport_score": rapport_score,
#                         "utterances": utterances_data
#                     }
#                 }}
#             )

#             # Retrieve data for the user(s) from the database
#             session = db.sessions.find_one({"session_id": session_id})
#             users_data = session.get("users", [])

#             # Filter out the relevant data
#             response_data = []
#             for user in users_data[:2]:
#                 user_data = user.get("data")
#                 if user_data:
#                     response_data.append(user_data)

#             # Send success message back to client
#             response = {
#                 "status": "success",
#                 "message": "Data updated successfully",
#                 "users_data": response_data
#             }
#             await websocket.send(json.dumps(response))
#             print("Data updated in MongoDB and response sent to client")
#             message = await websocket.recv()
#             print("Interval data message received from client")
#             data = json.loads(message)
#             # Extract the relevant data including device_id
#             device_id = data.get('device_id')
#             users_data = data.get('users')
#             # Update the user's intervals in MongoDB based on session_id and device_id
#             for user_data in users_data:
#                 db.sessions.update_one(
#                     {"session_id": session_id, "users.device_id": device_id},
#                     {"$push": {
#                         "users.$.intervals": user_data['intervals'][-1]  # Append the new interval data
#                     }}
#                 )
#             # Send a confirmation back to the client
#             response = {
#                 "status": "success",
#                 "message": "Interval data updated successfully"
#             }
#             await websocket.send(json.dumps(response))
#             print("Interval data updated in MongoDB and confirmation sent to client")

#     except websockets.exceptions.ConnectionClosedError as e:
#         print(f"Client connection closed with error: {e}")
#     except Exception as e:
#         print(f"Error in connection handler: {e}")
#     finally:
#         print("Closing connection with the client")
#         await websocket.close()
async def handle_connection(websocket, path):
    print("Client connected")
    
    try:
        # Receive the device_id and session_id from client
        message = await websocket.recv()
        print("Message received from client")
        
        data = json.loads(message)
        device_id = data.get('device_id')
        session_id = data.get('session_id')
        print(f"Device ID: {device_id}, Session ID: {session_id}")
        
        # Check if session_id already exists in MongoDB
        session = db.sessions.find_one({"session_id": session_id})
        
        if session:
            print("Session found, updating existing session")
            # Generate a new user_id for the new device/user
            user_id = max([user['user_id'] for user in session['users']], default=-1) + 1

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

        await websocket.send(json.dumps(response))
        print("Response sent to client with user_id:", response.get("user_id", "N/A"))

        # Wait for further data from the client
        while True:
            message = await websocket.recv()
            print("Data message received from client")
            data = json.loads(message)

            # Extract the relevant data
            LOC = data.get('LOC')
            rapport_score = data.get('rapport_score')
            utterances_data = data.get('utterances_data')

            # Update the user's data in MongoDB
            db.sessions.update_one(
                {"session_id": session_id, "users.device_id": device_id},
                {"$set": {
                    "users.$.data": {
                        "LOC": LOC,
                        "rapport_score": rapport_score,
                        "utterances": utterances_data
                    }
                }}
            )

            # Retrieve data for the user(s) from the database
            session = db.sessions.find_one({"session_id": session_id})
            users_data = session.get("users", [])
            #print(users_data)
            # Filter out the relevant data
            response_data = []
            for user in users_data:
                response_data.append(user)
            print(response_data)
            # Send success message back to client
            response = {
                "status": "success",
                "message": "Data updated successfully",
                "users_data": response_data
            }
            await websocket.send(json.dumps(response))
            print("Data updated in MongoDB and response sent to client")
            
            # Receive and process interval data
            message = await websocket.recv()
            print("Interval data message received from client")
            data = json.loads(message)
            device_id = data.get('device_id')
            users_data = data.get('users', [])
            
            for user_data in users_data:
                if user_data.get('device_id') == device_id:
                    db.sessions.update_one(
                        {"session_id": session_id, "users.device_id": device_id},
                        {"$push": {
                            "users.$.intervals": user_data['intervals'][-1]  # Append the new interval data
                        }}
                    )
                    break

            # Send a confirmation back to the client
            response = {
                "status": "success",
                "message": "Interval data updated successfully"
            }
            await websocket.send(json.dumps(response))
            print("Interval data updated in MongoDB and confirmation sent to client")

    except websockets.exceptions.ConnectionClosedError as e:
        print(f"Client connection closed with error: {e}")
    except Exception as e:
        print(f"Error in connection handler: {e}")
    finally:
        print("Closing connection with the client")
        await websocket.close()


start_server = websockets.serve(handle_connection, "localhost", 8765, ping_timeout=3000)

print("Starting server...")
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
