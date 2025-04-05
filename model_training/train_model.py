import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, BatchNormalization, Input
from tensorflow.keras.regularizers import l2
from tensorflow.keras.callbacks import ReduceLROnPlateau
from tensorflow.keras.utils import to_categorical

# Load dataset
X_train = np.load("X_train.npy")
X_val = np.load("X_val.npy")
y_train = np.load("y_train.npy")
y_val = np.load("y_val.npy")

# Convert labels to categorical
num_classes = len(np.unique(y_train))
y_train = to_categorical(y_train, num_classes)
y_val = to_categorical(y_val, num_classes)

# Build LSTM model
model = Sequential([
    Input(shape=(X_train.shape[1], X_train.shape[2])),
    LSTM(128, return_sequences=True, activation="relu"),
    BatchNormalization(),
    Dropout(0.3),
    
    LSTM(128, activation="relu"),
    BatchNormalization(),
    Dropout(0.3),

    Dense(64, activation="relu", kernel_regularizer=l2(0.001)),
    Dropout(0.3),

    Dense(num_classes, activation="softmax")  # Output layer
])

model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])

# Reduce learning rate when loss stops improving
lr_scheduler = ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=3, verbose=1, min_lr=1e-5)

# Train the model
history = model.fit(X_train, y_train, validation_data=(X_val, y_val),
                    epochs=30, batch_size=16, callbacks=[lr_scheduler])

# Save the trained model
model.save('gesture_model4.keras')

print("Model training complete! Saved as gesture_model.keras")
