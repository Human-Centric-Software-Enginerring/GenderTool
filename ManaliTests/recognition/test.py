from rapport_score import rapport_scorer
from pyinstrument import Profiler

profiler = Profiler()

with profiler:

    sample_utterance1 = [
        {
            "start_timestamp": 0.0,
            "end_timestamp": 5.72,
            "event": "speech",
            "transcription": "I'll start with the HTML structure, and you can work on the CSS styling."
        },
        {
            "start_timestamp": 5.72,
            "end_timestamp": 10.96,
            "event": "speech",
            "transcription": "Great! I'll start working on the backend data processing"
        },
        {
            "start_timestamp": 23.0,
            "end_timestamp": 23.5,
            "event": "Children playing",
            "confidence": 0.8188255429267883
        }
    ]

    sample_utterance2=[
        {
            "start_timestamp": 0.0,
            "end_timestamp": 5.72,
            "event": "speech",
            "transcription": "Weather was quite different than here on the west coast."
        },
        {
            "start_timestamp": 5.72,
            "end_timestamp": 10.96,
            "event": "speech",
            "transcription": "It was a great change of pace from the cold here in Central Oregon."
        },
        {
            "start_timestamp": 23.0,
            "end_timestamp": 23.5,
            "event": "Children playing",
            "confidence": 0.8188255429267883
        }
    ]

    sample_utterance3=[ {
            "start_timestamp": 0.0,
            "end_timestamp": 7.96,
            "event": "speech",
            "transcription": " There were at least two thousand attendees at the conference and it was quite impressive"
        },
        {
            "start_timestamp": 7.96,
            "end_timestamp": 12.32,
            "event": "speech",
            "transcription": "The flight was incredible during spring break with a lot of children heading to Orlando"
        }]

    sample_utterance4=[
        {
            "start_timestamp": 0.0,
            "end_timestamp": 8.68,
            "event": "speech",
            "transcription": "We need to debug it."
        },
        {
            "start_timestamp": 8.68,
            "end_timestamp": 12.2,
            "event": "speech",
            "transcription": "Can you check logs for the error type?"
        }
    ]

    sample_utterance5=[
        {
            "start_timestamp": 0.0,
            "end_timestamp": 8.68,
            "event": "speech",
            "transcription": "Let's have some ice-cream today?"
        },
        {
            "start_timestamp": 8.68,
            "end_timestamp": 12.2,
            "event": "speech",
            "transcription": "Can you check logs for the error type?"
        }
    ]

    print(rapport_scorer(sample_utterance1))
    print(rapport_scorer(sample_utterance2))
    print(rapport_scorer(sample_utterance3))
    print(rapport_scorer(sample_utterance4))
    print(rapport_scorer(sample_utterance5))

profiler.open_in_browser()




# import requests
# # Test sending hardcoded data to API
# test_data = [
#     {"emotion": "happy", "start_timestamp": 0.0, "end_timestamp": 1.0},
#     {"emotion": "neutral", "start_timestamp": 1.0, "end_timestamp": 2.0}
# ]

# response = requests.post("http://127.0.0.1:8000/update-emotions", json=test_data)
# print(response.status_code)
# print(response.json())
# response = requests.get("http://127.0.0.1:8000/get-emotions")
# print(response.status_code)
# print(response.json())
