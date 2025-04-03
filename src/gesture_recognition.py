import cv2
import mediapipe as mp
import numpy as np

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.8, min_tracking_confidence=0.8)

# Function to determine if a finger is extended
def is_finger_extended(finger_tip, finger_mcp, wrist):
    """Check if the finger is extended (above a certain threshold from the wrist)."""
    return finger_tip.y < finger_mcp.y and abs(finger_tip.y - wrist.y) > 0.1  # Threshold for extension

# Function to detect the gesture
def recognize_gesture(hand_landmarks):
    landmarks = hand_landmarks.landmark

    # Finger Landmarks
    thumb_tip = landmarks[4]
    index_tip = landmarks[8]
    middle_tip = landmarks[12]
    ring_tip = landmarks[16]
    pinky_tip = landmarks[20]

    index_mcp = landmarks[5]  # Base of index finger
    middle_mcp = landmarks[9]  # Base of middle finger
    ring_mcp = landmarks[13]
    pinky_mcp = landmarks[17]
    wrist = landmarks[0]  # Wrist

    # Check which fingers are extended
    index_extended = is_finger_extended(index_tip, index_mcp, wrist)
    middle_extended = is_finger_extended(middle_tip, middle_mcp, wrist)
    ring_extended = is_finger_extended(ring_tip, ring_mcp, wrist)
    pinky_extended = is_finger_extended(pinky_tip, pinky_mcp, wrist)

    # Gesture classification
    if not index_extended and not middle_extended and not ring_extended and not pinky_extended:
        return "Rock ✊"  # All fingers folded

    if index_extended and middle_extended and ring_extended and pinky_extended:
        return "Paper ✋"  # All fingers extended

    if index_extended and middle_extended and not ring_extended and not pinky_extended:
        return "Scissors ✌️"  # Only index and middle fingers extended

    return "Unknown"

# Start webcam
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Flip frame horizontally for mirror effect
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process the frame
    results = hands.process(rgb_frame)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Draw landmarks
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Recognize gesture
            gesture = recognize_gesture(hand_landmarks)

            # Display gesture text
            cv2.putText(frame, gesture, (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)

    # Show the webcam feed
    cv2.imshow("Rock Paper Scissors", frame)

    # Press 'q' to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
