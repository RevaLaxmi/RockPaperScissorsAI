# src2/hand_tracking.py
'''
import cv2
import mediapipe as mp

class HandTracker:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands()
        self.mp_draw = mp.solutions.drawing_utils

    def detect(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        return results.multi_hand_landmarks
''' 
    

import cv2
import mediapipe as mp

class HandTracker:
    def __init__(self, min_detection_confidence=0.7):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(min_detection_confidence=min_detection_confidence)
        self.mp_draw = mp.solutions.drawing_utils

    def detect(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        return results.multi_hand_landmarks

    def draw_landmarks(self, frame, hand_landmarks):
        """Draw hand landmarks on the frame"""
        if hand_landmarks:
            for hand in hand_landmarks:
                self.mp_draw.draw_landmarks(frame, hand, self.mp_hands.HAND_CONNECTIONS)

        return frame
