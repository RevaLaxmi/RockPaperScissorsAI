import cv2
import numpy as np
import os
import time
from hand_tracking_module import extract_keypoints_from_frame

# Setup
ACTIONS = ['rock', 'paper', 'scissors', 'nothing']
SEQUENCE_LENGTH = 30
DATA_PATH = os.path.join('gesture_data2')  # Save location

# Automatically create directories
for action in ACTIONS:
    os.makedirs(os.path.join(DATA_PATH, action), exist_ok=True)

cap = cv2.VideoCapture(0)
current_action = 0
sample_count = 0

print("Starting data collection.")
print("Press 'n' to switch gesture. Press 'q' to quit.")

sequence = []

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Flip for mirror effect & convert color
    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    keypoints = extract_keypoints_from_frame(rgb)

    # Display info
    action_text = f"Collecting: {ACTIONS[current_action]} | Sample {sample_count}"
    cv2.putText(frame, action_text, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    if keypoints is not None:
        sequence.append(keypoints)
        if len(sequence) == SEQUENCE_LENGTH:
            filename = os.path.join(DATA_PATH, ACTIONS[current_action], f"{int(time.time())}.npy")
            np.save(filename, np.array(sequence))
            sample_count += 1
            sequence = []  # Reset

    # Show frame
    cv2.imshow("Collecting Data", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('n'):
        current_action = (current_action + 1) % len(ACTIONS)
        sample_count = 0
        print(f"Switched to: {ACTIONS[current_action]}")

cap.release()
cv2.destroyAllWindows()
