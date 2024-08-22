import cv2
import time
import json
from deepface import DeepFace
import threading

class FaceDetection:
    def __init__(self):
        self.emotions = []
        self.running = False

    def gather_emotion(self):
        # Open the video stream
        cap = cv2.VideoCapture(0)
        previous_emotion = None
        start_time = time.time()  # Record the start time of the entire detection process
        emotion_start_time = None  # Track when the current emotion started

        try:
            while self.running:
                # Check if 5 minutes have passed
                if time.time() - start_time > 30:
                    break

                # Read each frame from the video stream
                ret, frame = cap.read()
                if not ret:
                    continue

                # Detect faces and emotions in the frame
                result = DeepFace.analyze(
                    img_path=frame,
                    actions=["emotion"],
                    enforce_detection=False,
                    silent=True,
                )
                
                if result and 'dominant_emotion' in result[0]:
                    emotion = result[0]["dominant_emotion"]
                    
                    # If the emotion changes, record the end time for the previous emotion
                    if emotion != previous_emotion:
                        if previous_emotion is not None and emotion_start_time is not None:
                            emotion_end_time = time.time() - start_time
                            self.emotions.append({
                                "emotion": previous_emotion,
                                "start_timestamp": f"{emotion_start_time:.2f} sec",
                                "end_timestamp": f"{emotion_end_time:.2f} sec"
                            })
                        
                        # Record the start time for the new emotion
                        emotion_start_time = time.time() - start_time
                        print(f"Detected emotion: {emotion} at {emotion_start_time:.2f} sec")
                    
                    previous_emotion = emotion

                time.sleep(0.5)
                cv2.imshow('Face Detection', frame)

                # Exit loop if 'q' is pressed
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            # After exiting, ensure the last emotion's end time is recorded
            if previous_emotion is not None and emotion_start_time is not None:
                emotion_end_time = time.time() - start_time
                self.emotions.append({
                    "emotion": previous_emotion,
                    "start_timestamp": f"{emotion_start_time:.2f} sec",
                    "end_timestamp": f"{emotion_end_time:.2f} sec"
                })
            
            cap.release()
            cv2.destroyAllWindows()
        
        except KeyboardInterrupt:
            cap.release()
            cv2.destroyAllWindows()

    def reset_state(self):
        self.emotions = []

    def collect(self):
        return self.emotions

    def save_to_file(self, filename='face_detection_data.json'):
        with open(filename, 'w') as f:
            json.dump(self.emotions, f, indent=4)

    def start(self):
        self.running = True
        self.gather_emotion()
    
    def stop(self):
        self.running = False

# Example usage
if __name__ == "__main__":
    face_detection = FaceDetection()
    
    # Start face detection in a separate thread
    detection_thread = threading.Thread(target=face_detection.start)
    detection_thread.start()
    
    try:
        # Wait for the detection to finish automatically
        detection_thread.join()
        emotions = face_detection.collect()
        #print(f"Collected emotions: {emotions}")
        face_detection.save_to_file()  # Save emotions to file
    
    except KeyboardInterrupt:
        face_detection.stop()
        detection_thread.join()
        print("Face detection stopped.")