import os
import numpy as np
import tensorflow as tf
from sklearn.model_selection import train_test_split

DATA_PATH = "gesture_data2"
SEQUENCE_LENGTH = 15  # shorter for fast response
LABELS = ["rock", "paper", "scissors", "nothing"]

# Load data
sequences, labels = [], []
for label in LABELS:
    folder_path = os.path.join(DATA_PATH, label)
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        data = np.load(file_path)
        if data.shape[0] >= SEQUENCE_LENGTH:
            for i in range(0, data.shape[0] - SEQUENCE_LENGTH + 1, SEQUENCE_LENGTH):
                sequence = data[i:i+SEQUENCE_LENGTH]
                sequences.append(sequence)
                labels.append(LABELS.index(label))

X = np.array(sequences)
y = tf.keras.utils.to_categorical(labels).astype(int)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=True)

# Define model
model = tf.keras.models.Sequential([
    tf.keras.layers.LSTM(64, return_sequences=True, activation='relu', input_shape=(SEQUENCE_LENGTH, 63)),
    tf.keras.layers.LSTM(64, return_sequences=False, activation='relu'),
    tf.keras.layers.Dense(64, activation='relu'),
    tf.keras.layers.Dense(32, activation='relu'),
    tf.keras.layers.Dense(len(LABELS), activation='softmax')
])

model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
model.fit(X_train, y_train, epochs=20, validation_data=(X_test, y_test))

model.save("gesture_model_fast.keras")
