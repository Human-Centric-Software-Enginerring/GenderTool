import wave
import pyaudio
import whisper
import webrtcvad
import time
import json
import threading
import tensorflow as tf
import tensorflow_hub as hub
import numpy as np
import requests
import pandas as pd
import os

# Initialize Whisper model
model = whisper.load_model("base")

# Initialize WebRTC VAD
vad = webrtcvad.Vad()
vad.set_mode(1)

# Initialize YAMNet model from TensorFlow Hub
yamnet_model = hub.load('https://tfhub.dev/google/yamnet/1')

# Load class map
class_map_path = "D://HCI_Research//GenderTool//Tool//recognition//yamnet_class_map.csv"
df = pd.read_csv(class_map_path, header=None)
class_names = df[2].values

# Audio recording parameters
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1024

# Initialize PyAudio
audio = pyaudio.PyAudio()

# Shared variable to stop recording
stop_recording = False
send_interval = 30  # 5 minutes in seconds

# Function to record audio
def record_audio():
    global stop_recording
    while not stop_recording:
        gather_audio_and_process(send_interval)

def gather_audio_and_process(duration):
    frames = []
    results = []
    start_time = time.time()

    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    print(f"Recording for {duration} seconds...")

    try:
        while time.time() - start_time < duration and not stop_recording:
            data = stream.read(CHUNK)
            frames.append(data)

            # Process audio frames of 20 ms length
            num_frames = int(len(data) / (RATE * 0.02))
            for i in range(num_frames):
                start = int(i * RATE * 0.02)
                end = start + int(RATE * 0.02)
                frame = data[start:end]

                if len(frame) != int(RATE * 0.02):
                    continue  # Skip if the frame length is not exactly 20 ms

                is_speech = vad.is_speech(frame, RATE)
                current_time = time.time() - start_time
                if is_speech:
                    last_activity_time = time.time()
                    if 'last_pause_start' in locals():
                        results.append({
                            "start_timestamp": round(last_pause_start, 2),
                            "end_timestamp": round(current_time, 2),
                            "event": "pause"
                        })
                        del last_pause_start
                else:
                    # Detect pauses (silence longer than a threshold, e.g., 0.5 seconds)
                    if 'last_activity_time' in locals() and time.time() - last_activity_time > 0.5:
                        if 'last_pause_start' not in locals():
                            last_pause_start = current_time  # Mark the start of the pause

        if 'last_pause_start' in locals():
            results.append({
                "start_timestamp": round(last_pause_start, 2),
                "end_timestamp": round(time.time() - start_time, 2),
                "event": "pause"
            })

        # Save the current audio segment
        segment_filename = "full_recording.wav"
        save_audio(frames, RATE, segment_filename)

        # Transcribe the audio
        transcription_result = transcribe_audio(segment_filename)
        for segment in transcription_result['segments']:
            if segment['text'].strip():
                results.append({
                    "start_timestamp": round(segment['start'], 2),
                    "end_timestamp": round(segment['end'], 2),
                    "event": "speech",
                    "transcription": segment['text'],
                    "words": len(segment['text'].split())
                })

        # Detect non-verbal sounds in the segment
        non_verbal_results = detect_non_verbal(segment_filename)
        results.extend(non_verbal_results)

        # Sort results by start_timestamp
        results.sort(key=lambda x: x['start_timestamp'])

        # Send the transcriptions to the server every 'x'seconds. Currently, 30 secs. 
        send_transcriptions_to_server(results)

        #write results to a file
        # with open('utterances_result.json', 'w') as f:
        #     json.dump(results, f, indent=4)

        # Remove the audio file after transcription
        os.remove(segment_filename)
        print(f"Deleted {segment_filename}")

    except Exception as e:
        print(f"Exception occurred during recording: {e}")
    finally:
        stream.stop_stream()
        stream.close()

# Function to save audio to a file
def save_audio(frames, rate, output_filename):
    wf = wave.open(output_filename, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(rate)
    wf.writeframes(b''.join(frames))
    wf.close()

# Function to transcribe audio using Whisper
def transcribe_audio(audio_filename):
    #result = model.transcribe(audio_filename)
    result = model.transcribe(audio_filename, language='en', beam_size=1)
    return result

# Function to detect non-verbal sounds using YAMNet
def detect_non_verbal(audio_filename):
    results = []
    wav_data = tf.audio.decode_wav(tf.io.read_file(audio_filename), desired_channels=1)
    waveform = wav_data.audio

    if len(waveform.shape) > 1:
        waveform = tf.squeeze(waveform, axis=-1)
    
    waveform = tf.cast(waveform, tf.float32)
    scores, embeddings, spectrogram = yamnet_model(waveform)
    human_sounds = [
            "Speech", "Child speech, kid speaking", "Babbling", "Shout", "Bellow", "Whoop", "Yell", "Screaming",
            "Whispering", "Laughter", "Baby laughter", "Giggle", "Snicker", "Belly laugh", "Chuckle, chortle",
            "Crying, sobbing", "Whimper", "Wail, moan", "Sigh", "Singing", "Choir", "Yodeling", "Chant", "Mantra",
            "Humming", "Groan", "Grunt", "Whistling", "Breathing", "Wheeze", "Snoring", "Gasp", "Pant", "Snort",
            "Cough", "Throat clearing", "Sneeze", "Sniff", "Cheering", "Hubbub, speech noise, speech babble"
        ]
    for i, score in enumerate(scores):
        timestamp = i * 0.5  # Assuming 0.5s per score segment
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

    return results

def send_transcriptions_to_server(transcriptions):
    """
    Send the transcriptions to the existing FastAPI server.
    """
    try:
        url = "http://127.0.0.1:8000/update-utterances"  
        response = requests.post(url, json=transcriptions)
        if response.status_code != 200:
            print(f"Failed to send transcriptions. Server response: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error sending transcriptions to the server: {e}")

# Main function
def main():
    global stop_recording

    # Start recording in a separate thread
    record_thread = threading.Thread(target=record_audio)
    record_thread.start()

    # Set a timer to stop the recording after 30 seconds
    stop_timer = threading.Timer(30, lambda: globals().__setitem__('stop_recording', True))
    stop_timer.start()

    try:
        while record_thread.is_alive():
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Stopping recording...")
        stop_recording = True
        record_thread.join()

    stop_timer.cancel()  # Cancel the timer if recording is stopped manually
    audio.terminate()

if __name__ == "__main__":
    main()
