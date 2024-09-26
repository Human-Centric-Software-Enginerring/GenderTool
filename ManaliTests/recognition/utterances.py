import wave
import whisper
import webrtcvad
import json
import tensorflow as tf
import tensorflow_hub as hub
import numpy as np
import pandas as pd
import os
import time
import requests  # Import the requests library for HTTP requests

# Initialize Whisper model
model = whisper.load_model("base")

# Initialize WebRTC VAD
vad = webrtcvad.Vad()
vad.set_mode(1)

# Initialize YAMNet model from TensorFlow Hub
yamnet_model = hub.load('https://tfhub.dev/google/yamnet/1')

# Load class map
class_map_path = "D:\\HCI_Research\\ManaliTests\\recognition\\yamnet_class_map.csv"
df = pd.read_csv(class_map_path, header=None)
class_names = df[2].values

# Audio processing parameters
RATE = 16000
FRAME_DURATION_MS = 20  # Frame duration in milliseconds

def process_audio_file(audio_filename):
    try:
        # Read and process audio file
        wav_data = tf.audio.decode_wav(tf.io.read_file(audio_filename), desired_channels=1)
        waveform = wav_data.audio

        if len(waveform.shape) > 1:
            waveform = tf.squeeze(waveform, axis=-1)

        waveform = tf.cast(waveform, tf.float32)

        # Segment audio for processing
        results = []
        transcription_start_time = time.time()

        # Detect non-verbal sounds in the segment
        non_verbal_results = detect_non_verbal(waveform)
        results.extend(non_verbal_results)

        # Initialize pause detection variables
        start_time = time.time()
        last_activity_time = start_time
        last_pause_start = None

        # Detect pauses in the segment
        for i, score in enumerate(non_verbal_results):
            current_time = time.time() - start_time
            is_speech = score['event'] == 'speech' or score['event'] in class_names

            if is_speech:
                last_activity_time = time.time()
                if last_pause_start is not None:
                    results.append({
                        "start_timestamp": round(last_pause_start, 2),
                        "end_timestamp": round(current_time, 2),
                        "event": "pause"
                    })
                    last_pause_start = None
            else:
                if last_pause_start is None and (time.time() - last_activity_time) > 0.5:
                    last_pause_start = current_time

        # Transcribe the audio
        transcription_result = transcribe_audio(audio_filename)
        transcription_end_time = time.time()
        transcription_duration = transcription_end_time - transcription_start_time
        print(f"Transcription completed in {transcription_duration:.2f} seconds")

        for segment in transcription_result['segments']:
            if segment['text'].strip():
                results.append({
                    "start_timestamp": round(segment['start'], 2),
                    "end_timestamp": round(segment['end'], 2),
                    "event": "speech",
                    "transcription": segment['text'],
                    "words": len(segment['text'].split())
                })

        results.sort(key=lambda x: x['start_timestamp'])
        print(results)
        #Save results to a JSON file
        # json_filename = "utterance_test.json"
        # with open(json_filename, "w") as f:
        #     json.dump(results, f, indent=4)

        # print(f"Results saved to {json_filename}")

        # Send the transcriptions to the existing server
        send_transcriptions_to_server(results)

        # Remove the audio file after processing
        #os.remove(audio_filename)

        return results

    except Exception as e:
        print(f"Error processing audio file: {e}")
        return []

def transcribe_audio(audio_filename):
    try:
        result = model.transcribe(audio_filename)
        return result
    except Exception as e:
        print(f"Error during transcription: {e}")
        return {"segments": []}

def detect_non_verbal(waveform):
    results = []
    try:
        scores, embeddings, spectrogram = yamnet_model(waveform)
        human_sounds = [
            "Speech", "Child speech, kid speaking", "Babbling", "Shout", "Bellow", "Whoop", "Yell", "Screaming",
            "Whispering", "Laughter", "Baby laughter", "Giggle", "Snicker", "Belly laugh", "Chuckle, chortle",
            "Crying, sobbing", "Whimper", "Wail, moan", "Sigh", "Singing", "Choir", "Yodeling", "Chant", "Mantra",
            "Humming", "Groan", "Grunt", "Whistling", "Breathing", "Wheeze", "Snoring", "Gasp", "Pant", "Snort",
            "Cough", "Throat clearing", "Sneeze", "Sniff", "Cheering", "Hubbub, speech noise, speech babble"
        ]

        for i, score in enumerate(scores):
            timestamp = i * 0.5
            top_class = np.argmax(score)
            class_name = class_names[top_class]
            confidence = score[top_class]

            if class_name in human_sounds and confidence > 0.8:
                results.append({
                    "start_timestamp": round(timestamp, 2),
                    "end_timestamp": round(timestamp + 0.5, 2),
                    "event": class_name,
                    "confidence": float(confidence)
                })
                print(f"Detected non-verbal sound: {class_name} with confidence {confidence:.2f} at {timestamp:.2f}s")

    except Exception as e:
        print(f"Error detecting non-verbal sounds: {e}")

    return results

def send_transcriptions_to_server(transcriptions):
    """
    Send the transcriptions to the existing FastAPI server.
    """
    try:
        url = "http://127.0.0.1:8000/update-utterances"  # Replace with your actual endpoint
        response = requests.post(url, json=transcriptions)
        if response.status_code != 200:
            print(f"Failed to send transcriptions. Server response: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error sending transcriptions to the server: {e}")

# Example usage
audio_filename = "D:\\HCI_Research\\ManaliTests\\samples\\audio_1.wav"
if os.path.exists(audio_filename):
    process_audio_file(audio_filename)
else:
    print("Audio file not found.")
