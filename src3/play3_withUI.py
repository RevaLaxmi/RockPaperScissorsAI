import cv2
import numpy as np
from hand_tracking_module import extract_keypoints_from_frame
from ai_opponent_module import get_ai_move
from PIL import ImageFont, ImageDraw, Image

# Load AI move images
ai_images = {
    "rock": cv2.imread("assets/rock2.png"),
    "paper": cv2.imread("assets/paper2.png"),
    "scissors": cv2.imread("assets/scissors2.png"),
    "nothing": np.zeros((300, 300, 3), dtype=np.uint8)
}

# Resize images
for key in ai_images:
    ai_images[key] = cv2.resize(ai_images[key], (300, 300))

cap = cv2.VideoCapture(0)

# Constants
SEQUENCE_LENGTH = 10
EARLY_PREDICTION_FRAMES = 5
STABILITY_FRAMES = 7

# State vars
sequence, early_sequence = [], []
player_move, prev_move = "nothing", None
move_counter = 0
ai_move = "nothing"
ai_prediction_made = False
show_ai_now = False
player_score, ai_score = 0, 0
last_result_text = ""
last_stable_move, last_ai_move = "", ""
game_over = False
wait_frames = 0  # Frame-based pause between rounds

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

    if keypoints is not None and not game_over and wait_frames == 0:
        sequence.append(keypoints)
        early_sequence.append(keypoints)
        if len(sequence) > SEQUENCE_LENGTH:
            sequence.pop(0)
        if len(early_sequence) > EARLY_PREDICTION_FRAMES:
            early_sequence.pop(0)

        # Early prediction by AI
        if not ai_prediction_made and len(early_sequence) == EARLY_PREDICTION_FRAMES:
            early_input = np.array(early_sequence).reshape(1, EARLY_PREDICTION_FRAMES, 63).astype(np.float32)
            predicted_player_move = get_ai_move(early_input)
            if predicted_player_move != "nothing":
                ai_move = {'rock': 'paper', 'paper': 'scissors', 'scissors': 'rock'}.get(predicted_player_move, 'rock')
                ai_prediction_made = True
                last_ai_move = ai_move

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
                    show_ai_now = True

                    if player_score == 3:
                        game_over = True
                        last_result_text = "YOU WIN THE GAME!"
                    elif ai_score == 3:
                        game_over = True
                        last_result_text = "AI WINS THE GAME!"

                    if not game_over:
                        wait_frames = 30  # Delay ~1 second using frames

    # --- UI Drawing START ---

    chakra_font = ImageFont.truetype("C:/Users/Reva Laxmi Chauhan/Desktop/RockPaperScissorsAI/assets/fonts/RussoOne-Regular.ttf", 28)
    russo_font_big = ImageFont.truetype("C:/Users/Reva Laxmi Chauhan/Desktop/RockPaperScissorsAI/assets/fonts/RussoOne-Regular.ttf", 36)
    russo_font_button = ImageFont.truetype("C:/Users/Reva Laxmi Chauhan/Desktop/RockPaperScissorsAI/assets/fonts/RussoOne-Regular.ttf", 28)

    ui_frame = np.ones((600, 900, 3), dtype=np.uint8) * 255
    player_display = cv2.resize(frame, (300, 300))
    cv2.rectangle(ui_frame, (100, 100), (400, 400), (0, 0, 0), 2)
    ui_frame[100:400, 100:400] = player_display

    ai_display = ai_images[last_ai_move if show_ai_now else "nothing"]
    cv2.rectangle(ui_frame, (500, 100), (800, 400), (0, 0, 0), 2)
    ui_frame[100:400, 500:800] = ai_display

    ui_pil = Image.fromarray(ui_frame)
    draw = ImageDraw.Draw(ui_pil)

    draw.text((180, 30), "ROCK PAPER SCISSORS", font=chakra_font, fill=(0, 0, 0))
    draw.text((220, 410), "You", font=chakra_font, fill=(0, 0, 0))
    draw.text((630, 410), "AI", font=chakra_font, fill=(0, 0, 0))
    draw.text((280, 450), f"Score: You {player_score} - {ai_score} AI", font=chakra_font, fill=(0, 0, 0))

    if last_result_text:
        draw.text((250, 490), last_result_text, font=russo_font_big, fill=(0, 0, 0))

    restart_button_coords = (350, 530, 550, 570)
    if game_over:
        draw.rectangle(restart_button_coords, outline=(0, 0, 0), width=2)
        draw.text((restart_button_coords[0] + 20, restart_button_coords[1] + 5),
                  "RESTART", font=russo_font_button, fill=(0, 0, 0))

    ui_frame = np.array(ui_pil)
    # --- UI Drawing END ---

    def mouse_callback(event, x, y, flags, param):
        global player_score, ai_score, last_result_text, last_ai_move, last_stable_move, game_over, show_ai_now, wait_frames
        if event == cv2.EVENT_LBUTTONDOWN:
            x1, y1, x2, y2 = restart_button_coords
            if game_over and x1 <= x <= x2 and y1 <= y <= y2:
                player_score = 0
                ai_score = 0
                last_result_text = ""
                last_ai_move = ""
                last_stable_move = ""
                game_over = False
                show_ai_now = False
                wait_frames = 0

    # Handle waiting between rounds
    if wait_frames > 0:
        wait_frames -= 1
        if wait_frames == 0 and not game_over:
            ai_prediction_made = False
            ai_move = "nothing"
            sequence, early_sequence = [], []
            move_counter = 0
            prev_move = None
            show_ai_now = False

    cv2.imshow("Rock Paper Scissors", ui_frame)

    if not hasattr(cv2, 'callback_set'):
        if cv2.getWindowProperty("Rock Paper Scissors", cv2.WND_PROP_VISIBLE) >= 1:
            cv2.setMouseCallback("Rock Paper Scissors", mouse_callback)
            cv2.callback_set = True

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()






'''
    # --- UI Drawing START ---
    # White background
    ui_frame = np.ones((600, 900, 3), dtype=np.uint8) * 255
    ui_frame = ui_frame.astype(np.uint8)

    # Header
    cv2.putText(ui_frame, "ROCK PAPER SCISSORS", (180, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 0), 3)

    # Player Feed
    player_display = cv2.resize(frame, (300, 300))
    cv2.rectangle(ui_frame, (100, 100), (400, 400), (0, 0, 0), 2)  # Border
    ui_frame[100:400, 100:400] = player_display
    cv2.putText(ui_frame, "You", (220, 430), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

    # AI Display
    ai_display = ai_images[last_ai_move if show_ai_now else "nothing"]
    cv2.rectangle(ui_frame, (500, 100), (800, 400), (0, 0, 0), 2)  # Border
    ui_frame[100:400, 500:800] = ai_display
    cv2.putText(ui_frame, "AI", (630, 430), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

    # Score
    cv2.putText(ui_frame, f"Score: You {player_score} - {ai_score} AI", (280, 470), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 0), 2)

    # Result Message
    if last_result_text:
        cv2.putText(ui_frame, last_result_text, (250, 510), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 0), 3)

    # Restart Button
    restart_button_coords = (350, 540, 550, 570)
    if last_result_text:
        cv2.rectangle(ui_frame, (restart_button_coords[0], restart_button_coords[1]),
                    (restart_button_coords[2], restart_button_coords[3]), (0, 0, 0), 2)
        cv2.putText(ui_frame, "RESTART", (restart_button_coords[0] + 20, restart_button_coords[3] - 7),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)

    # --- UI Drawing ENDING ---
'''
    