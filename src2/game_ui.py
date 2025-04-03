# src2/game_ui.py
import cv2
import numpy as np

def display_start_screen():
    screen = np.zeros((500, 800, 3), dtype=np.uint8)
    text = "START GAME"
    cv2.putText(screen, text, (220, 250), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
    cv2.imshow("Rock Paper Scissors", screen)
    cv2.waitKey(0)


def display_game_screen(frame, player_frame, ai_move_img, player_move, ai_move, winner, player_score, ai_score):
    # Ensure AI image is correctly resized
    ai_move_img_resized = cv2.resize(ai_move_img, (250, 300))  # Resize AI move image to match UI box size

    # Position the player and AI images correctly
    frame[100:400, 50:350] = player_frame  # Player image (left side)
    frame[100:400, 450:700] = ai_move_img_resized  # AI image (right side)

    # Add score display at the bottom
    cv2.putText(frame, f"Score: You {player_score} - AI {ai_score}", (200, 380),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

    # Show current moves
    cv2.putText(frame, f"Your Move: {player_move}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.putText(frame, f"AI Move: {ai_move}", (450, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    # Show winner message
    cv2.putText(frame, f"Winner: {winner}", (250, 350), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)




def display_end_screen(winner):
    screen = np.zeros((500, 800, 3), dtype=np.uint8)
    text = "YOU WIN" if winner == "player" else "YOU LOSE"
    cv2.putText(screen, text, (220, 250), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
    cv2.putText(screen, "RESTART", (330, 350), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
    
    cv2.imshow("Rock Paper Scissors", screen)
    cv2.waitKey(0)
