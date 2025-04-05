import numpy as np
import os
from sklearn.model_selection import train_test_split

# Define dataset path and gestures
DATASET_PATH = "gesture_data"
GESTURES = ["Rock", "Paper", "Scissors"]

X, y = [], []  # Correct initialization

expected_shape = None  # Keep track of the correct shape

# Load data
for label, gesture in enumerate(GESTURES):
    gesture_path = os.path.join(DATASET_PATH, gesture)
    for file in os.listdir(gesture_path):
        if file.endswith(".npy"):
            file_path = os.path.join(gesture_path, file)
            data = np.load(file_path)  

            # Ensure consistent shape
            if expected_shape is None:
                expected_shape = data.shape  # Set the expected shape
            elif data.shape != expected_shape:
                print(f"Skipping {file} due to shape mismatch: {data.shape}")
                continue  # Skip inconsistent files

            X.append(data)
            y.append(label)

# Convert to NumPy arrays
X = np.array(X, dtype=np.float32)  # Ensure numerical data
y = np.array(y, dtype=np.int32)    # Ensure integer labels

# Split dataset
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

# Save correctly formatted arrays
np.save("X_train.npy", X_train)
np.save("y_train.npy", y_train)
np.save("X_val.npy", X_val)
np.save("y_val.npy", y_val)

print("✅ Dataset prepared successfully!")
