# ai_opponent_module.py
import numpy as np
from tensorflow.keras.models import load_model

model = load_model('gesture_model4.keras')

class_names = ['rock', 'paper', 'scissors', 'nothing']

def get_ai_move(keypoints):  # keypoints shape: (1, 30, 63)
    prediction = model.predict(keypoints, verbose=0)[0]  # Don't wrap in np.array again
    predicted_class = class_names[np.argmax(prediction)]
    return predicted_class
