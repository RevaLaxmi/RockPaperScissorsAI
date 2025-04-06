# ai_opponent_module.py
import tensorflow as tf
import numpy as np

model = tf.keras.models.load_model("gesture_model_fast.keras")

LABELS = ["rock", "paper", "scissors", "nothing"]

def get_ai_move(input_data):
    prediction = model.predict(input_data, verbose=0)
    return LABELS[np.argmax(prediction)]
