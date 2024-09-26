from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import uvicorn

app = FastAPI()

class KeystrokeData(BaseModel):
    lines_of_code: int

class UtteranceData(BaseModel):
    start_timestamp: float
    end_timestamp: float
    event: str
    transcription: str = None
    words : float = None

class EmotionData(BaseModel):
    emotion: str
    start_timestamp: float
    end_timestamp: float

# Initialize data storage
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

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
