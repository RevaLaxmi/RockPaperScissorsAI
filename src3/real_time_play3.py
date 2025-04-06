import cv2
import numpy as np
from hand_tracking_module import extract_keypoints_from_frame
from ai_opponent_module import get_ai_move

cap = cv2.VideoCapture(0)

SEQUENCE_LENGTH = 10           # Slightly reduced
EARLY_PREDICTION_FRAMES = 5    # AI decides based on this
STABILITY_FRAMES = 7           # For human move stabilization

sequence = []
early_sequence = []

player_move = "nothing"
prev_move = None
move_counter = 0

ai_committed = False
ai_move = "nothing"
ai_prediction_made = False

player_score, ai_score = 0, 0
last_result_text = ""
last_stable_move = ""
last_ai_move = ""

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

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    keypoints = extract_keypoints_from_frame(frame_rgb)

    if keypoints is not None:
        sequence.append(keypoints)
        early_sequence.append(keypoints)

        # Maintain max lengths
        if len(sequence) > SEQUENCE_LENGTH:
            sequence.pop(0)
        if len(early_sequence) > EARLY_PREDICTION_FRAMES:
            early_sequence.pop(0)

        # --- AI predicts early ---
        if not ai_prediction_made and len(early_sequence) == EARLY_PREDICTION_FRAMES:
            early_input = np.array(early_sequence).reshape(1, EARLY_PREDICTION_FRAMES, 63).astype(np.float32)
            predicted_player_move = get_ai_move(early_input)
            if predicted_player_move != "nothing":
                ai_move = {
                    'rock': 'paper',
                    'paper': 'scissors',
                    'scissors': 'rock'
                }.get(predicted_player_move, 'rock')
                ai_prediction_made = True

        # --- Player move stabilizing ---
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
                        last_result_text = "You win!"
                    elif result == "ai":
                        ai_score += 1
                        last_result_text = "AI wins!"
                    else:
                        last_result_text = "It's a draw!"

                    last_stable_move = player_move
                    last_ai_move = ai_move

                    # Reset all for next round
                    ai_prediction_made = False
                    sequence = []
                    early_sequence = []
                    move_counter = 0
                    prev_move = None

    # --- UI ---
    cv2.putText(frame, f"Your move: {last_stable_move or '...'}", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    cv2.putText(frame, f"AI move: {last_ai_move or '...'}", (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    if last_result_text:
        cv2.putText(frame, last_result_text, (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)

    cv2.putText(frame, f"Score: You {player_score} - {ai_score} AI", (10, 450), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    cv2.imshow("Rock Paper Scissors", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
