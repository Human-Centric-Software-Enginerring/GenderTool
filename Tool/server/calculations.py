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


emotion_list = [{'emotion': 'neutral', 'timestamp': 1721962156381.1973}, {'emotion': 'happy', 'timestamp': 1721962157050.0027}, {'emotion': 'neutral', 'timestamp': 1721962158352.327}, {'emotion': 'surprise', 'timestamp': 1721962159010.963}, {'emotion': 'sad', 'timestamp': 1721962160291.7124}, {'emotion': 'fear', 'timestamp': 1721962160918.401}, {'emotion': 'sad', 'timestamp': 1721962162197.5671}, {'emotion': 'neutral', 'timestamp': 1721962163552.9448}, {'emotion': 'happy', 'timestamp': 1721962168066.5361}, {'emotion': 'neutral', 'timestamp': 1721962171287.64}]
print("User X's self efficacy is: " , count_self_efficacy(emotion_list))