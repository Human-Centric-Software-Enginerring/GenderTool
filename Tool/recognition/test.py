# import pandas as pd

# # Use pandas to read the class map file
# class_map_path = r"D://HCI_Research//GenderTool//Tool//recognition//yamnet_class_map.csv"
# df = pd.read_csv(class_map_path, header=None)
# class_names = df[2].values  # Adjust column index if necessary

# # Print class names to verify
# print("Class names loaded from the class map:")
# print(class_names)

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

def detect_non_verbal(audio_filename):
    results = []

    # Load the audio file
    wav_data = tf.audio.decode_wav(tf.io.read_file(audio_filename), desired_channels=1)
    waveform = wav_data.audio

    # Flatten the waveform to remove the batch dimension
    waveform = tf.squeeze(waveform)  # Remove any singleton dimensions (shape: [num_samples])

    # Ensure waveform is a 1D tensor of shape (num_samples,)
    print(f"Waveform shape: {waveform.shape}")
    class_map_path = r"D://HCI_Research//GenderTool//Tool//recognition//yamnet_class_map.csv"
    df = pd.read_csv(class_map_path, header=None)
    class_names = df[2].values
    # Predict using YAMNet
    try:
        scores, embeddings, spectrogram = yamnet_model(waveform)
        print(f"Scores shape: {scores.shape}")
        print(f"Embeddings shape: {embeddings.shape}")
        print(f"Spectrogram shape: {spectrogram.shape}")
        print("First few scores:", scores[:5])
        print("First few class names:", class_names[:10])
    except TypeError as e:
        print(f"Error during YAMNet prediction: {e}")
        return results


    # Analyze the scores to detect laughter or other non-verbal sounds
    for i, score in enumerate(scores[0]):  # Iterate over the scores for each frame
        timestamp = i * 0.5  # Assuming 0.5s per score segment
        top_class = np.argmax(score)
        class_name = class_names[top_class]
        if class_name == 'Laughter':
            print(f"Laughter detected at {timestamp:.2f}s")
            results.append({"timestamp": timestamp, "event": "laughter"})
        elif class_name == 'Non-verbal speech':
            print(f"Non-verbal speech detected at {timestamp:.2f}s")
            results.append({"timestamp": timestamp, "event": "non-verbal speech"})

    return results

results  = detect_non_verbal('segment_0.wav')
print(results)