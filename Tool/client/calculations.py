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

def count_self_efficacy(emotion_list):
    # Define categories of emotions
    negative_emotions = {"sad", "angry"}
    positive_emotions = {"happy", "neutral", "surprised"}
    # Initialize counters
    counts = {
        "negative": 0,
        "positive": 0
    }
    # Count occurrences
    for emotion_data in emotion_list:
        emotion = emotion_data['emotion']
        if emotion in negative_emotions:
            counts["negative"] += 1
        elif emotion in positive_emotions:
            counts["positive"] += 1
    print(counts)
    if counts['negative'] > counts['positive']:
        return "Low"
    else:
        return "High"


#to-do
def communication_style(e1,e2,s1,s2):
    return 0

def interruptions(s1,s2):
    return




emotion_list = [{'emotion': 'neutral', 'timestamp': 1721962156381.1973}, {'emotion': 'happy', 'timestamp': 1721962157050.0027}, {'emotion': 'neutral', 'timestamp': 1721962158352.327}, {'emotion': 'surprise', 'timestamp': 1721962159010.963}, {'emotion': 'sad', 'timestamp': 1721962160291.7124}, {'emotion': 'fear', 'timestamp': 1721962160918.401}, {'emotion': 'sad', 'timestamp': 1721962162197.5671}, {'emotion': 'neutral', 'timestamp': 1721962163552.9448}, {'emotion': 'happy', 'timestamp': 1721962168066.5361}, {'emotion': 'neutral', 'timestamp': 1721962171287.64}]
[
    {
        "start_timestamp": 0.7785203456878662,
        "end_timestamp": 0.9784083366394043,
        "event": "pause"
    },
    {
        "start_timestamp": 1.547856330871582,
        "end_timestamp": 1.547856330871582,
        "event": "pause"
    },
    {
        "start_timestamp": 4.940053462982178,
        "end_timestamp": 5.068324327468872,
        "event": "pause"
    },
    {
        "start_timestamp": 9.228927850723267,
        "end_timestamp": 9.737693548202515,
        "event": "pause"
    },
    {
        "start_timestamp": 13.387543439865112,
        "end_timestamp": 13.779017210006714,
        "event": "pause"
    },
    {
        "start_timestamp": 15.818559646606445,
        "end_timestamp": 16.26836609840393,
        "event": "pause"
    },
    {
        "start_timestamp": 24.398748636245728,
        "end_timestamp": 25.22948694229126,
        "event": "pause"
    },
    {
        "start_timestamp": 0.0,
        "end_timestamp": 7.0,
        "event": "speech",
        "transcription": " Hello, hello, hello."
    },
    {
        "start_timestamp": 7.0,
        "end_timestamp": 10.0,
        "event": "speech",
        "transcription": " Yeah."
    },
    {
        "start_timestamp": 10.0,
        "end_timestamp": 14.0,
        "event": "speech",
        "transcription": " I understand that."
    },
    {
        "start_timestamp": 14.0,
        "end_timestamp": 21.0,
        "event": "speech",
        "transcription": " Yeah."
    },
    {
        "start_timestamp": 21.0,
        "end_timestamp": 24.0,
        "event": "speech",
        "transcription": " Yeah."
    },
    {
        "start_timestamp": 24.0,
        "end_timestamp": 28.0,
        "event": "speech",
        "transcription": " Okay."
    },
    {
        "start_timestamp": 28.0,
        "end_timestamp": 31.0,
        "event": "speech",
        "transcription": " Good."
    },
    {
        "start_timestamp": 0.0,
        "end_timestamp": 0.5,
        "event": "Crunch"
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
    }]
print("User X's self efficacy is: " , count_self_efficacy(emotion_list))
