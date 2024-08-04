import time
import asyncio
import cv2
from deepface import DeepFace

class FaceDetection:
    emotions = []
    running = False

    async def gather_emotion(self):
        # Open the video stream once connected
        cap = cv2.VideoCapture(0)

        previous_emotion = None
        try:
            while self.running:
                # Read each frame from the video stream
                ret, frame = cap.read()
                if not ret:
                    continue
                # Detect faces in the frame
                result = DeepFace.analyze(
                    img_path=frame,
                    actions=["emotion"],
                    enforce_detection=False,
                    silent=True,
                )
                if result and 'dominant_emotion' in result[0]:
                    emotion = result[0]["dominant_emotion"]
                    if emotion != previous_emotion:
                        print(f"Detected emotion: {emotion}")
                        self.emotions.append(
                            {"emotion": emotion, "timestamp": time.time() * 1000}
                        )
                    previous_emotion = emotion

                time.sleep(0.5)
                cv2.imshow('Face Detection', frame)

                # Exit loop if 'q' is pressed
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            cap.release()
            cv2.destroyAllWindows()
        
        except KeyboardInterrupt:
            cap.release()
            cv2.destroyAllWindows()

    def reset_state(self):
        self.emotions = []

    def collect(self):
        return self.emotions

    def start(self):
        self.running = True
        asyncio.run(self.gather_emotion())
    
    def stop(self):
        self.running = False

# Example usage
if __name__ == "__main__":
    face_detection = FaceDetection()
    
    # Start face detection in a separate thread
    import threading
    detection_thread = threading.Thread(target=face_detection.start)
    detection_thread.start()
    
    try:
        while True:
            # Check for user input to stop the detection
            command = input("Enter 'stop' to stop face detection and see collected emotions: ").strip().lower()
            if command == 'stop':
                face_detection.stop()
                detection_thread.join()  # Wait for the detection thread to finish
                emotions = face_detection.collect()
                print(f"Collected emotions: {emotions}")
                break
    
    except KeyboardInterrupt:
        face_detection.stop()
        detection_thread.join()
        print("Face detection stopped.")
