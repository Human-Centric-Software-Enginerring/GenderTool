import os
import json
import threading
import time
import re
import requests
from rapport_score import rapport_scorer

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

def determine_user_role(loc1, loc2):
    X1 = loc1 / (loc1 + loc2)
    X2 = loc2 / (loc1 + loc2)
    if X1 > X2:
        return "Driver"
    else:
        return "Navigator"

def interruptions(utterances1, utterances2):
    user1_interruptions = 0
    for event2 in utterances2:
        start2 = event2['start_timestamp']
        end2 = event2['end_timestamp']
        for event1 in utterances1:
            start1 = event1['start_timestamp']
            if event1['event'] == 'speech' and event2['event'] == 'speech' and start2 <= start1 <= end2:
                print(event1)
                user1_interruptions += 1
    return user1_interruptions

def communication_style(utterances):
    verbal_time = 0
    for event in utterances:
        if event["event"].lower() == "speech":
            verbal_time += event['end_timestamp']-event['start_timestamp']
    #total interval time is 300 seconds, if speaks more than 50% time,communication style is verbal.
    if verbal_time > 15:
        return "Verbal"
    else:
        return "Non Verbal"
    
    #proportion- talking /verbal speech over the interval > 50% verbal else non-verbal
    # non_verbal = len(emotions) + sum(1 for event in utterances if event["event"].lower() not in ["speech", "pause"])
    # verbal = sum(1 for event in utterances if event["event"].lower() == "speech")
    # if non_verbal > verbal:
    #     return "Non-Verbal"
    # else:
    #     return "Verbal"

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

def leadership(loc1, loc2, utterances1, utterances2):
    #proportions
    words1 = 0
    words2 =0
    for event1 in utterances1:
        words1 += event1['words']
    for event2 in utterances2:
        words2 += event2['words']
    L1 = (loc1/(loc1+loc2)) + (words1/(words1+words2))
    L2 = (loc2/(loc1+loc2)) + ((words2/words1+words2))
    if (L1-L2) > 1:
        return "Authoritative"
    else:
        return "Democratic"

    
def trigger_scripts():
    # Function to run scripts and wait for them to complete
    base_dir = "D:\\HCI_Research\\ManaliTests\\recognition"
    def run_script(script_name):
        script_path = os.path.join(base_dir, script_name)
        os.system(f"python {script_path}")

    # Start the scripts in separate threads
    threads = []
    for script in ["emotion_detection.py", "utterances.py","keystroke.py"]:
        thread = threading.Thread(target=run_script, args=(script,))
        thread.start()
        threads.append(thread)

    # Wait for all scripts to complete
    for thread in threads:
        thread.join()

def process_generated_data():
    keystroke_data = requests.get("http://127.0.0.1:8000/get-keystrokes").json()
    face_detection_data = requests.get("http://127.0.0.1:8000/get-emotions").json()
    utterances_data = requests.get("http://127.0.0.1:8000/get-utterances").json()
    print("Keystroke data: " ,keystroke_data)
    print("Emotion data: " ,face_detection_data)
    print("Utterance data: ",utterances_data)

    rapport = rapport_score(utterances_data)
    #processed_utterance_data(utterances_data)
    
    # print("LOC:", keystroke_data['lines_of_code'])
    #print("Rapport Score:", rapport)
    # print("Processed Utterances:", processed_utterances)
    
    #Simulated user data for demonstration purposes
    user1_data = {
        'data': {
            'LOC': keystroke_data['lines_of_code'],
            'utterances': utterances_data
        },
        'intervals': []
    }
    user2_data = {
        'data': {
            'LOC': 20,
            'utterances': [
    {
        "start_timestamp": 1.6,
        "end_timestamp": 8.68,
        "event": "speech",
        "transcription": " The flight was incredible during spring break with a lot of children heading to Orlando",
        "words": 15

    },
    {
        "start_timestamp": 8.68,
        "end_timestamp": 12.2,
        "event": "speech",
        "transcription": " for Universal Studios and all of the theme parks in Central Florida.",
        "words": 12
    },
    {
        "start_timestamp": 13.2,
        "end_timestamp": 30.4,
        "event": "speech",
        "transcription": " for Universal Studios and all of the theme parks in Central Florida.",
        "words": 12
    }
    ]
        },
        'intervals': []
    }
    
    loc1 = user1_data['data']['LOC']
    loc2 = user2_data['data']['LOC']
    utterances1 = user1_data['data']['utterances']
    utterances2 = user2_data['data']['utterances']
    emotions1 = face_detection_data
    
    role_user1 = determine_user_role(loc1, loc2)
    user1_interruptions = interruptions(utterances1, utterances2)
    comm_style_user1 = communication_style(utterances1)
    self_efficacy_user1 = self_efficacy(emotions1)
    leadership_style = leadership(loc1, loc2, utterances1, utterances2)
    
    # Store results in the corresponding user's interval data
    user1_data['intervals'].append({
        "timeframe": 1, 
        "role": role_user1,
        "loc" : loc1,
        "communication_style": comm_style_user1,
        "self_efficacy": self_efficacy_user1,
        "interruptions": user1_interruptions,
        "leadership": leadership_style,
        "rapport_score": rapport
    })

    print("User 1 Data:")
    print(user1_data['intervals'])


# Main function to trigger scripts and process data
def main():
    trigger_scripts()
    process_generated_data()

if __name__ == "__main__":
    main()
