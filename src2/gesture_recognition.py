def is_finger_extended(finger_tip, finger_mcp, wrist):
    """Check if the finger is extended (above a certain threshold from the wrist)."""
    return finger_tip.y < finger_mcp.y and abs(finger_tip.y - wrist.y) > 0.1  # Threshold for extension

def recognize_gesture(hand_landmarks):
    """Recognizes the player's hand gesture as 'rock', 'paper', or 'scissors'."""
    if not hand_landmarks or not hand_landmarks.landmark:
        return None
    
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
        return "rock"  # All fingers folded

    if index_extended and middle_extended and ring_extended and pinky_extended:
        return "paper"  # All fingers extended

    if index_extended and middle_extended and not ring_extended and not pinky_extended:
        return "scissors"  # Only index and middle fingers extended

    return "unknown"
