import cv2
from hand_tracking import HandTracker  # Detects hand
from gesture_recognition import recognize_gesture  # Identifies move
from ai_opponent import get_ai_move  # AI picks a move
from game_ui import display_game  # UI for results

def main():
    # Initialize hand tracker
    hand_tracker = HandTracker()

    # Start the game loop
    cap = cv2.VideoCapture(0)  # Open webcam
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        # Detect hand
        hand_landmarks = hand_tracker.track_hand(frame)
        
        if hand_landmarks:
            # Recognize the player's move
            player_move = recognize_gesture(hand_landmarks)
            
            if player_move:
                # AI picks a move
                ai_move = get_ai_move()
                
                # Display the moves and winner
                frame = display_game(frame, player_move, ai_move)

        # Show the updated frame
        cv2.imshow("Rock-Paper-Scissors AI", frame)
        
        # Press 'q' to exit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

