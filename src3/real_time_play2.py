import cv2
import numpy as np
import time
from hand_tracking_module import extract_keypoints_from_frame
from ai_opponent_module import get_ai_move

cap = cv2.VideoCapture(0)

SEQUENCE_LENGTH = 15
STABILITY_FRAMES = 2
COOLDOWN_TIME = 2  # seconds

sequence = []
prev_move = None
move_counter = 0
ai_has_played = False
cooldown_start_time = None

player_score, ai_score = 0, 0
last_result_text = ""
last_stable_move = ""
last_ai_move = ""

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

    if ai_has_played:
        if time.time() - cooldown_start_time >= COOLDOWN_TIME:
            ai_has_played = False
            last_stable_move = ""
            last_ai_move = ""
            last_result_text = ""
            sequence = []
            move_counter = 0
            prev_move = None
        else:
            # Freeze and show result during cooldown
            cv2.putText(frame, f"Your move: {last_stable_move}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
            cv2.putText(frame, f"AI move: {last_ai_move}", (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
            cv2.putText(frame, f"Result: {last_result_text}", (10, 160), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
    else:
        # Only process input if not in cooldown
        if keypoints is not None:
            sequence.append(keypoints)
            if len(sequence) > SEQUENCE_LENGTH:
                sequence.pop(0)

            if len(sequence) == SEQUENCE_LENGTH:
                input_data = np.array(sequence).reshape(1, SEQUENCE_LENGTH, 63).astype(np.float32)
                player_move = get_ai_move(input_data)

                if player_move != "nothing":
                    if player_move == prev_move:
                        move_counter += 1
                    else:
                        move_counter = 1
                    prev_move = player_move

                    if move_counter >= STABILITY_FRAMES:
                        # Lock in the move and immediately get AI response
                        stable_move = player_move
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
                        ai_has_played = True
                        cooldown_start_time = time.time()

        # Prompt only if no stable move yet
        if not ai_has_played:
            cv2.putText(frame, "SHOW YOUR MOVE!", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 3)

    # Score Display (always visible)
    cv2.putText(frame, f"Score: You {player_score} - {ai_score} AI", (10, 450),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    cv2.imshow("Rock Paper Scissors", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()





'''
import cv2
import numpy as np
import time
from hand_tracking_module import extract_keypoints_from_frame
from ai_opponent_module import get_ai_move

cap = cv2.VideoCapture(0)

SEQUENCE_LENGTH = 15
STABILITY_FRAMES = 2
COOLDOWN_TIME = 2  # seconds

sequence = []
prev_move = None
move_counter = 0
ai_has_played = False
cooldown_start_time = None

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

    # Wait during cooldown
    if ai_has_played:
        if time.time() - cooldown_start_time >= COOLDOWN_TIME:
            ai_has_played = False
            last_stable_move = ""
            last_ai_move = ""
            last_result_text = ""
            sequence = []
            move_counter = 0
            prev_move = None
            latest_player_move = "nothing"

    elif keypoints is not None:
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
                    ai_has_played = True
                    cooldown_start_time = time.time()

    # UI Rendering
    if ai_has_played:
        cv2.putText(frame, f"Your move: {last_stable_move}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
        cv2.putText(frame, f"AI move: {last_ai_move}", (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
        cv2.putText(frame, f"Result: {last_result_text}", (10, 160), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
    else:
        cv2.putText(frame, "SHOW YOUR MOVE!", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 3)
        if latest_player_move != "nothing":
            cv2.putText(frame, f"We see: {latest_player_move}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (100, 255, 100), 2)
        else:
            cv2.putText(frame, "We see: nothing", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (100, 100, 255), 2)

    # Score
    cv2.putText(frame, f"Score: You {player_score} - {ai_score} AI", (10, 450),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    cv2.imshow("Rock Paper Scissors", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
'''




'''
import cv2
import numpy as np
import time
from hand_tracking_module import extract_keypoints_from_frame
from ai_opponent_module import get_ai_move

cap = cv2.VideoCapture(0)

SEQUENCE_LENGTH = 15
STABILITY_FRAMES = 2

sequence = []
prev_move = None
move_counter = 0
ai_has_played = False

player_score, ai_score = 0, 0
last_result_text = ""
last_stable_move = ""
last_ai_move = ""
latest_player_move = ""

cooldown_frames = 30  # ~1 second if FPS ~30
cooldown_counter = 0

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

    if cooldown_counter == 0:
        if keypoints is not None:
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

                        # AI chooses counter move
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
                        ai_has_played = True
                        move_counter = 0
                        sequence = []

                        cooldown_counter = cooldown_frames  # Start cooldown
                        prev_move = None
                        latest_player_move = "nothing"
    else:
        cooldown_counter -= 1

    # 🖥️ UI Elements
    if ai_has_played and cooldown_counter >= cooldown_frames - 10:
        # Show result briefly at start of cooldown
        cv2.putText(frame, f"Result: You: {last_stable_move} | AI: {last_ai_move}", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        cv2.putText(frame, last_result_text, (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
    elif cooldown_counter == 0:
        cv2.putText(frame, "SHOW YOUR MOVE!", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 0), 3)
        if latest_player_move != "nothing":
            cv2.putText(frame, f"We see: {latest_player_move}", (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (100, 255, 100), 2)
        else:
            cv2.putText(frame, "We see: nothing", (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (100, 100, 255), 2)

    # Score
    cv2.putText(frame, f"Score: You {player_score} - {ai_score} AI", (10, 450),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    cv2.imshow("Rock Paper Scissors", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
'''






'''
import cv2
import numpy as np
from hand_tracking_module import extract_keypoints_from_frame
from ai_opponent_module import get_ai_move

cap = cv2.VideoCapture(0)

SEQUENCE_LENGTH = 15   # Shorter = faster (but keep ≥10 for context)
STABILITY_FRAMES = 2   # Lower = faster move detection

sequence = []
prev_move = None
move_counter = 0
ai_has_played = False

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

    if keypoints is not None:
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

                # React faster
                if move_counter >= STABILITY_FRAMES and not ai_has_played:
                    stable_move = player_move

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
                    ai_has_played = True
                    move_counter = 0
                    sequence = []

    # Reset after each prediction
    if ai_has_played:
        ai_has_played = False
        prev_move = None
        latest_player_move = "nothing"

    # UI
    if not ai_has_played:
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
'''