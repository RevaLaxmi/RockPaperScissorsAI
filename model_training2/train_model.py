import os
import numpy as np
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.utils import to_categorical

# Settings
DATA_PATH = os.path.join('gesture_data2')
ACTIONS = ['rock', 'paper', 'scissors', 'nothing']
SEQUENCE_LENGTH = 30

# 1. Load data
sequences, labels = [], []

for action_idx, action in enumerate(ACTIONS):
    action_folder = os.path.join(DATA_PATH, action)
    for filename in os.listdir(action_folder):
        filepath = os.path.join(action_folder, filename)
        sequence = np.load(filepath)
        if sequence.shape == (SEQUENCE_LENGTH, 63):  # Sanity check
            sequences.append(sequence)
            labels.append(action_idx)

X = np.array(sequences)
y = to_categorical(labels).astype(int)

# 2. Split dataset
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1)

# 3. Define the LSTM model
model = Sequential()
model.add(LSTM(64, return_sequences=True, activation='relu', input_shape=(SEQUENCE_LENGTH, 63)))
model.add(LSTM(64, return_sequences=False, activation='relu'))
model.add(Dense(64, activation='relu'))
model.add(Dense(32, activation='relu'))
model.add(Dense(len(ACTIONS), activation='softmax'))

# 4. Compile and train
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
model.fit(X_train, y_train, epochs=30, validation_data=(X_test, y_test))

# 5. Save the model
model.save("gesture_model2.keras")
print("✅ Model trained and saved as gesture_model2.keras")
