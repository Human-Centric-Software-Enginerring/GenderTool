import wave
import pyaudio
import whisper
import webrtcvad
import time
import json
import threading
import numpy as np

# Initialize Whisper model
model = whisper.load_model("base")

# Initialize WebRTC VAD
vad = webrtcvad.Vad()
vad.set_mode(1)

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
def record_audio():
    global stop_recording
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    frames = []
    results = []

    print("Recording...")
    start_time = time.time()
    last_activity_time = start_time

    while not stop_recording:
        data = stream.read(CHUNK)
        frames.append(data)

        # Convert data to numpy array for VAD
        audio_data = np.frombuffer(data, dtype=np.int16)
        
        # WebRTC VAD expects frames of 320 samples (16 ms at 16 kHz)
        if len(audio_data) == 320:
            is_speech = vad.is_speech(audio_data.tobytes(), RATE)
            current_time = time.time() - start_time
            if is_speech:
                print(f"Speech detected at {current_time:.2f}s")
                last_activity_time = time.time()
                results.append({"timestamp": current_time, "event": "speech"})
            else:
                if time.time() - last_activity_time > 0.5:
                    print(f"Pause detected at {current_time:.2f}s")
                    last_activity_time = time.time()
                    results.append({"timestamp": current_time, "event": "pause"})

        # Stop after 60 seconds
        if time.time() - start_time > 60:
            break

    print("Recording stopped.")

    stream.stop_stream()
    stream.close()

    return frames, results

# Function to save audio to a file
def save_audio(frames, rate, output_filename="output.wav"):
    with wave.open(output_filename, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(rate)
        wf.writeframes(b''.join(frames))

# Function to transcribe audio using Whisper
def transcribe_audio(audio_filename):
    try:
        result = model.transcribe(audio_filename)
        return result
    except Exception as e:
        print(f"Error during transcription: {e}")
        return {"segments": []}

# Main function
def main():
    global stop_recording

    # Start recording in a separate thread
    record_thread = threading.Thread(target=record_audio)
    record_thread.start()

    try:
        while record_thread.is_alive():
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Stopping recording...")
        stop_recording = True
        record_thread.join()  # Ensure the recording thread stops

    # Once recording is stopped, process the audio
    frames, results = record_audio()
    save_audio(frames, RATE)

    result = transcribe_audio("output.wav")

    # Print the transcription with timestamps
    for segment in result.get('segments', []):
        print(f"[{segment['start']:.2f}s - {segment['end']:.2f}s]: {segment['text']}")
        results.append({"timestamp": segment['start'], "transcription": segment['text']})

    # Save results to a JSON file
    with open("transcription_results.json", "w") as f:
        json.dump(results, f, indent=4)

    print("Results saved to transcription_results.json")

if __name__ == "__main__":
    main()
