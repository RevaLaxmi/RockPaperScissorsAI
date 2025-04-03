# src2/ai_opponent.py

import random

class AI_Opponent:
    def __init__(self):
        self.choices = ["rock", "paper", "scissors"]
        self.ai_move = "Waiting..."  # Default AI state
        self.last_valid_player_move = None  # Track last valid player move

    def get_winner(self, player_move):
        if player_move is None or player_move == "unknown":  # No move detected
            self.ai_move = "Waiting..."  # AI also waits
            return self.ai_move, "Waiting..."

        if player_move != self.last_valid_player_move:
            self.ai_move = random.choice(self.choices)  # AI makes a new move
            self.last_valid_player_move = player_move  # Lock the last move

        winner = self._determine_winner(player_move, self.ai_move)
        return self.ai_move, winner
    
    def _determine_winner(self, player, ai):
        winning_combos = {
            "rock": "scissors",
            "scissors": "paper",
            "paper": "rock"
        }
        if player == ai:
            return "Draw"
        return "Player Wins" if winning_combos[player] == ai else "AI Wins"
