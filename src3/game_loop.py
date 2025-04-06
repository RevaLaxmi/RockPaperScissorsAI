import cv2
import numpy as np
import time
from hand_tracking_module import extract_keypoints_from_frame
from ai_opponent_module import get_ai_move

cap = cv2.VideoCapture(0)
player_score, ai_score = 0, 0
rounds_played = 0
SEQUENCE_LENGTH = 30

# Game timing stages
STAGE_TIMES = {
    "get_ready": 1.5,
    "rock": 1.0,
    "paper": 1.0,
    "scissors": 1.0,
    "shoot": 1.5,
    "result": 2.0
}
STAGES = list(STAGE_TIMES.keys())

# State variables
current_stage_idx = 0
stage_start_time = time.time()

sequence = []
stable_move = ""
last_stable_move = ""
last_ai_move = ""
last_result_text = ""
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

def get_stage_text(stage_name):
    if stage_name == "get_ready":
        return "Get Ready..."
    elif stage_name == "rock":
        return "Rock..."
    elif stage_name == "paper":
        return "Paper..."
    elif stage_name == "scissors":
        return "Scissors..."
    elif stage_name == "shoot":
        return "SHOOT!"
    elif stage_name == "result":
        return f"You: {last_stable_move} | AI: {last_ai_move} - {last_result_text}"

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    keypoints = extract_keypoints_from_frame(frame_rgb)

    current_stage = STAGES[current_stage_idx]
    elapsed_time = time.time() - stage_start_time

    # Collect frames during anticipation stages
    if current_stage in ["rock", "paper", "scissors"] and keypoints is not None:
        sequence.append(keypoints)
        if len(sequence) > SEQUENCE_LENGTH:
            sequence.pop(0)

    # On "shoot", do prediction ONCE per round
    if current_stage == "shoot" and len(sequence) == SEQUENCE_LENGTH and stable_move == "":
        input_data = np.array(sequence).reshape(1, SEQUENCE_LENGTH, 63).astype(np.float32)
        player_move = get_ai_move(input_data)
        latest_player_move = player_move
        sequence = []  # clear for next round

        if player_move != "nothing":
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
        else:
            last_stable_move = "nothing"
            last_ai_move = "-"
            last_result_text = "Couldn't detect move"

    # Draw stage text
    stage_text = get_stage_text(current_stage)
    cv2.putText(frame, stage_text, (10, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 0), 3)

    # On "shoot", show BOTH moves
    if current_stage == "shoot":
        if latest_player_move and latest_player_move != "nothing":
            cv2.putText(frame, f"You played: {latest_player_move.upper()}", (10, 120),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
            cv2.putText(frame, f"AI played: {last_ai_move.upper()}", (10, 170),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)
        else:
            cv2.putText(frame, "Can't detect your move!", (10, 120),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)

    # Scoreboard
    cv2.putText(frame, f"Score: You {player_score} - {ai_score} AI", (10, 450),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    cv2.imshow("Rock Paper Scissors", frame)

    # Advance to next stage
    if elapsed_time > STAGE_TIMES[current_stage]:
        current_stage_idx += 1
        stage_start_time = time.time()
        if current_stage_idx >= len(STAGES):
            current_stage_idx = 0
            rounds_played += 1
            stable_move = ""  # reset for next round
            latest_player_move = ""

    if rounds_played >= 5:
        break
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
player_score, ai_score = 0, 0
rounds_played = 0
SEQUENCE_LENGTH = 30

# Game timing stages
STAGE_TIMES = {
    "get_ready": 1.5,
    "rock": 1.0,
    "paper": 1.0,
    "scissors": 1.0,
    "shoot": 1.5,
    "result": 2.0
}
STAGES = list(STAGE_TIMES.keys())

# State variables
current_stage_idx = 0
stage_start_time = time.time()

sequence = []
stable_move = None
last_stable_move = ""
last_ai_move = ""
last_result_text = ""
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

def get_stage_text(stage_name):
    if stage_name == "get_ready":
        return "Get Ready..."
    elif stage_name == "rock":
        return "Rock..."
    elif stage_name == "paper":
        return "Paper..."
    elif stage_name == "scissors":
        return "Scissors..."
    elif stage_name == "shoot":
        return "SHOOT! Show your move"
    elif stage_name == "result":
        return f"You: {last_stable_move} | AI: {last_ai_move} - {last_result_text}"

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    keypoints = extract_keypoints_from_frame(frame_rgb)

    current_stage = STAGES[current_stage_idx]
    elapsed_time = time.time() - stage_start_time

    # Stage progression
    if elapsed_time > STAGE_TIMES[current_stage]:
        current_stage_idx += 1
        stage_start_time = time.time()

        if current_stage_idx >= len(STAGES):
            current_stage_idx = 0  # reset for next round
            rounds_played += 1

    # SHOOT stage: perform prediction only at this moment
    if current_stage == "shoot":
        if keypoints is not None:
            sequence.append(keypoints)
            if len(sequence) > SEQUENCE_LENGTH:
                sequence.pop(0)

            if len(sequence) == SEQUENCE_LENGTH:
                input_data = np.array(sequence).reshape(1, SEQUENCE_LENGTH, 63).astype(np.float32)
                player_move = get_ai_move(input_data)
                latest_player_move = player_move

                if player_move != "nothing":
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
                    sequence = []  # clear after a round
        else:
            latest_player_move = "nothing"

    # Draw stage text
    stage_text = get_stage_text(current_stage)
    cv2.putText(frame, stage_text, (10, 80),
                cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 255), 5)

    # Show live prediction during shoot
    if current_stage == "shoot":
        color = (0, 255, 0) if latest_player_move != "nothing" else (0, 0, 255)
        cv2.putText(frame, f"Model sees: {latest_player_move}", (10, 130),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 3)

    # Scoreboard
    cv2.putText(frame, f"Score: You {player_score} - {ai_score} AI", (10, 450),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    cv2.imshow("Rock Paper Scissors", frame)

    if rounds_played >= 5:
        break
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
player_score, ai_score = 0, 0
rounds_played = 0
SEQUENCE_LENGTH = 30

# Game timing stages
STAGE_TIMES = {
    "get_ready": 1.5,
    "rock": 1.0,
    "paper": 1.0,
    "scissors": 1.0,
    "shoot": 1.5,
    "result": 2.0
}
STAGES = list(STAGE_TIMES.keys())

# State variables
current_stage_idx = 0
stage_start_time = time.time()

sequence = []
stable_move = None
last_stable_move = ""
last_ai_move = ""
last_result_text = ""
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

def get_stage_text(stage_name):
    if stage_name == "get_ready":
        return "Get Ready..."
    elif stage_name == "rock":
        return "Rock..."
    elif stage_name == "paper":
        return "Paper..."
    elif stage_name == "scissors":
        return "Scissors..."
    elif stage_name == "shoot":
        return "SHOOT! Show your move"
    elif stage_name == "result":
        return f"You: {last_stable_move} | AI: {last_ai_move} - {last_result_text}"

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    keypoints = extract_keypoints_from_frame(frame_rgb)

    current_stage = STAGES[current_stage_idx]
    elapsed_time = time.time() - stage_start_time

    # Stage progression
    if elapsed_time > STAGE_TIMES[current_stage]:
        current_stage_idx += 1
        stage_start_time = time.time()

        if current_stage_idx >= len(STAGES):
            current_stage_idx = 0  # reset for next round
            rounds_played += 1

    if current_stage == "shoot" and keypoints is not None:
        sequence.append(keypoints)
        if len(sequence) > SEQUENCE_LENGTH:
            sequence.pop(0)

        if len(sequence) == SEQUENCE_LENGTH:
            input_data = np.array(sequence).reshape(1, SEQUENCE_LENGTH, 63).astype(np.float32)
            player_move = get_ai_move(input_data)
            latest_player_move = player_move

            if player_move != "nothing":
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
                sequence = []  # clear after a round

    # Draw stage text
    stage_text = get_stage_text(current_stage)
    cv2.putText(frame, stage_text, (10, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 0), 3)

    # Show live prediction during shoot
    if current_stage == "shoot":
        cv2.putText(frame, f"Model sees: {latest_player_move}", (10, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Scoreboard
    cv2.putText(frame, f"Score: You {player_score} - {ai_score} AI", (10, 450),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    cv2.imshow("Rock Paper Scissors", frame)

    if rounds_played >= 5:
        break
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
'''





'''
# game_loop.py
import cv2
import numpy as np
from hand_tracking_module import extract_keypoints_from_frame
from ai_opponent_module import get_ai_move

cap = cv2.VideoCapture(0)
rounds_played = 0
player_score, ai_score = 0, 0

sequence = []
SEQUENCE_LENGTH = 30

# Stability and cooldown control
prev_move = None
move_counter = 0
stable_move = None
cooldown_counter = 0
COOLDOWN_FRAMES = 60  # 2 seconds at 30 fps

# Display data
last_stable_move = ""
last_ai_move = ""
last_result_text = ""
latest_player_move = ""

# Winner logic
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

    player_move = 'nothing'
    message_text = ""

    if keypoints is not None:
        sequence.append(keypoints)
        if len(sequence) > SEQUENCE_LENGTH:
            sequence.pop(0)

        if len(sequence) == SEQUENCE_LENGTH:
            input_data = np.array(sequence).reshape(1, SEQUENCE_LENGTH, 63).astype(np.float32)
            player_move = get_ai_move(input_data)
            latest_player_move = player_move

            if player_move != 'nothing':
                if player_move == prev_move:
                    move_counter += 1
                else:
                    move_counter = 1
                prev_move = player_move

                if move_counter >= 10 and cooldown_counter == 0:
                    stable_move = player_move
                    ai_move = {'rock': 'paper', 'paper': 'scissors', 'scissors': 'rock'}[stable_move]

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
                    rounds_played += 1
                    cooldown_counter = COOLDOWN_FRAMES
                    move_counter = 0

    # Countdown / move cue
    if cooldown_counter > 0:
        cooldown_counter -= 1
        message_text = f"Next round in: {cooldown_counter // 10 + 1}..."
    else:
        message_text = "SHOW YOUR MOVE NOW!"

    # Overlay for readability
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (frame.shape[1], 240), (0, 0, 0), -1)
    frame = cv2.addWeighted(overlay, 0.4, frame, 0.6, 0)

    # Prompt text
    if cooldown_counter == 0:
        cv2.putText(frame, message_text, (180, 200),
                    cv2.FONT_HERSHEY_DUPLEX, 1.4, (0, 255, 255), 3)
    else:
        cv2.putText(frame, message_text, (10, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 200, 255), 2)

    # Player hand detection
    if latest_player_move != 'nothing':
        cv2.putText(frame, f"We see: {latest_player_move}", (10, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (100, 255, 100), 2)
    elif cooldown_counter == 0:
        cv2.putText(frame, "We see: nothing", (10, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (50, 100, 255), 2)

    # Result and score
    if last_stable_move and last_ai_move:
        cv2.putText(frame, f"You: {last_stable_move} | AI: {last_ai_move}", (10, 120),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(frame, f"{last_result_text}", (10, 160),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 2)

    cv2.putText(frame, f"Score: You {player_score} - {ai_score} AI", (10, 210),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    cv2.imshow("Rock Paper Scissors", frame)

    if rounds_played >= 5:
        break
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
'''




'''
# game_loop.py
import cv2
import numpy as np
from hand_tracking_module import extract_keypoints_from_frame
from ai_opponent_module import get_ai_move

cap = cv2.VideoCapture(0)
rounds_played = 0
player_score, ai_score = 0, 0

sequence = []
SEQUENCE_LENGTH = 30

# Stability-related variables
prev_move = None
move_counter = 0
stable_move = None
cooldown_counter = 0
COOLDOWN_FRAMES = 60

# Game control flags
waiting_for_move = False

# Last move info
last_stable_move = ""
last_ai_move = ""
last_result_text = ""
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
    keypoints = extract_keypoints_from_frame(frame_rgb)  # shape (63,)

    message_text = ""
    player_move = 'nothing'

    if cooldown_counter > 0:
        cooldown_counter -= 1
        message_text = f"Next round in: {cooldown_counter // 10 + 1}..."
        waiting_for_move = False  # Not accepting input during cooldown

    elif not waiting_for_move:
        waiting_for_move = True
        move_counter = 0
        prev_move = None
        message_text = "SHOW YOUR MOVE NOW!"

    elif waiting_for_move:
        message_text = "Waiting for your move..."

        if keypoints is not None:
            sequence.append(keypoints)

            if len(sequence) > SEQUENCE_LENGTH:
                sequence.pop(0)

            if len(sequence) == SEQUENCE_LENGTH:
                input_data = np.array(sequence).reshape(1, SEQUENCE_LENGTH, 63).astype(np.float32)
                player_move = get_ai_move(input_data)
                latest_player_move = player_move

                if player_move != 'nothing':
                    if player_move == prev_move:
                        move_counter += 1
                    else:
                        move_counter = 1
                    prev_move = player_move

                    if move_counter >= 10:
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

                        rounds_played += 1
                        cooldown_counter = COOLDOWN_FRAMES
                        waiting_for_move = False

                        last_stable_move = stable_move
                        last_ai_move = ai_move
                        move_counter = 0

    # Display instructions
    cv2.putText(frame, message_text, (10, 160),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

    # Show current detected move
    if latest_player_move != 'nothing':
        cv2.putText(frame, f"We see: {latest_player_move}", (10, 200),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (100, 255, 100), 2)
    else:
        if waiting_for_move:
            cv2.putText(frame, "We see: nothing", (10, 200),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (50, 100, 255), 2)

    # Show last round's result
    if last_stable_move and last_ai_move:
        cv2.putText(frame, f"You: {last_stable_move} | AI: {last_ai_move}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(frame, f"{last_result_text}", (10, 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 2)

    # Show score
    cv2.putText(frame, f"Score: You {player_score} - {ai_score} AI", (10, 110),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    cv2.imshow("Rock Paper Scissors", frame)

    if rounds_played >= 5:
        break
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
'''





'''
# game_loop.py
import cv2
import numpy as np
from hand_tracking_module import extract_keypoints_from_frame
from ai_opponent_module import get_ai_move

cap = cv2.VideoCapture(0)
rounds_played = 0
player_score, ai_score = 0, 0

sequence = []
SEQUENCE_LENGTH = 30

# New stability-related variables
prev_move = None
move_counter = 0
stable_move = None
cooldown_counter = 0
COOLDOWN_FRAMES = 60  # Adjust this value to control cooldown duration

# Last move info
last_stable_move = ""
last_ai_move = ""
last_result_text = ""
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
    keypoints = extract_keypoints_from_frame(frame_rgb)  # shape (63,)

    message_text = ""
    player_move = 'nothing'

    if keypoints is not None:
        sequence.append(keypoints)

        if len(sequence) > SEQUENCE_LENGTH:
            sequence.pop(0)

        if len(sequence) == SEQUENCE_LENGTH:
            input_data = np.array(sequence).reshape(1, SEQUENCE_LENGTH, 63).astype(np.float32)
            player_move = get_ai_move(input_data)
            latest_player_move = player_move

            if player_move != 'nothing':
                if player_move == prev_move:
                    move_counter += 1
                else:
                    move_counter = 1  # reset counter if move changes
                prev_move = player_move

                if move_counter >= 10 and cooldown_counter == 0:
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

                    rounds_played += 1
                    cooldown_counter = COOLDOWN_FRAMES

                    last_stable_move = stable_move
                    last_ai_move = ai_move
                    move_counter = 0  # reset after scoring

    if cooldown_counter > 0:
        cooldown_counter -= 1
        message_text = f"Next round in: {cooldown_counter // 10 + 1}..."
    else:
        message_text = "SHOW YOUR MOVE NOW!"

    # Display guidance message
    cv2.putText(frame, message_text, (10, 160),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

    # Show current detected move
    if latest_player_move != 'nothing':
        cv2.putText(frame, f"We see: {latest_player_move}", (10, 200),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (100, 255, 100), 2)

    # Always show last known result
    if last_stable_move and last_ai_move:
        cv2.putText(frame, f"You: {last_stable_move} | AI: {last_ai_move}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(frame, f"{last_result_text}", (10, 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 2)

    cv2.putText(frame, f"Score: You {player_score} - {ai_score} AI", (10, 110),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    cv2.imshow("Rock Paper Scissors", frame)

    if rounds_played >= 5:
        break
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
'''


'''
# game_loop.py
import cv2
import numpy as np
from hand_tracking_module import extract_keypoints_from_frame
from ai_opponent_module import get_ai_move

cap = cv2.VideoCapture(0)
rounds_played = 0
player_score, ai_score = 0, 0

sequence = []
SEQUENCE_LENGTH = 30

# New stability-related variables
prev_move = None
move_counter = 0
stable_move = None
cooldown_counter = 0
COOLDOWN_FRAMES = 60  # Adjust this value to control cooldown duration

# Last move info
last_stable_move = ""
last_ai_move = ""
last_result_text = ""

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
    keypoints = extract_keypoints_from_frame(frame_rgb)  # shape (63,)

    if keypoints is not None:
        sequence.append(keypoints)

        if len(sequence) > SEQUENCE_LENGTH:
            sequence.pop(0)

        if len(sequence) == SEQUENCE_LENGTH:
            input_data = np.array(sequence).reshape(1, SEQUENCE_LENGTH, 63).astype(np.float32)
            player_move = get_ai_move(input_data)

            if player_move != 'nothing':
                if player_move == prev_move:
                    move_counter += 1
                else:
                    move_counter = 1  # reset counter if move changes
                prev_move = player_move

                if move_counter >= 10 and cooldown_counter == 0:
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

                    rounds_played += 1
                    cooldown_counter = COOLDOWN_FRAMES

                    last_stable_move = stable_move
                    last_ai_move = ai_move

    if cooldown_counter > 0:
        cooldown_counter -= 1

    # Always show last known result
    if last_stable_move and last_ai_move:
        cv2.putText(frame, f"You: {last_stable_move} | AI: {last_ai_move}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(frame, f"{last_result_text}", (10, 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 2)

    cv2.putText(frame, f"Score: You {player_score} - {ai_score} AI", (10, 110),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    cv2.imshow("Rock Paper Scissors", frame)

    if rounds_played >= 5:
        break
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
'''



'''
# game_loop.py
import cv2
import numpy as np
from hand_tracking_module import extract_keypoints_from_frame
from ai_opponent_module import get_ai_move

cap = cv2.VideoCapture(0)
rounds_played = 0
player_score, ai_score = 0, 0

sequence = []
SEQUENCE_LENGTH = 30

# New stability-related variables
prev_move = None
move_counter = 0
stable_move = None
cooldown_counter = 0
COOLDOWN_FRAMES = 60  # Adjust this value to control cooldown duration


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
    keypoints = extract_keypoints_from_frame(frame_rgb)  # shape (63,)

    if keypoints is not None:
        sequence.append(keypoints)

        if len(sequence) > SEQUENCE_LENGTH:
            sequence.pop(0)

        if len(sequence) == SEQUENCE_LENGTH:
            input_data = np.array(sequence).reshape(1, SEQUENCE_LENGTH, 63).astype(np.float32)
            player_move = get_ai_move(input_data)

            if player_move != 'nothing':
                if player_move == prev_move:
                    move_counter += 1
                else:
                    move_counter = 1  # reset counter if move changes
                prev_move = player_move

                if move_counter >= 10 and cooldown_counter == 0:
                    stable_move = player_move
                    ai_move = {
                        'rock': 'paper',
                        'paper': 'scissors',
                        'scissors': 'rock'
                    }[stable_move]

                    result = determine_winner(stable_move, ai_move)
                    if result == "player":
                        player_score += 1
                    elif result == "ai":
                        ai_score += 1
                    rounds_played += 1

                    cooldown_counter = COOLDOWN_FRAMES

                    cv2.putText(frame, f"You: {stable_move} | AI: {ai_move}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)
                    cv2.putText(frame, f"Score: You {player_score} - {ai_score} AI", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)

    if cooldown_counter > 0:
        cooldown_counter -= 1

    cv2.imshow("Rock Paper Scissors", frame)

    if rounds_played >= 5:
        break
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
'''