import cv2
import numpy as np
from hand_tracking_module import extract_keypoints_from_frame
from ai_opponent_module import get_ai_move
import time

cap = cv2.VideoCapture(0)

SEQUENCE_LENGTH = 30
STABILITY_FRAMES = 10
COOLDOWN_TIME = 2  # seconds to wait after each round

sequence = []
prev_move = None
move_counter = 0
stable_move = None

cooldown_start = None
in_cooldown = False

player_score, ai_score = 0, 0
last_result_text = ""
last_stable_move = ""
last_ai_move = ""
latest_player_move = ""

def determine_winner(player_move, ai_move):
    if player_move == ai_move:
        return "draw"
    if (
        (player_move == 'rock' and ai_move == 'scissors') or
        (player_move == 'paper' and ai_move == 'rock') or
        (player_move == 'scissors' and ai_move == 'paper')
    ):
        return "player"
    else:
        return "ai"

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    keypoints = extract_keypoints_from_frame(frame_rgb)

    player_move = "nothing"

    if keypoints is not None and not in_cooldown:
        sequence.append(keypoints)
        if len(sequence) > SEQUENCE_LENGTH:
            sequence.pop(0)

        if len(sequence) == SEQUENCE_LENGTH:
            input_data = np.array(sequence).reshape(1, SEQUENCE_LENGTH, 63).astype(np.float32)
            player_move = get_ai_move(input_data)
            latest_player_move = player_move

            if player_move != "nothing":
                if player_move == prev_move:
                    move_counter += 1
                else:
                    move_counter = 1
                prev_move = player_move

                if move_counter >= STABILITY_FRAMES:
                    stable_move = player_move

                    # AI plays instantly
                    ai_move = {
                        'rock': 'paper',
                        'paper': 'scissors',
                        'scissors': 'rock'
                    }[stable_move]

                    result = determine_winner(stable_move, ai_move)
                    if result == "player":
                        player_score += 1
                        last_result_text = "You win!"
                    elif result == "ai":
                        ai_score += 1
                        last_result_text = "AI wins!"
                    else:
                        last_result_text = "It's a draw!"

                    last_stable_move = stable_move
                    last_ai_move = ai_move

                    # Start cooldown to prevent re-trigger
                    in_cooldown = True
                    cooldown_start = time.time()
                    move_counter = 0
                    sequence = []

    # Cooldown logic
    if in_cooldown:
        elapsed = time.time() - cooldown_start
        if elapsed >= COOLDOWN_TIME:
            in_cooldown = False
            stable_move = None
            prev_move = None
            latest_player_move = "nothing"

    # UI
    if not in_cooldown:
        cv2.putText(frame, "SHOW YOUR MOVE!", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 0), 3)
        if latest_player_move != "nothing":
            cv2.putText(frame, f"We see: {latest_player_move}", (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (100, 255, 100), 2)
        else:
            cv2.putText(frame, "We see: nothing", (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (100, 100, 255), 2)
    else:
        cv2.putText(frame, f"Result: You: {last_stable_move} | AI: {last_ai_move}", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        cv2.putText(frame, last_result_text, (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)

    cv2.putText(frame, f"Score: You {player_score} - {ai_score} AI", (10, 450),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    cv2.imshow("Rock Paper Scissors", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
