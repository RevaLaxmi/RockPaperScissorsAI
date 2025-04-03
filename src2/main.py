import cv2
import numpy as np
from hand_tracking import HandTracker
from gesture_recognition import recognize_gesture
from ai_opponent import AI_Opponent
from game_ui import display_start_screen, display_game_screen, display_end_screen

def main():
    cap = cv2.VideoCapture(0)
    tracker = HandTracker()
    ai = AI_Opponent()
    
    last_player_move = None  # Store last move to detect changes
    ai_move = "Waiting..."
    winner = "Waiting..."
    player_score, ai_score = 0, 0
    game_over = False
    
    # Load AI move images
    move_images = {
        "Rock": cv2.imread("assets/rock.png"),
        "Paper": cv2.imread("assets/paper.png"),
        "Scissors": cv2.imread("assets/scissors.png"),
    }
    
    # Display start screen
    display_start_screen()
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Flip frame for a mirror effect
        frame = cv2.flip(frame, 1)
        
        # Detect hands
        hand_landmarks_list = tracker.detect(frame)
        
        if hand_landmarks_list:
            frame = tracker.draw_landmarks(frame, hand_landmarks_list)
            hand_landmarks = hand_landmarks_list[0]  # Use the first detected hand
            player_move = recognize_gesture(hand_landmarks)

            # Only get AI move if player changes move
            if player_move and player_move != last_player_move:
                ai_move, winner = ai.get_winner(player_move)
                last_player_move = player_move  # Update last move
                
                # Update scores
                if winner == "Player Wins":
                    player_score += 1
                elif winner == "AI Wins":
                    ai_score += 1
        else:
            player_move = "Waiting..."
            ai_move, winner = "Waiting...", "Waiting..."  # AI also resets
        
        # Select AI move image
        ai_move_img = move_images.get(ai_move, np.zeros((300, 300, 3), dtype=np.uint8))
        
        # Resize AI move image to match player frame size
        ai_move_img = cv2.resize(ai_move_img, (300, 300))
        
        # Check if the game is over (Best out of 5)
        if player_score == 3 or ai_score == 3:
            game_over = True
        
        if game_over:
            display_end_screen("player" if player_score == 3 else "ai")
            if cv2.waitKey(0) & 0xFF == ord('r'):  # Wait for restart command
                main()  # Restart the game
            else:
                break
        
        # Resize player camera feed
        player_frame = cv2.resize(frame, (300, 300))
        
        # Create a black background for the game screen
        game_screen = np.zeros((400, 700, 3), dtype=np.uint8)
        
        # Position player and AI images side by side
        game_screen[50:350, 50:350] = player_frame  # Player camera feed
        game_screen[50:350, 400:700] = ai_move_img  # AI move image
        
        # Display game screen with player and AI moves (FIXED CALL)
        display_game_screen(game_screen, player_frame, ai_move_img, player_move, ai_move, winner, player_score, ai_score)
        
        # Show the updated frame
        cv2.imshow("Rock Paper Scissors", game_screen)
        
        # Exit condition
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
