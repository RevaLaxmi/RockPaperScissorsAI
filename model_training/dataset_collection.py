import cv2
import mediapipe as mp
import numpy as np
import os

# Initialize Mediapipe Hand module
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)

# Define gestures
GESTURES = ["Rock", "Paper", "Scissors"]
DATASET_PATH = "gesture_data"  # Folder to save data
SEQUENCE_LENGTH = 30  # Number of frames per sample

# Create dataset directory
if not os.path.exists(DATASET_PATH):
    os.makedirs(DATASET_PATH)
    for gesture in GESTURES:
        os.makedirs(os.path.join(DATASET_PATH, gesture))

# Start video capture
cap = cv2.VideoCapture(0)

current_gesture = 0  # Index for gesture
recording = False  # Flag to control recording
sequence = []  # Stores frames of hand landmarks
sample_count = 0  # Number of recorded samples

print("Press 'r' to start/stop recording and 'n' to switch gestures")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    
    frame = cv2.flip(frame, 1)  # Flip frame for mirror effect
    image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(image_rgb)
    
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            # Extract 21 hand landmarks
            landmarks = []
            for lm in hand_landmarks.landmark:
                landmarks.extend([lm.x, lm.y, lm.z])  # Flattened landmark positions
            
            if recording:
                sequence.append(landmarks)
                if len(sequence) == SEQUENCE_LENGTH:
                    np.save(os.path.join(DATASET_PATH, GESTURES[current_gesture], f"sample_{sample_count}.npy"), sequence)
                    print(f"Saved {GESTURES[current_gesture]} sample {sample_count}")
                    sample_count += 1
                    sequence = []  # Reset sequence
    
    # Display instructions
    cv2.putText(frame, f"Gesture: {GESTURES[current_gesture]}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    cv2.putText(frame, f"Samples: {sample_count}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    cv2.imshow("Hand Gesture Recorder", frame)
    key = cv2.waitKey(1) & 0xFF
    
    if key == ord('q'):  # Quit
        break
    elif key == ord('r'):  # Start/Stop recording
        recording = not recording
        print("Recording" if recording else "Stopped recording")
    elif key == ord('n'):  # Switch gestures
        current_gesture = (current_gesture + 1) % len(GESTURES)
        sample_count = 0
        sequence = []
        print(f"Switched to {GESTURES[current_gesture]}")

cap.release()
cv2.destroyAllWindows()
