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
class_map_path = r"D://HCI_Research//GenderTool//Tool//recognition//yamnet_class_map.csv"
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

# Function to record audio
def record_audio(duration=30):  # 5 minutes in seconds
    global stop_recording
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    frames = []
    results = []
    start_time = time.time()

    print("Recording...")
    while not stop_recording:
        try:
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
                    #print(f"Speech detected at {current_time:.2f}s")
                    last_activity_time = time.time()
                    if 'last_pause_start' in locals():
                        # Record the pause
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

            # Check if 5 minutes have passed
            if time.time() - start_time >= duration:
                break
        except Exception as e:
            print(f"Exception occurred in recording thread: {e}")

    # Handle case where recording ends and there was an ongoing pause
    if 'last_pause_start' in locals():
        results.append({
            "start_timestamp": round(last_pause_start, 2),
            "end_timestamp": round(time.time() - start_time, 2),
            "event": "pause"
        })

    # Save the current audio segment
    segment_filename = "full_recording.wav"
    save_audio(frames, RATE, segment_filename)

    # Measure time for transcription
    transcription_start_time = time.time()
    
    # Transcribe the audio
    transcription_result = transcribe_audio(segment_filename)
    
    transcription_end_time = time.time()
    transcription_duration = transcription_end_time - transcription_start_time
    print(f"Transcription completed in {transcription_duration:.2f} seconds")

    for segment in transcription_result['segments']:
        if segment['text'].strip():  # Only include if there's actual transcription
            results.append({
                "start_timestamp": round(segment['start'], 2),
                "end_timestamp": round(segment['end'], 2),
                "event": "speech",
                "transcription": segment['text']
            })

    # Detect non-verbal sounds in the segment
    non_verbal_results = detect_non_verbal(segment_filename)
    results.extend(non_verbal_results)

    # Sort results by start_timestamp (which should be float)
    #print(results)
    results.sort(key=lambda x: x['start_timestamp'])

    # Save results to a JSON file
    json_filename = "utterance_data.json"
    with open(json_filename, "w") as f:
        json.dump(results, f, indent=4)

    print(f"Results saved to {json_filename}")

    # Remove the audio file after transcription
    os.remove(segment_filename)
    print(f"Deleted {segment_filename}")

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
    result = model.transcribe(audio_filename)
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

    for i, score in enumerate(scores):
        timestamp = i * 0.5  # Assuming 0.5s per score segment
        top_class = np.argmax(score)
        class_name = class_names[top_class]

        if class_name != 'display_name':
            results.append({
                "start_timestamp": round(timestamp, 2),
                "end_timestamp": round(timestamp + 0.5, 2),
                "event": class_name
            })

    return results

# Main function
def main():
    global stop_recording

    # Start recording in a separate thread to allow for manual interruption
    record_thread = threading.Thread(target=record_audio)
    record_thread.start()

    try:
        while record_thread.is_alive():
            time.sleep(0.1)
    except KeyboardInterrupt:
        #print("Stopping recording...")
        stop_recording = True
        record_thread.join()

    audio.terminate()

if __name__ == "__main__":
    main()
