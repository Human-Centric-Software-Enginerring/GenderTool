import cv2
import time
from deepface import DeepFace
import threading
import requests  # Import requests library for sending data to the API

class FaceDetection:
    def __init__(self):
        self.emotions = []
        self.running = False
        self.video_file = "D:\\HCI_Research\\ManaliTests\\samples\\video_1.mp4"
        self.frame_skip = 10
        self.resize_width = 640
        self.resize_height = 480
        self.lock = threading.Lock()  # Thread safety lock

    def gather_emotion(self):
        cap = cv2.VideoCapture(self.video_file)
        if not cap.isOpened():
            print(f"Error: Unable to open video file {self.video_file}")
            return
        
        previous_emotion = None
        start_time = time.time()
        emotion_start_time = None
        frame_count = 0

        try:
            while self.running:
                if not cap.isOpened() or time.time() - start_time > 60:
                    break

                ret, frame = cap.read()
                if not ret:
                    print("Error: Failed to read frame from video.")
                    break
                
                frame_count += 1
                if frame_count % self.frame_skip != 0:
                    continue

                current_time = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
                result = DeepFace.analyze(frame, actions=["emotion"], enforce_detection=False, silent=True)

                if result and 'dominant_emotion' in result[0]:
                    emotion = result[0]["dominant_emotion"]
                    confidence = result[0]["emotion"][emotion]
                    #print(f"Detected emotion: {emotion} with confidence: {confidence:.2f}")

                    with self.lock:  # Ensure thread-safe access
                        if emotion != previous_emotion and confidence > 50:
                            if previous_emotion is not None and emotion_start_time is not None:
                                emotion_end_time = current_time
                                self.emotions.append({
                                    "emotion": previous_emotion,
                                    "start_timestamp": emotion_start_time,
                                    "end_timestamp": emotion_end_time
                                })
                                #print(f"Appended emotion data: {previous_emotion}")
                            emotion_start_time = current_time
                        previous_emotion = emotion

                resized_frame = cv2.resize(frame, (self.resize_width, self.resize_height))
                if previous_emotion:
                    cv2.putText(resized_frame, f"Emotion: {previous_emotion}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                cv2.imshow('Face Detection', resized_frame)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            # After exiting, ensure the last emotion's end time is recorded
            if previous_emotion is not None and emotion_start_time is not None:
                emotion_end_time = current_time
                self.emotions.append({
                    "emotion": previous_emotion,
                    "start_timestamp": f"{emotion_start_time:.2f}",
                    "end_timestamp": f"{emotion_end_time:.2f}"
                })
            # After processing, send the collected emotions to the API
            self.send_data_to_api()
        
        except KeyboardInterrupt:
            pass
        finally:
            cap.release()
            cv2.destroyAllWindows()

    def send_data_to_api(self):
        # Validate the data format before sending
        data = [{"emotion": e["emotion"], "start_timestamp": e["start_timestamp"], "end_timestamp": e["end_timestamp"]} for e in self.emotions]
        #print(f"Sending data: {data}")  # Debug print to verify data
        if not data:
            print("No emotion data to send")
        try:
            response = requests.post("http://127.0.0.1:8000/update-emotions", json=data)
            #print(f"Emotion data sent to API: {response.status_code}")
            #print(f"Response content: {response.json()}")  # Print response content for debugging
        except Exception as e:
            print(f"Failed to send emotion data to API: {e}")

    def reset_state(self):
        with self.lock:  # Ensure thread-safe access
            self.emotions = []

    def collect(self):
        with self.lock:  # Ensure thread-safe access
            return self.emotions

    def start(self):
        self.running = True
        self.gather_emotion()
    
    def stop(self):
        self.running = False

# Example usage
if __name__ == "__main__":
    face_detection = FaceDetection()
    face_detection.start()
    # Later in the code or based on some condition
    face_detection.stop()

