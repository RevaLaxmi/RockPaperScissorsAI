import cv2
import mediapipe as mp
import numpy as np
import random  # AI move selection

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.75, min_tracking_confidence=0.75)

# Possible AI moves
MOVES = ["Rock ✊", "Paper ✋", "Scissors ✌️"]

# Function to check if a finger is extended
def is_finger_extended(finger_tip, finger_mcp, wrist, threshold=0.08):
    return (finger_tip.y < finger_mcp.y) and (abs(finger_tip.y - wrist.y) > threshold)  # Slightly lowered threshold

# Function to recognize the player's hand gesture
def recognize_gesture(hand_landmarks):
    landmarks = hand_landmarks.landmark

    # Get key finger positions
    index_tip, index_mcp = landmarks[8], landmarks[5]
    middle_tip, middle_mcp = landmarks[12], landmarks[9]
    ring_tip, ring_mcp = landmarks[16], landmarks[13]
    pinky_tip, pinky_mcp = landmarks[20], landmarks[17]
    wrist = landmarks[0]

    # Check which fingers are extended
    index_extended = is_finger_extended(index_tip, index_mcp, wrist)
    middle_extended = is_finger_extended(middle_tip, middle_mcp, wrist)
    ring_extended = is_finger_extended(ring_tip, ring_mcp, wrist, threshold=0.1)  # Slightly different threshold
    pinky_extended = is_finger_extended(pinky_tip, pinky_mcp, wrist, threshold=0.1)

    # Classify the gesture
    if not index_extended and not middle_extended and not ring_extended and not pinky_extended:
        return "Rock ✊"
    if index_extended and middle_extended and ring_extended and pinky_extended:
        return "Paper ✋"
    if index_extended and middle_extended and not ring_extended and not pinky_extended:
        return "Scissors ✌️"

    return "Unknown"

# Function to determine the winner
def get_winner(player_move, ai_move):
    if player_move == ai_move:
        return "It's a Tie! 😐"
    if (player_move == "Rock ✊" and ai_move == "Scissors ✌️") or \
       (player_move == "Paper ✋" and ai_move == "Rock ✊") or \
       (player_move == "Scissors ✌️" and ai_move == "Paper ✋"):
        return "You Win! 🎉"
    return "AI Wins! 🤖"

# Start webcam
cap = cv2.VideoCapture(0)

# Variables to lock AI choice
last_player_move = None
ai_move = "🤔"
winner_text = ""
show_ai_move = False  # Flag to control when to show AI move

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Flip frame horizontally for mirror effect
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process the frame
    results = hands.process(rgb_frame)
    player_move = "Waiting..."

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Draw landmarks
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Recognize player's gesture
            recognized_move = recognize_gesture(hand_landmarks)

            # Only reset AI move if the player move is truly unknown for a while
            if recognized_move == "Unknown":
                player_move = last_player_move if last_player_move else "Waiting..."
            else:
                # If a valid move is detected, update AI choice
                if recognized_move != last_player_move:
                    ai_move = random.choice(MOVES)
                    last_player_move = recognized_move  # Lock player move
                    show_ai_move = True  # Now AI move can be revealed

                player_move = recognized_move
                winner_text = get_winner(player_move, ai_move) if show_ai_move else ""

    # Display game results
    cv2.putText(frame, f"Your Move: {player_move}", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    # AI Move only appears after player finalizes move, then disappears on next move
    if show_ai_move:
        cv2.putText(frame, f"AI Move: {ai_move}", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(frame, winner_text, (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)

    # Show the webcam feed
    cv2.imshow("Rock Paper Scissors - AI Opponent", frame)

    # Press 'q' to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
