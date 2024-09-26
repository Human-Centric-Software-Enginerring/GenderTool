import asyncio
import websockets
import json

# Define the interval data grouped by timeframe
grouped_interval_data = [
    {
        'status': 'intervalData',
        'message': 'Interval data for timeframe 1 fetched and sent to client',
        'interval_data': [
            {
                'timeframe': 1,
                'role': 'Navigator',
                'communication_style': 'Non-Verbal',
                'self_efficacy': [4, 3],
                'interruptions': 4,
                'leadership': 'Authoritative',
                'loc' : 1,
                'rapport_score': 0.7
            },
            {
                'timeframe': 1,
                'role': 'Driver',
                'loc' : 20,
                'communication_style': 'Non-Verbal',
                'self_efficacy': [1, 0],
                'interruptions': 5,
                'rapport_score': 0.2,
                'leadership': 'Authoritative'
            }
        ]
    },
    {
        'status': 'intervalData',
        'message': 'Interval data for timeframe 2 fetched and sent to client',
        'interval_data': [
            {
                'timeframe': 2,
                'role': 'Navigator',
                'loc' : 3,
                'communication_style': 'Verbal',
                'self_efficacy': [4, 3],
                'interruptions': 10,
                'rapport_score': 0.9,
                'leadership': 'Authoritative'
            },
            {
                'timeframe': 2,
                'role': 'Driver',
                'loc' : 20,
                'communication_style': 'Verbal',
                'self_efficacy': [1, 0],
                'interruptions': 9,
                'rapport_score': 0.3,
                'leadership': 'Democratic'
            }
        ]
    }
]

intervals1= [ {
                'timeframe': 1,
                'LOC' : 10,
                'role': 'Navigator',
                'communication_style': 'Non-Verbal',
                'self_efficacy': [4, 3],
                'interruptions': 4,
                'leadership': 'Authoritative',
                'rapport_score': 0.7
            },
            {
                'timeframe': 2,
                'LOC' : 20,
                'role': 'Driver',
                'communication_style': 'Non-Verbal',
                'self_efficacy': [1, 0],
                'interruptions': 5,
                'leadership': 'Authoritative',
                'rapport_score': 0.1
            },{
                'timeframe': 3,
                'LOC' : 10,
                'role': 'Navigator',
                'communication_style': 'Verbal',
                'self_efficacy': [4, 3],
                'interruptions': 10,
                'leadership': 'Authoritative',
                'rapport_score': 0.3
            },
            {
                'timeframe': 4,
                'LOC':12,
                'role': 'Driver',
                'communication_style': 'Verbal',
                'self_efficacy': [1, 0],
                'interruptions': 9,
                'leadership': 'Democratic',
                'rapport_score': 0.58
            }]

intervals2= [ {
                'timeframe': 1,
                'LOC' : 10,
                'role': 'Navigator',
                'communication_style': 'Non-Verbal',
                'self_efficacy': [4, 3],
                'interruptions': 4,
                'leadership': 'Authoritative',
                'rapport_score': 0
            },
            {
                'timeframe': 2,
                'LOC' : 20,
                'role': 'Driver',
                'communication_style': 'Non-Verbal',
                'self_efficacy': [1, 0],
                'interruptions': 5,
                'leadership': 'Authoritative',
                'rapport_score': 0.34
            },{
                'timeframe': 3,
                'LOC' : 10,
                'role': 'Navigator',
                'communication_style': 'Verbal',
                'self_efficacy': [4, 3],
                'interruptions': 10,
                'leadership': 'Authoritative',
                'rapport_score': 0.2
            },
            {
                'timeframe': 4,
                'LOC':12,
                'role': 'Driver',
                'communication_style': 'Verbal',
                'self_efficacy': [1, 0],
                'interruptions': 9,
                'leadership': 'Democratic',
                'rapport_score': 0.9
            }]

def final_user_role(intervals):
    driver = 0
    navigator=0 
    for interval in intervals:
        if interval['role'] == 'Navigator':
            navigator += 1
        else:
            driver += 1
    return 'Driver' if driver >= navigator else 'Navigator'

def final_interruptions(intervals):
    count =0 
    for interval in intervals:
        count += interval['interruptions']
    return count

def final_lines_of_code(intervals):
    count =0 
    for interval in intervals:
        count += interval['LOC']
    return count

def final_communication_style(intervals):
    verbal =0 
    non_verbal=0
    for interval in intervals:
        if interval['communication_style'] == 'Verbal':
            verbal += 1
        else:
            non_verbal += 1
    return 'Verbal' if verbal >= non_verbal else 'Non Verbal'

def final_self_efficacy(intervals):
    high =[]
    low =[]
    for interval in intervals:
        high.append(interval['self_efficacy'][0])
        low.append(interval['self_efficacy'][1])
    return (high,low)

def final_leadership(intervals):
    authoritative = 0
    democratic = 0
    for interval in intervals:
        if interval['leadership'] == 'Authoritative':
            authoritative += 1
        else:
            democratic += 1
    return 'Authoritative' if authoritative >= democratic else 'Democratic'


def compute_final_data(intervals1, intervals2):
    return {
        'status': 'finalData',
        'message': 'Final session data calculated and sent to client',
        'final_data': [
            {
                'role': final_user_role(intervals1),
                'communication_style': final_communication_style(intervals1),
                'self_efficacy': final_self_efficacy(intervals1),
                'interruptions': final_interruptions(intervals1),
                'leadership': final_leadership(intervals1),
                'loc': final_lines_of_code(intervals1)
            },
            {
                'role': final_user_role(intervals2),
                'communication_style': final_communication_style(intervals2),
                'self_efficacy': final_self_efficacy(intervals2),
                'interruptions': final_interruptions(intervals2),
                'leadership': final_leadership(intervals2),
                'loc': final_lines_of_code(intervals2)
            }
        ]
    }




async def handler(websocket, path):
    try:
        async for message in websocket:
            stop = False
            print(f"Received message: {message}")
            #Send grouped interval data back to the client one at a time every 30 seconds
            # for interval_group in grouped_interval_data:
            #     await asyncio.sleep(15)  # Wait for 30 seconds before sending the next group
            #     await websocket.send(json.dumps(interval_group))
            #     print(f"Sent interval data for timeframe {interval_group['interval_data'][0]['timeframe']}")

            # Send interval data one at a time every 30 seconds
            if message == 'Hello Server':
                for interval_group in grouped_interval_data:
                    await asyncio.sleep(30)  # Wait for 30 seconds before sending the next group
                    await websocket.send(json.dumps(interval_group))
                    print(f"Sent interval data for timeframe {interval_group['interval_data'][0]['timeframe']}")
            
            # Handle EndSession command
            elif message == 'Endsession':
                stop = True
                final_data = compute_final_data(intervals1, intervals2)
                await websocket.send(json.dumps(final_data))
                print("Sent final session data")

    except websockets.ConnectionClosed:
        print("Connection closed")
    except Exception as e:
        print(f"Error: {e}")

async def start_server():
    try:
        server = await websockets.serve(handler, "localhost", 8765)
        print("Server started")  # Print message to indicate server has started
        await server.wait_closed()  # Keep the server running
    except Exception as e:
        print(f"Error starting server: {e}")

# Run the server
asyncio.run(start_server())
