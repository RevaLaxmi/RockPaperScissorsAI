import cv2
import numpy as np
from hand_tracking_module import extract_keypoints_from_frame
from ai_opponent_module import get_ai_move

# Load AI move images
ai_images = {
    "rock": cv2.imread("assets/rock2.png"),
    "paper": cv2.imread("assets/paper2.png"),
    "scissors": cv2.imread("assets/scissors2.png"),
    "nothing": np.zeros((300, 300, 3), dtype=np.uint8)
}

# Resize all images
for key in ai_images:
    ai_images[key] = cv2.resize(ai_images[key], (300, 300))

cap = cv2.VideoCapture(0)

SEQUENCE_LENGTH = 10
EARLY_PREDICTION_FRAMES = 5
STABILITY_FRAMES = 7

sequence, early_sequence = [], []
player_move, prev_move = "nothing", None
move_counter = 0

ai_move = "nothing"
ai_prediction_made = False
show_ai_now = False  # Flag to control AI image visibility

player_score, ai_score = 0, 0
last_result_text = ""
last_stable_move, last_ai_move = "", ""

def determine_winner(player, ai):
    if player == ai:
        return "draw"
    if (player == "rock" and ai == "scissors") or \
       (player == "paper" and ai == "rock") or \
       (player == "scissors" and ai == "paper"):
        return "player"
    return "ai"

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    keypoints = extract_keypoints_from_frame(frame_rgb)

    if keypoints is not None:
        sequence.append(keypoints)
        early_sequence.append(keypoints)

        if len(sequence) > SEQUENCE_LENGTH:
            sequence.pop(0)
        if len(early_sequence) > EARLY_PREDICTION_FRAMES:
            early_sequence.pop(0)

        # EARLY prediction: let AI pick its move
        if not ai_prediction_made and len(early_sequence) == EARLY_PREDICTION_FRAMES:
            early_input = np.array(early_sequence).reshape(1, EARLY_PREDICTION_FRAMES, 63).astype(np.float32)
            predicted_player_move = get_ai_move(early_input)
            if predicted_player_move != "nothing":
                ai_move = {'rock': 'paper', 'paper': 'scissors', 'scissors': 'rock'}.get(predicted_player_move, 'rock')
                ai_prediction_made = True
                last_ai_move = ai_move  # Show this immediately
                show_ai_now = True

        if len(sequence) == SEQUENCE_LENGTH:
            input_data = np.array(sequence).reshape(1, SEQUENCE_LENGTH, 63).astype(np.float32)
            player_move = get_ai_move(input_data)

            if player_move != "nothing":
                if player_move == prev_move:
                    move_counter += 1
                else:
                    move_counter = 1
                prev_move = player_move

                if move_counter >= STABILITY_FRAMES and ai_prediction_made:
                    result = determine_winner(player_move, ai_move)

                    if result == "player":
                        player_score += 1
                        last_result_text = "YOU WIN!"
                    elif result == "ai":
                        ai_score += 1
                        last_result_text = "AI WINS!"
                    else:
                        last_result_text = "IT'S A DRAW!"

                    last_stable_move = player_move

                    # Reset for next round
                    ai_prediction_made = False
                    ai_move = "nothing"
                    show_ai_now = False  # Immediately stop showing AI move
                    sequence, early_sequence = [], []
                    move_counter = 0
                    prev_move = None
    else:
        # If no hand detected, also hide AI move
        show_ai_now = False

    # --- UI Drawing Area ---
    ui_frame = np.zeros((500, 800, 3), dtype=np.uint8)

    # Title
    cv2.putText(ui_frame, "ROCK PAPER SCISSORS", (150, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 3)

    # Player frame (left)
    player_display = cv2.resize(frame, (300, 300))
    ui_frame[100:400, 50:350] = player_display

    # AI move frame (right)
    ai_display = ai_images[last_ai_move if show_ai_now else "nothing"]
    ui_frame[100:400, 450:750] = ai_display

    # Labels
    cv2.putText(ui_frame, "You", (160, 430), cv2.FONT_HERSHEY_SIMPLEX, 1, (200, 200, 255), 2)
    cv2.putText(ui_frame, "AI", (580, 430), cv2.FONT_HERSHEY_SIMPLEX, 1, (200, 200, 255), 2)

    # Result
    if last_result_text:
        cv2.putText(ui_frame, last_result_text, (260, 470), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 100), 3)

    # Score
    cv2.putText(ui_frame, f"Score: You {player_score} - {ai_score} AI", (220, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)

    cv2.imshow("Rock Paper Scissors", ui_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
