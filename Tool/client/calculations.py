#need to get keystroke count from database
def determine_user_role(p1,p2):
    X1  = p1/(p1 + p2)
    X2 = p2/(p1+p2)
    if X1 > X2:
        user1 = "Driver"
        user2= "Navigator"
    else:
        user2 = "Driver"
        user1 = "Navigator"
    return (user1, X1, user2, X2)

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

    # Iterate over each event in user2's data
    for event2 in utterances2:
        start2 = event2['start_timestamp']
        end2 = event2['end_timestamp']

        # Check for interruptions by user1 during user2's event
        for event1 in utterances1:
            start1 = event1['start_timestamp']
            if event2['event'] == 'speech' and event1['event'] == 'speech' and start2 <= start1 <= end2:
                print(event2,event1,"\n")
                user1_interruptions += 1

    return user1_interruptions, user2_interruptions

def rapport_score(s1):
    
    return

#to-do
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
    if high > low:
        return "High"
    else:
        "Low"

emotions= [{'emotion': 'happy', 'start_timestamp': '9.76 sec', 'end_timestamp': '16.47 sec'}, {'emotion': 'neutral', 
'start_timestamp': '16.47 sec', 'end_timestamp': '24.88 sec'}, {'emotion': 'happy', 'start_timestamp': '24.88 sec', 'end_timestamp': '27.94 sec'}, {'emotion': 'sad', 'start_timestamp': '27.94 sec', 'end_timestamp': '29.50 sec'}, {'emotion': 'happy', 'start_timestamp': '29.50 sec', 'end_timestamp': '31.77 sec'}, {'emotion': 'neutral', 'start_timestamp': '31.77 sec', 'end_timestamp': '41.70 sec'}, {'emotion': 'fear', 'start_timestamp': '41.70 sec', 'end_timestamp': '42.53 sec'}, {'emotion': 'neutral', 'start_timestamp': '42.53 sec', 'end_timestamp': '44.09 sec'}, {'emotion': 'fear', 'start_timestamp': '44.09 sec', 'end_timestamp': '44.85 sec'}, {'emotion': 'neutral', 'start_timestamp': '44.85 sec', 'end_timestamp': '50.30 sec'}, {'emotion': 'surprise', 'start_timestamp': '50.30 sec', 'end_timestamp': '50.99 sec'}, {'emotion': 'fear', 'start_timestamp': '50.99 sec', 'end_timestamp': '53.39 sec'}, {'emotion': 'neutral', 'start_timestamp': '53.39 sec', 'end_timestamp': '56.41 sec'}, {'emotion': 'fear', 'start_timestamp': '56.41 sec', 'end_timestamp': '57.13 sec'}, {'emotion': 'neutral', 'start_timestamp': '57.13 sec', 'end_timestamp': '63.33 sec'}, {'emotion': 'surprise', 'start_timestamp': '63.33 sec', 'end_timestamp': '64.12 sec'}, {'emotion': 'neutral', 'start_timestamp': '64.12 sec', 'end_timestamp': '64.91 sec'}, {'emotion': 'surprise', 'start_timestamp': '64.91 sec', 'end_timestamp': '65.68 sec'}, {'emotion': 'happy', 'start_timestamp': '65.68 sec', 'end_timestamp': '69.78 sec'}, {'emotion': 'neutral', 'start_timestamp': '69.78 sec', 'end_timestamp': '80.04 sec'}, {'emotion': 'sad', 'start_timestamp': '80.04 sec', 'end_timestamp': '80.81 sec'}, {'emotion': 'neutral', 'start_timestamp': '80.81 sec', 'end_timestamp': '85.30 sec'}]

utterances=[
    {
        "start_timestamp": 0.0,
        "end_timestamp": 8.8,
        "event": "speech",
        "transcription": " Hello, I'm Minali. Can you check the server code? It just reaches in the server folder. It's the file"
    },
    {
        "start_timestamp": 8.8,
        "end_timestamp": 36.28,
        "event": "speech",
        "transcription": " wsr.py? Yes, that's right, that's right. Maybe not sure. Interesting. Whoa, that's big. Right."
    },
    {
        "start_timestamp": 11.917940616607666,
        "end_timestamp": 12.298444032669067,
        "event": "pause"
    },
    {
        "start_timestamp": 15.0,
        "end_timestamp": 15.5,
        "event": "Pulse"
    },
    {
        "start_timestamp": 16.0,
        "end_timestamp": 16.5,
        "event": "Crunch"
    },
    {
        "start_timestamp": 16.397663354873657,
        "end_timestamp": 16.77860188484192,
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
        "event": "Pulse"
    },
    {
        "start_timestamp": 17.5,
        "end_timestamp": 18.0,
        "event": "Rapping"
    },
    {
        "start_timestamp": 17.997289657592773,
        "end_timestamp": 18.187286138534546,
        "event": "pause"
    },
    {
        "start_timestamp": 18.0,
        "end_timestamp": 18.5,
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
        "event": "Rapping"
    },
    {
        "start_timestamp": 19.5,
        "end_timestamp": 20.0,
        "event": "Chant"
    },
    {
        "start_timestamp": 20.0,
        "end_timestamp": 20.5,
        "event": "Crunch"
    },
    {
        "start_timestamp": 20.367318630218506,
        "end_timestamp": 20.618753671646118,
        "event": "pause"
    },
    {
        "start_timestamp": 20.5,
        "end_timestamp": 21.0,
        "event": "Crunch"
    },
    {
        "start_timestamp": 21.5,
        "end_timestamp": 22.0,
        "event": "Soundtrack music"
    },
    {
        "start_timestamp": 22.0,
        "end_timestamp": 22.5,
        "event": "Chant"
    },
    {
        "start_timestamp": 22.218504905700684,
        "end_timestamp": 22.287878274917603,
        "event": "pause"
    },
    {
        "start_timestamp": 23.0,
        "end_timestamp": 23.5,
        "event": "Chant"
    },
    {
        "start_timestamp": 23.5,
        "end_timestamp": 24.0,
        "event": "Whale vocalization"
    },
    {
        "start_timestamp": 24.0,
        "end_timestamp": 24.5,
        "event": "Rapping"
    },
    {
        "start_timestamp": 24.5,
        "end_timestamp": 25.0,
        "event": "Crunch"
    },
    {
        "start_timestamp": 26.0,
        "end_timestamp": 26.5,
        "event": "Chant"
    },
    {
        "start_timestamp": 26.5,
        "end_timestamp": 27.0,
        "event": "Crunch"
    },
    {
        "start_timestamp": 27.0,
        "end_timestamp": 27.5,
        "event": "Crunch"
    },
    {
        "start_timestamp": 27.5,
        "end_timestamp": 28.0,
        "event": "Crunch"
    },
    {
        "start_timestamp": 28.29850172996521,
        "end_timestamp": 28.29850172996521,
        "event": "pause"
    },
    {
        "start_timestamp": 30.0,
        "end_timestamp": 30.5,
        "event": "Crunch"
    },
    {
        "start_timestamp": 31.49847149848938,
        "end_timestamp": 31.887486457824707,
        "event": "pause"
    },
    {
        "start_timestamp": 32.0,
        "end_timestamp": 32.5,
        "event": "Crunch"
    },
    {
        "start_timestamp": 32.5,
        "end_timestamp": 33.0,
        "event": "Chant"
    },
    {
        "start_timestamp": 33.0,
        "end_timestamp": 33.5,
        "event": "Yodeling"
    },
    {
        "start_timestamp": 36.28,
        "end_timestamp": 48.28,
        "event": "speech",
        "transcription": " We can see we can check that. Okay, that's right. That's right. We can't really understand"
    },
    {
        "start_timestamp": 38.0,
        "end_timestamp": 38.5,
        "event": "Crunch"
    },
    {
        "start_timestamp": 38.5,
        "end_timestamp": 39.0,
        "event": "Pulse"
    },
    {
        "start_timestamp": 39.0,
        "end_timestamp": 39.5,
        "event": "Whale vocalization"
    },
    {
        "start_timestamp": 40.33755874633789,
        "end_timestamp": 40.33755874633789,
        "event": "pause"
    },
    {
        "start_timestamp": 41.5,
        "end_timestamp": 42.0,
        "event": "Crunch"
    },
    {
        "start_timestamp": 47.5,
        "end_timestamp": 48.0,
        "event": "Crunch"
    },
    {
        "start_timestamp": 48.0,
        "end_timestamp": 48.5,
        "event": "Crunch"
    },
    {
        "start_timestamp": 48.28,
        "end_timestamp": 77.28,
        "event": "speech",
        "transcription": " grade read a lot of papers and stuff. Maybe not sure. Yeah. Okay, like do. Yeah, that one. Yeah, there you go. Right. Right. Right. Oh my god, are you crazy? Holy moly. Please. Please, get in here right now. No way that's going to happen."
    },
    {
        "start_timestamp": 54.0276243686676,
        "end_timestamp": 54.098801136016846,
        "event": "pause"
    },
    {
        "start_timestamp": 57.0,
        "end_timestamp": 57.5,
        "event": "Crunch"
    },
    {
        "start_timestamp": 65.5,
        "end_timestamp": 66.0,
        "event": "Crunch"
    },
    {
        "start_timestamp": 66.0,
        "end_timestamp": 66.5,
        "event": "Crunch"
    },
    {
        "start_timestamp": 66.5,
        "end_timestamp": 67.0,
        "event": "Snort"
    },
    {
        "start_timestamp": 67.0,
        "end_timestamp": 67.5,
        "event": "Rumble"
    },
    {
        "start_timestamp": 69.38757014274597,
        "end_timestamp": 69.51698231697083,
        "event": "pause"
    },
    {
        "start_timestamp": 70.0,
        "end_timestamp": 70.5,
        "event": "Wail, moan"
    },
    {
        "start_timestamp": 70.5,
        "end_timestamp": 71.0,
        "event": "Wail, moan"
    },
    {
        "start_timestamp": 71.0,
        "end_timestamp": 71.5,
        "event": "Chirp tone"
    },
    {
        "start_timestamp": 71.5,
        "end_timestamp": 72.0,
        "event": "Crunch"
    },
    {
        "start_timestamp": 72.0,
        "end_timestamp": 72.5,
        "event": "Crunch"
    },
    {
        "start_timestamp": 72.5276083946228,
        "end_timestamp": 72.90731358528137,
        "event": "pause"
    },
    {
        "start_timestamp": 74.5,
        "end_timestamp": 75.0,
        "event": "Crunch"
    },
    {
        "start_timestamp": 75.0,
        "end_timestamp": 75.5,
        "event": "Crunch"
    },
    {
        "start_timestamp": 77.28,
        "end_timestamp": 79.28,
        "event": "speech",
        "transcription": " that's gonna happen."
    },
    {
        "start_timestamp": 80.71705079078674,
        "end_timestamp": 81.29822373390198,
        "event": "pause"
    },
    {
        "start_timestamp": 81.28,
        "end_timestamp": 82.28,
        "event": "speech",
        "transcription": " Crazy."
    },
    {
        "start_timestamp": 81.5,
        "end_timestamp": 82.0,
        "event": "Crunch"
    },
    {
        "start_timestamp": 82.28,
        "end_timestamp": 84.28,
        "event": "speech",
        "transcription": " Are you crazy or something bro?"
    },
    {
        "start_timestamp": 83.5,
        "end_timestamp": 84.0,
        "event": "Crunch"
    },
    {
        "start_timestamp": 84.28,
        "end_timestamp": 86.28,
        "event": "speech",
        "transcription": "bro?"
    },
    {
        "start_timestamp": 86.28,
        "end_timestamp": 88.28,
        "event": "speech",
        "transcription": " Uh-huh."
    },
    {
        "start_timestamp": 87.11757588386536,
        "end_timestamp": 87.3076548576355,
        "event": "pause"
    },
    {
        "start_timestamp": 88.28,
        "end_timestamp": 89.28,
        "event": "speech",
        "transcription": " Uh-huh."
    },
    {
        "start_timestamp": 89.28,
        "end_timestamp": 90.28,
        "event": "speech",
        "transcription": " No."
    },
    {
        "start_timestamp": 89.5,
        "end_timestamp": 90.0,
        "event": "Crunch"
    },
    {
        "start_timestamp": 90.0,
        "end_timestamp": 90.5,
        "event": "Crunch"
    },
    {
        "start_timestamp": 92.0,
        "end_timestamp": 92.5,
        "event": "Crunch"
    }
]

utterances2=[
    {
        "start_timestamp": 0.0,
        "end_timestamp": 16.36,
        "event": "speech",
        "transcription": " that. Stop. I said stop. It's gonna be a long pause and nothing else because I don't"
    },
    {
        "start_timestamp": 0.5,
        "end_timestamp": 1.0,
        "event": "Crunch"
    },
    {
        "start_timestamp": 0.834587812423706,
        "end_timestamp": 1.1537249088287354,
        "event": "pause"
    },
    {
        "start_timestamp": 1.0,
        "end_timestamp": 1.5,
        "event": "Crunch"
    },
    {
        "start_timestamp": 1.5,
        "end_timestamp": 2.0,
        "event": "Crunch"
    },
    {
        "start_timestamp": 2.0,
        "end_timestamp": 2.5,
        "event": "Crunch"
    },
    {
        "start_timestamp": 2.5,
        "end_timestamp": 3.0,
        "event": "Crunch"
    },
    {
        "start_timestamp": 2.6246490478515625,
        "end_timestamp": 3.0738754272460938,
        "event": "pause"
    },
    {
        "start_timestamp": 3.0,
        "end_timestamp": 3.5,
        "event": "Crunch"
    },
    {
        "start_timestamp": 3.5,
        "end_timestamp": 4.0,
        "event": "Pulse"
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
        "start_timestamp": 5.754182815551758,
        "end_timestamp": 7.2347681522369385,
        "event": "pause"
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
        "start_timestamp": 7.0,
        "end_timestamp": 7.5,
        "event": "Crunch"
    },
    {
        "start_timestamp": 10.0,
        "end_timestamp": 10.5,
        "event": "Crunch"
    },
    {
        "start_timestamp": 14.5,
        "end_timestamp": 15.0,
        "event": "Crunch"
    },
    {
        "start_timestamp": 14.913059711456299,
        "end_timestamp": 15.033864259719849,
        "event": "pause"
    },
    {
        "start_timestamp": 16.36,
        "end_timestamp": 22.32,
        "event": "speech",
        "transcription": " really need more information."
    },
    {
        "start_timestamp": 17.5,
        "end_timestamp": 18.0,
        "event": "Crunch"
    },
    {
        "start_timestamp": 18.0,
        "end_timestamp": 18.5,
        "event": "Crunch"
    },
    {
        "start_timestamp": 18.174518823623657,
        "end_timestamp": 18.874683141708374,
        "event": "pause"
    },
    {
        "start_timestamp": 18.5,
        "end_timestamp": 19.0,
        "event": "Crunch"
    },
    {
        "start_timestamp": 21.24393582344055,
        "end_timestamp": 21.95251441001892,
        "event": "pause"
    },
    {
        "start_timestamp": 21.5,
        "end_timestamp": 22.0,
        "event": "Crunch"
    },
    {
        "start_timestamp": 22.0,
        "end_timestamp": 22.5,
        "event": "Crunch"
    },
    {
        "start_timestamp": 22.5,
        "end_timestamp": 23.0,
        "event": "Crunch"
    },
    {
        "start_timestamp": 22.52432155609131,
        "end_timestamp": 23.105220794677734,
        "event": "pause"
    },
    {
        "start_timestamp": 23.0,
        "end_timestamp": 23.5,
        "event": "Crunch"
    },
    {
        "start_timestamp": 23.5,
        "end_timestamp": 24.0,
        "event": "Crunch"
    },
    {
        "start_timestamp": 24.0,
        "end_timestamp": 24.5,
        "event": "Crunch"
    },
    {
        "start_timestamp": 24.5,
        "end_timestamp": 25.0,
        "event": "Crunch"
    },
    {
        "start_timestamp": 24.95312762260437,
        "end_timestamp": 25.022700309753418,
        "event": "pause"
    },
    {
        "start_timestamp": 25.0,
        "end_timestamp": 25.5,
        "event": "Crunch"
    },
    {
        "start_timestamp": 25.5,
        "end_timestamp": 26.0,
        "event": "Crunch"
    },
    {
        "start_timestamp": 25.664815187454224,
        "end_timestamp": 27.00429654121399,
        "event": "pause"
    },
    {
        "start_timestamp": 26.0,
        "end_timestamp": 26.5,
        "event": "Crunch"
    },
    {
        "start_timestamp": 26.5,
        "end_timestamp": 27.0,
        "event": "Crunch"
    },
    {
        "start_timestamp": 27.0,
        "end_timestamp": 27.5,
        "event": "Crunch"
    },
    {
        "start_timestamp": 27.5,
        "end_timestamp": 28.0,
        "event": "Crunch"
    },
    {
        "start_timestamp": 27.58524489402771,
        "end_timestamp": 29.5635404586792,
        "event": "pause"
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
        "start_timestamp": 29.28,
        "end_timestamp": 40.16,
        "event": "speech",
        "transcription": " Good good good good good good good good good good good good good good good good"
    },
    {
        "start_timestamp": 29.5,
        "end_timestamp": 30.0,
        "event": "Crunch"
    },
    {
        "start_timestamp": 30.0,
        "end_timestamp": 30.5,
        "event": "Crunch"
    },
    {
        "start_timestamp": 31.48460555076599,
        "end_timestamp": 32.704439878463745,
        "event": "pause"
    },
    {
        "start_timestamp": 32.5,
        "end_timestamp": 33.0,
        "event": "Crunch"
    },
    {
        "start_timestamp": 33.0,
        "end_timestamp": 33.5,
        "event": "Crunch"
    },
    {
        "start_timestamp": 33.5,
        "end_timestamp": 34.0,
        "event": "Crunch"
    },
    {
        "start_timestamp": 34.75448703765869,
        "end_timestamp": 35.96346831321716,
        "event": "pause"
    },
    {
        "start_timestamp": 35.5,
        "end_timestamp": 36.0,
        "event": "Crunch"
    },
    {
        "start_timestamp": 36.0,
        "end_timestamp": 36.5,
        "event": "Crunch"
    },
    {
        "start_timestamp": 36.5,
        "end_timestamp": 37.0,
        "event": "Crunch"
    },
    {
        "start_timestamp": 38.20484209060669,
        "end_timestamp": 39.48455810546875,
        "event": "pause"
    },
    {
        "start_timestamp": 39.0,
        "end_timestamp": 39.5,
        "event": "Crunch"
    },
    {
        "start_timestamp": 39.5,
        "end_timestamp": 40.0,
        "event": "Crunch"
    },
    {
        "start_timestamp": 40.0,
        "end_timestamp": 40.5,
        "event": "Crunch"
    },
    {
        "start_timestamp": 42.5,
        "end_timestamp": 43.0,
        "event": "Crunch"
    },
    {
        "start_timestamp": 43.0,
        "end_timestamp": 43.5,
        "event": "Crunch"
    },
    {
        "start_timestamp": 43.5,
        "end_timestamp": 44.0,
        "event": "Crunch"
    },
    {
        "start_timestamp": 44.0,
        "end_timestamp": 44.5,
        "event": "Crunch"
    },
    {
        "start_timestamp": 44.5,
        "end_timestamp": 45.0,
        "event": "Crunch"
    },
    {
        "start_timestamp": 45.0,
        "end_timestamp": 45.5,
        "event": "Crunch"
    },
    {
        "start_timestamp": 45.053855895996094,
        "end_timestamp": 45.185449838638306,
        "event": "pause"
    },
    {
        "start_timestamp": 45.5,
        "end_timestamp": 46.0,
        "event": "Crunch"
    },
    {
        "start_timestamp": 45.824366092681885,
        "end_timestamp": 45.88373136520386,
        "event": "pause"
    },
    {
        "start_timestamp": 46.0,
        "end_timestamp": 46.5,
        "event": "Crunch"
    },
    {
        "start_timestamp": 46.5,
        "end_timestamp": 47.0,
        "event": "Crunch"
    },
    {
        "start_timestamp": 46.96,
        "end_timestamp": 56.84,
        "event": "speech",
        "transcription": " It's so crazy. This code is so crazy like the sound detections are crazy. The voice is"
    },
    {
        "start_timestamp": 47.0,
        "end_timestamp": 47.5,
        "event": "Crunch"
    },
    {
        "start_timestamp": 47.5,
        "end_timestamp": 48.0,
        "event": "Crunch"
    },
    {
        "start_timestamp": 48.0,
        "end_timestamp": 48.5,
        "event": "Crunch"
    },
    {
        "start_timestamp": 48.5,
        "end_timestamp": 49.0,
        "event": "Crack"
    },
    {
        "start_timestamp": 53.18516778945923,
        "end_timestamp": 53.24427795410156,
        "event": "pause"
    },
    {
        "start_timestamp": 54.5,
        "end_timestamp": 55.0,
        "event": "Crunch"
    },
    {
        "start_timestamp": 56.5,
        "end_timestamp": 57.0,
        "event": "Crunch"
    },
    {
        "start_timestamp": 56.84,
        "end_timestamp": 67.28,
        "event": "speech",
        "transcription": " perfect but the sound is no way that's right it's it's very crazy."
    },
    {
        "start_timestamp": 57.0,
        "end_timestamp": 57.5,
        "event": "Crunch"
    },
    {
        "start_timestamp": 59.71441650390625,
        "end_timestamp": 59.71441650390625,
        "event": "pause"
    },
    {
        "start_timestamp": 62.0,
        "end_timestamp": 62.5,
        "event": "Crunch"
    },
    {
        "start_timestamp": 62.84309458732605,
        "end_timestamp": 62.912445306777954,
        "event": "pause"
    },
    {
        "start_timestamp": 65.0,
        "end_timestamp": 65.5,
        "event": "Crunch"
    },
    {
        "start_timestamp": 65.72435808181763,
        "end_timestamp": 65.79312825202942,
        "event": "pause"
    },
    {
        "start_timestamp": 66.49408841133118,
        "end_timestamp": 66.55447506904602,
        "event": "pause"
    },
    {
        "start_timestamp": 68.0,
        "end_timestamp": 68.5,
        "event": "Crunch"
    },
    {
        "start_timestamp": 68.5,
        "end_timestamp": 69.0,
        "event": "Crunch"
    },
    {
        "start_timestamp": 69.0,
        "end_timestamp": 69.5,
        "event": "Crunch"
    },
    {
        "start_timestamp": 69.5,
        "end_timestamp": 70.0,
        "event": "Crunch"
    },
    {
        "start_timestamp": 70.0,
        "end_timestamp": 70.5,
        "event": "Crunch"
    },
    {
        "start_timestamp": 70.5,
        "end_timestamp": 71.0,
        "event": "Crunch"
    },
    {
        "start_timestamp": 71.0,
        "end_timestamp": 71.5,
        "event": "Crunch"
    },
    {
        "start_timestamp": 71.5,
        "end_timestamp": 72.0,
        "event": "Crunch"
    },
    {
        "start_timestamp": 72.0,
        "end_timestamp": 72.5,
        "event": "Crunch"
    },
    {
        "start_timestamp": 72.5,
        "end_timestamp": 73.0,
        "event": "Crunch"
    },
    {
        "start_timestamp": 72.6333839893341,
        "end_timestamp": 75.39436626434326,
        "event": "pause"
    },
    {
        "start_timestamp": 73.0,
        "end_timestamp": 73.5,
        "event": "Crunch"
    },
    {
        "start_timestamp": 73.5,
        "end_timestamp": 74.0,
        "event": "Crunch"
    },
    {
        "start_timestamp": 74.0,
        "end_timestamp": 74.5,
        "event": "Crunch"
    },
    {
        "start_timestamp": 74.5,
        "end_timestamp": 75.0,
        "event": "Crunch"
    },
    {
        "start_timestamp": 75.0,
        "end_timestamp": 75.5,
        "event": "Crunch"
    },
    {
        "start_timestamp": 75.5,
        "end_timestamp": 76.0,
        "event": "Crunch"
    },
    {
        "start_timestamp": 76.0,
        "end_timestamp": 76.5,
        "event": "Crunch"
    },
    {
        "start_timestamp": 76.5,
        "end_timestamp": 77.0,
        "event": "Crunch"
    },
    {
        "start_timestamp": 77.0,
        "end_timestamp": 77.5,
        "event": "Crunch"
    },
    {
        "start_timestamp": 77.3138918876648,
        "end_timestamp": 77.6926167011261,
        "event": "pause"
    },
    {
        "start_timestamp": 77.5,
        "end_timestamp": 78.0,
        "event": "Crunch"
    },
    {
        "start_timestamp": 78.0,
        "end_timestamp": 78.5,
        "event": "Crunch"
    },
    {
        "start_timestamp": 78.46506214141846,
        "end_timestamp": 78.84410524368286,
        "event": "pause"
    },
    {
        "start_timestamp": 78.5,
        "end_timestamp": 79.0,
        "event": "Crunch"
    },
    {
        "start_timestamp": 79.0,
        "end_timestamp": 79.5,
        "event": "Crunch"
    },
    {
        "start_timestamp": 79.5,
        "end_timestamp": 80.0,
        "event": "Crunch"
    },
    {
        "start_timestamp": 80.0,
        "end_timestamp": 80.5,
        "event": "Crunch"
    },
    {
        "start_timestamp": 80.06475853919983,
        "end_timestamp": 80.51442170143127,
        "event": "pause"
    },
    {
        "start_timestamp": 80.5,
        "end_timestamp": 81.0,
        "event": "Crunch"
    },
    {
        "start_timestamp": 81.0,
        "end_timestamp": 81.5,
        "event": "Crunch"
    },
    {
        "start_timestamp": 81.47435116767883,
        "end_timestamp": 81.7946515083313,
        "event": "pause"
    },
    {
        "start_timestamp": 81.5,
        "end_timestamp": 82.0,
        "event": "Crunch"
    },
    {
        "start_timestamp": 82.0,
        "end_timestamp": 82.5,
        "event": "Crunch"
    },
    {
        "start_timestamp": 82.5,
        "end_timestamp": 83.0,
        "event": "Crunch"
    },
    {
        "start_timestamp": 83.0,
        "end_timestamp": 83.5,
        "event": "Crunch"
    },
    {
        "start_timestamp": 83.5,
        "end_timestamp": 84.0,
        "event": "Crunch"
    },
    {
        "start_timestamp": 84.0,
        "end_timestamp": 84.5,
        "event": "Crunch"
    },
    {
        "start_timestamp": 84.47439908981323,
        "end_timestamp": 85.31370615959167,
        "event": "pause"
    },
    {
        "start_timestamp": 84.5,
        "end_timestamp": 85.0,
        "event": "Crunch"
    },
    {
        "start_timestamp": 85.0,
        "end_timestamp": 85.5,
        "event": "Crunch"
    },
    {
        "start_timestamp": 85.5,
        "end_timestamp": 86.0,
        "event": "Crunch"
    },
    {
        "start_timestamp": 86.0,
        "end_timestamp": 86.5,
        "event": "Crunch"
    },
    {
        "start_timestamp": 86.5,
        "end_timestamp": 87.0,
        "event": "Crunch"
    },
    {
        "start_timestamp": 86.9732654094696,
        "end_timestamp": 87.03330397605896,
        "event": "pause"
    },
    {
        "start_timestamp": 87.0,
        "end_timestamp": 87.5,
        "event": "Crunch"
    },
    {
        "start_timestamp": 87.5,
        "end_timestamp": 88.0,
        "event": "Crunch"
    },
    {
        "start_timestamp": 87.87403154373169,
        "end_timestamp": 88.3852481842041,
        "event": "pause"
    },
    {
        "start_timestamp": 88.0,
        "end_timestamp": 88.5,
        "event": "Crunch"
    },
    {
        "start_timestamp": 88.5,
        "end_timestamp": 89.0,
        "event": "Crunch"
    },
    {
        "start_timestamp": 89.0,
        "end_timestamp": 89.5,
        "event": "Crunch"
    },
    {
        "start_timestamp": 89.15409326553345,
        "end_timestamp": 89.21461772918701,
        "event": "pause"
    },
    {
        "start_timestamp": 89.5,
        "end_timestamp": 90.0,
        "event": "Crunch"
    },
    {
        "start_timestamp": 89.98416924476624,
        "end_timestamp": 90.04335045814514,
        "event": "pause"
    },
    {
        "start_timestamp": 90.0,
        "end_timestamp": 90.5,
        "event": "Crunch"
    },
    {
        "start_timestamp": 90.5,
        "end_timestamp": 91.0,
        "event": "Crunch"
    },
    {
        "start_timestamp": 91.0,
        "end_timestamp": 91.5,
        "event": "Crunch"
    },
    {
        "start_timestamp": 91.5,
        "end_timestamp": 92.0,
        "event": "Crunch"
    },
    {
        "start_timestamp": 92.0,
        "end_timestamp": 92.5,
        "event": "Crunch"
    },
    {
        "start_timestamp": 92.5,
        "end_timestamp": 93.0,
        "event": "Crunch"
    },
    {
        "start_timestamp": 93.0,
        "end_timestamp": 93.5,
        "event": "Crunch"
    }
]
print(communication_style(emotions,utterances))
print(self_efficacy(emotions))
print(interruptions(utterances,utterances2))