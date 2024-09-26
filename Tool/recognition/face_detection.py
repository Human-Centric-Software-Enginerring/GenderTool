import cv2
import time
import json
from deepface import DeepFace
import threading
import aiohttp
import asyncio

class FaceDetection:
    def __init__(self):
        self.emotions = []
        self.running = False

    async def gather_emotion(self):
        cap = cv2.VideoCapture(0)  # Open the video stream
        previous_emotion = None
        start_time = time.time()  # Record the start time of the entire detection process
        emotion_start_time = None  # Track when the current emotion started

        try:
            while self.running:
                # Check if 5 minutes have passed
                if time.time() - start_time > 30:  # 300 seconds = 5 minutes
                    await self.send_data_to_api()
                    self.stop()
                    # self.reset_state()  # Reset the emotions
                    # start_time = time.time()  # Reset the start time for the next batch

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
                    confidence = result[0]["emotion"][emotion]

                    # If the emotion changes, record the end time for the previous emotion
                    if emotion != previous_emotion and confidence > 50:
                        if previous_emotion is not None and emotion_start_time is not None:
                            emotion_end_time = time.time() - start_time
                            self.emotions.append({
                                "emotion": previous_emotion,
                                "start_timestamp": f"{emotion_start_time:.2f}",
                                "end_timestamp": f"{emotion_end_time:.2f}"
                            })

                        # Record the start time for the new emotion
                        emotion_start_time = time.time() - start_time

                    previous_emotion = emotion

                resized_frame = cv2.resize(frame, (640, 480))
                if previous_emotion:
                    cv2.putText(resized_frame, f"Emotion: {previous_emotion}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                cv2.imshow('Face Detection', resized_frame)

                # Exit loop if 'q' is pressed
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            # After exiting, ensure the last emotion's end time is recorded
            if previous_emotion is not None and emotion_start_time is not None:
                emotion_end_time = time.time() - start_time
                self.emotions.append({
                    "emotion": previous_emotion,
                    "start_timestamp": f"{emotion_start_time:.2f}",
                    "end_timestamp": f"{emotion_end_time:.2f}"
                })

            await self.send_data_to_api()
            cap.release()
            cv2.destroyAllWindows()

        except KeyboardInterrupt:
            cap.release()
            cv2.destroyAllWindows()

    async def send_data_to_api(self):
        # Validate the data format before sending
        data = [{"emotion": e["emotion"], "start_timestamp": e["start_timestamp"], "end_timestamp": e["end_timestamp"]} for e in self.emotions]
        if not data:
            print("No emotion data to send")
            return

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post("http://127.0.0.1:8000/update-emotions", json=data) as response:
                    if response.status == 200:
                        print(f"Emotion data successfully sent: {data}")
                    else:
                        print(f"Failed to send emotion data. Status code: {response.status}")
        except Exception as e:
            print(f"Failed to send emotion data to API: {e}")

    def reset_state(self):
        self.emotions = []

    def collect(self):
        return self.emotions

    def start(self):
        self.running = True
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.gather_emotion())

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

        # Print collected emotions if needed
        emotions = face_detection.collect()
        print(f"Collected emotions: {emotions}")

    except KeyboardInterrupt:
        face_detection.stop()
        detection_thread.join()
        print("Face detection stopped.")
