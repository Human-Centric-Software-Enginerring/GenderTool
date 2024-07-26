# import wave
# import pyaudio
# import whisper
# import webrtcvad
# import time
# import json
# import threading

# # Initialize Whisper model
# model = whisper.load_model("base")

# # Initialize WebRTC VAD
# vad = webrtcvad.Vad()
# vad.set_mode(1)

# # Audio recording parameters
# FORMAT = pyaudio.paInt16
# CHANNELS = 1
# RATE = 16000
# CHUNK = 1024

# # Initialize PyAudio
# audio = pyaudio.PyAudio()

# # Shared variable to stop recording
# stop_recording = False

# # Function to record audio
# def record_audio():
#     global stop_recording
#     stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
#     frames = []
#     results = []

#     print("Recording...")
#     start_time = time.time()
#     last_activity_time = start_time
#     frame_duration = 0.02  # 20 ms frames

#     while not stop_recording:
#         data = stream.read(CHUNK)
#         frames.append(data)

#         # Process audio frames of 20 ms length
#         num_frames = int(len(data) / (RATE * frame_duration))
#         for i in range(num_frames):
#             start = int(i * RATE * frame_duration)
#             end = start + int(RATE * frame_duration)
#             frame = data[start:end]

#             if len(frame) != int(RATE * frame_duration):
#                 continue  # Skip if the frame length is not exactly 20 ms

#             is_speech = vad.is_speech(frame, RATE)
#             current_time = time.time() - start_time
#             if is_speech:
#                 print(f"Speech detected at {current_time:.2f}s")
#                 last_activity_time = time.time()
#                 results.append({"timestamp": current_time, "event": "speech"})
#             else:
#                 # Detect pauses (silence longer than a threshold, e.g., 0.5 seconds)
#                 if time.time() - last_activity_time > 0.5:
#                     print(f"Pause detected at {current_time:.2f}s")
#                     last_activity_time = time.time()  # Reset the last activity time
#                     results.append({"timestamp": current_time, "event": "pause"})

#         # Break on specific key or condition
#         if time.time() - start_time > 30:  # Stop after 60 seconds
#             stop_recording = False
#             break

#     print("Recording stopped.")

#     stream.stop_stream()
#     stream.close()

#     return frames, results

# # Function to save audio to a file
# def save_audio(frames, rate, output_filename="output.wav"):
#     wf = wave.open(output_filename, 'wb')
#     wf.setnchannels(CHANNELS)
#     wf.setsampwidth(audio.get_sample_size(FORMAT))
#     wf.setframerate(rate)
#     wf.writeframes(b''.join(frames))
#     wf.close()

# # Function to transcribe audio using Whisper
# def transcribe_audio(audio_filename):
#     result = model.transcribe(audio_filename)
#     return result

# # Main function
# def main():
#     global stop_recording

#     # Start recording in a separate thread to allow for manual interruption
#     record_thread = threading.Thread(target=record_audio)
#     record_thread.start()

#     try:
#         while record_thread.is_alive():
#             time.sleep(0.1)
#     except KeyboardInterrupt:
#         print("Stopping recording...")
#         stop_recording = True
#         record_thread.join()

#     frames, results = record_audio()
#     save_audio(frames, RATE)

#     result = transcribe_audio("output.wav")

#     # Print the transcription with timestamps
#     for segment in result['segments']:
#         print(f"[{segment['start']:.2f}s - {segment['end']:.2f}s]: {segment['text']}")
#         results.append({"timestamp": segment['start'], "transcription": segment['text']})

#     # Save results to a JSON file
#     with open("transcription_results.json", "w") as f:
#         json.dump(results, f, indent=4)

#     print("Results saved to transcription_results.json")

# if __name__ == "__main__":
#     main()

import wave
import pyaudio
import whisper
import webrtcvad
import time
import json
import threading

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
                    results.append({"timestamp": current_time, "event": "speech"})
                else:
                    # Detect pauses (silence longer than a threshold, e.g., 0.5 seconds)
                    if time.time() - last_activity_time > 0.5:
                        print(f"Pause detected at {current_time:.2f}s")
                        last_activity_time = time.time()  # Reset the last activity time
                        results.append({"timestamp": current_time, "event": "pause"})

        # Save the current audio segment
        segment_filename = f"segment_{segment_counter}.wav"
        save_audio(frames, RATE, segment_filename)
        segment_counter += 1

        # Transcribe the current audio segment
        transcription_result = transcribe_audio(segment_filename)
        print("Transcription:")
        for segment in transcription_result['segments']:
            print(f"[{segment['start']:.2f}s - {segment['end']:.2f}s]: {segment['text']}")
            results.append({"timestamp": segment['start'], "transcription": segment['text']})

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
