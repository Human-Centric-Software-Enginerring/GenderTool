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
def record_audio(segment_duration=30):
    global stop_recording
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    segment_counter = 0

    print("Recording...")
    while not stop_recording:
        frames = []
        results = []
        start_time = time.time()
        last_activity_time = start_time
        last_pause_start = None
        frame_duration = 0.02  # 20 ms frames

        while time.time() - start_time < segment_duration:
            data = stream.read(CHUNK)
            frames.append(data)

            # Process audio frames of 20 ms length
            num_frames = int(len(data) / (RATE * frame_duration))
            for i in range(num_frames):
                start = int(i * RATE * frame_duration)
                end = start + int(RATE * frame_duration)
                frame = data[start:end]

                if len(frame) != int(RATE * frame_duration):
                    continue  # Skip if the frame length is not exactly 20 ms

                is_speech = vad.is_speech(frame, RATE)
                current_time = time.time() - start_time
                if is_speech:
                    print(f"Speech detected at {current_time:.2f}s")
                    last_activity_time = time.time()
                    if last_pause_start is not None:
                        # Record the pause
                        pause_end_time = current_time
                        results.append({
                            "start_timestamp": last_pause_start,
                            "end_timestamp": pause_end_time,
                            "event": "pause"
                        })
                        last_pause_start = None
                else:
                    # Detect pauses (silence longer than a threshold, e.g., 0.5 seconds)
                    if time.time() - last_activity_time > 0.5:
                        if last_pause_start is None:
                            last_pause_start = current_time  # Mark the start of the pause

        # Handle case where recording ends and there was an ongoing pause
        if last_pause_start is not None:
            pause_end_time = time.time() - start_time
            results.append({
                "start_timestamp": last_pause_start,
                "end_timestamp": pause_end_time,
                "event": "pause"
            })

        # Save the current audio segment
        segment_filename = f"segment_{segment_counter}.wav"
        save_audio(frames, RATE, segment_filename)
        segment_counter += 1

        # Transcribe the current audio segment
        transcription_result = transcribe_audio(segment_filename)
        for segment in transcription_result['segments']:
            if segment['text'].strip():  # Only include if there's actual transcription
                print(f"[{segment['start']:.2f}s - {segment['end']:.2f}s]: {segment['text']}")
                results.append({
                    "start_timestamp": segment['start'],
                    "end_timestamp": segment['end'],
                    "event": "speech",
                    "transcription": segment['text']
                })

        # Detect non-verbal sounds (e.g., laughter) in the segment
        non_verbal_results = detect_non_verbal(segment_filename)
        results.extend(non_verbal_results)

        # Save transcription results to a JSON file
        json_filename = f"transcription_results_{segment_counter}.json"
        with open(json_filename, "w") as f:
            json.dump(results, f, indent=4)

        print(f"Results saved to {json_filename}")

    print("Recording stopped.")
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

# Function to detect non-verbal sounds (e.g., laughter) using YAMNet
def detect_non_verbal(audio_filename):
    results = []

    # Load the audio file and ensure it's mono-channel
    wav_data = tf.audio.decode_wav(tf.io.read_file(audio_filename), desired_channels=1)
    waveform = wav_data.audio

    # Ensure waveform is 1D and reshape if necessary
    if len(waveform.shape) > 1:
        waveform = tf.squeeze(waveform, axis=-1)
    
    # Convert to float32 and normalize if needed
    waveform = tf.cast(waveform, tf.float32)
    
    # Predict using YAMNet
    scores, embeddings, spectrogram = yamnet_model(waveform)

    # Analyze the scores to detect laughter or other non-verbal sounds
    for i, score in enumerate(scores):
        timestamp = i * 0.5  # Assuming 0.5s per score segment
        top_class = np.argmax(score)
        class_name = class_names[top_class]
        
        if class_name == 'Laughter':
            print(f"Laughter detected at {timestamp:.2f}s")
            results.append({"timestamp": timestamp, "event": "laughter"})
        elif class_name == 'Non-verbal speech':
            print(f"Non-verbal speech detected at {timestamp:.2f}s")
            results.append({"timestamp": timestamp, "event": "non-verbal"})

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
        print("Stopping recording...")
        stop_recording = True
        record_thread.join()

    audio.terminate()

if __name__ == "__main__":
    main()
