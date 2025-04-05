import numpy as np
import os

# Set paths for dataset
base_path = "gesture_data"
categories = {
    "rock": 29,  # Last file is sample_29.npy
    "paper": 31, # Last file is sample_31.npy
    "scissors": 29 # Last file is sample_29.npy
}

# Data augmentation functions
def add_jitter(data, sigma=0.01):
    return data + np.random.normal(0, sigma, data.shape)

def scale_data(data, scale_range=(0.8, 1.2)):
    scale_factor = np.random.uniform(*scale_range)
    return data * scale_factor

def rotate_data(data):
    # Ensure data is reshaped properly before applying rotation
    data = data.reshape(-1, 3)  # Reshape to (21, 3)
    
    # Small random rotation
    angle = np.random.uniform(-15, 15)  # Rotation angle in degrees
    theta = np.radians(angle)
    
    rotation_matrix = np.array([
        [np.cos(theta), -np.sin(theta), 0],
        [np.sin(theta), np.cos(theta), 0],
        [0, 0, 1]
    ])

    rotated_data = np.dot(data, rotation_matrix)  # Apply rotation
    return rotated_data.flatten()  # Flatten back to original shape (63,)

def flip_data(data):
    # Ensure the data is reshaped properly
    data = data.reshape(-1, 3)  # Reshape to (21, 3)

    # Flip x-coordinates (negate the first column)
    flipped_data = data * np.array([-1, 1, 1])  

    return flipped_data.flatten()  # Flatten back to (63,)


# Augment and save data
for category, last_sample in categories.items():
    category_path = os.path.join(base_path, category)
    
    for i in range(last_sample + 1):  # Go from sample_0 to sample_last
        file_path = os.path.join(category_path, f"sample_{i}.npy")
        
        if os.path.exists(file_path):
            data = np.load(file_path)  # Load original data
            
            augmented_data = [
                add_jitter(data),
                scale_data(data),
                rotate_data(data),
                flip_data(data)
            ]
            
            # Save augmented versions
            for j, aug_data in enumerate(augmented_data):
                save_path = os.path.join(category_path, f"aug_{i}_{j}.npy")
                np.save(save_path, aug_data)

print("Data augmentation complete. Augmented files saved!")
