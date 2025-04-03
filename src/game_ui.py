import cv2
import mediapipe as mp
import numpy as np
import random
import time
import threading
import tkinter as tk
from PIL import Image, ImageTk

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.75, min_tracking_confidence=0.75)

# Possible AI moves
MOVES = ["Rock", "Paper", "Scissors"]
import os

# Get the absolute path to the "assets" folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Get the directory of the current script
ASSETS_DIR = os.path.join(BASE_DIR, "..", "assets")  # Move up one level and go into "assets"

ICONS = {
    "Rock": os.path.join(ASSETS_DIR, "rock.png"),
    "Paper": os.path.join(ASSETS_DIR, "paper.png"),
    "Scissors": os.path.join(ASSETS_DIR, "scissors.png"),
    "Unknown": os.path.join(ASSETS_DIR, "question.png")
}


# Function to check if a finger is extended
def is_finger_extended(finger_tip, finger_mcp, wrist, threshold=0.08):
    return (finger_tip.y < finger_mcp.y) and (abs(finger_tip.y - wrist.y) > threshold)

# Function to recognize the player's hand gesture
def recognize_gesture(hand_landmarks):
    landmarks = hand_landmarks.landmark
    index_tip, index_mcp = landmarks[8], landmarks[5]
    middle_tip, middle_mcp = landmarks[12], landmarks[9]
    ring_tip, ring_mcp = landmarks[16], landmarks[13]
    pinky_tip, pinky_mcp = landmarks[20], landmarks[17]
    wrist = landmarks[0]

    index_extended = is_finger_extended(index_tip, index_mcp, wrist)
    middle_extended = is_finger_extended(middle_tip, middle_mcp, wrist)
    ring_extended = is_finger_extended(ring_tip, ring_mcp, wrist, threshold=0.1)
    pinky_extended = is_finger_extended(pinky_tip, pinky_mcp, wrist, threshold=0.1)

    if not index_extended and not middle_extended and not ring_extended and not pinky_extended:
        return "Rock"
    if index_extended and middle_extended and ring_extended and pinky_extended:
        return "Paper"
    if index_extended and middle_extended and not ring_extended and not pinky_extended:
        return "Scissors"

    return "Unknown"

# Function to determine the winner
def get_winner(player_move, ai_move):
    if player_move == ai_move:
        return "It's a Tie! 😐"
    if (player_move == "Rock" and ai_move == "Scissors") or \
       (player_move == "Paper" and ai_move == "Rock") or \
       (player_move == "Scissors" and ai_move == "Paper"):
        return "You Win! 🎉"
    return "AI Wins! 🤖"

# Tkinter UI Class
class RPSGameUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Rock Paper Scissors Game")

        self.player_move = "Unknown"
        self.ai_move = "Unknown"
        self.winner_text = ""

        # Create Labels for Player & AI
        self.player_label = tk.Label(root, text="Your Move:", font=("Arial", 14))
        self.player_label.pack()
        self.player_img_label = tk.Label(root)
        self.player_img_label.pack()

        self.ai_label = tk.Label(root, text="AI Move:", font=("Arial", 14))
        self.ai_label.pack()
        self.ai_img_label = tk.Label(root)
        self.ai_img_label.pack()

        self.result_label = tk.Label(root, text="", font=("Arial", 16, "bold"))
        self.result_label.pack()

        # Start Button
        self.start_button = tk.Button(root, text="Start Game", command=self.start_game, font=("Arial", 14))
        self.start_button.pack()

        # Load Webcam in Background Thread
        self.running = False
        self.cap = cv2.VideoCapture(0)

    def start_game(self):
        if not self.running:
            self.running = True
            self.start_button.config(text="Stop Game")
            self.update_frame()
        else:
            self.running = False
            self.start_button.config(text="Start Game")
            self.cap.release()
            self.root.quit()

    def update_frame(self):
        if not self.running:
            return
        
        ret, frame = self.cap.read()
        if not ret:
            return

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # Resize the frame to a square shape (e.g., 480x480)
        h, w, _ = frame.shape
        size = min(h, w)
        frame = cv2.resize(frame, (size, size))  # Make it square

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)

        recognized_move = "Unknown"

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                recognized_move = recognize_gesture(hand_landmarks)

        if recognized_move != self.player_move and recognized_move != "Unknown":
            self.player_move = recognized_move
            self.ai_move = random.choice(MOVES)
            self.winner_text = get_winner(self.player_move, self.ai_move)
            self.update_ui()

        # Show Frame in Tkinter Window
        cv2.imshow("Rock Paper Scissors - Camera Feed", frame)

        self.root.after(50, self.update_frame)

    def update_ui(self):
        # Update player image
        player_img = Image.open(ICONS[self.player_move])
        player_img = player_img.resize((100, 100), Image.LANCZOS)  # ✅ Use LANCZOS instead of ANTIALIAS
        self.player_img = ImageTk.PhotoImage(player_img)
        self.player_img_label.config(image=self.player_img)

        # Update AI image
        ai_img = Image.open(ICONS[self.ai_move])
        ai_img = ai_img.resize((100, 100), Image.LANCZOS)  # ✅ Use LANCZOS
        self.ai_img = ImageTk.PhotoImage(ai_img)
        self.ai_img_label.config(image=self.ai_img)

        # Update Result
        self.result_label.config(text=self.winner_text, fg="green" if "Win" in self.winner_text else "red")



# Start the game UI
root = tk.Tk()
game = RPSGameUI(root)
root.mainloop()
