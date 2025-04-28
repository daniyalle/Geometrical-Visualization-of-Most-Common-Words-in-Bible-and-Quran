import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Load the data from the CSV file
data_path =  # Path to the CSV file
data = pd.read_csv(data_path)

# Extract the relevant columns
words = data['word']
frequencies = data['count']
average_Xs = data['avg_xs']
average_Ys = data['avg_ys']
std_dev_Xs = data['std_dev_xs']
std_dev_Ys = data['std_dev_ys']

# Compute the global center as the average of all centroids
global_center_x = np.mean(average_Xs)
global_center_y = np.mean(average_Ys)

# Calculate the mean direction and resultant vector length
delta_x = average_Xs - global_center_x
delta_y = average_Ys - global_center_y
resultant_vector_length = np.sqrt(delta_x ** 2 + delta_y ** 2).mean()

# Calculate angles in degrees
angles_in_degrees = np.degrees(np.arctan2(delta_y, delta_x))


# Function to adjust angles if they're too close
def adjust_angle(angles, min_diff=16):
    # Make a copy of the angles to avoid modifying the original array while iterating
    adjusted_angles = angles.copy()

    # Check for pairs of angles that are too close
    for i in range(len(adjusted_angles)):
        for j in range(i + 1, len(adjusted_angles)):
            while abs(adjusted_angles[i] - adjusted_angles[j]) < min_diff:
                # If the difference is too small, move both angles by the necessary amount
                # Calculate the shift amount to achieve the 5-degree difference
                shift_amount = (min_diff - abs(adjusted_angles[i] - adjusted_angles[j])) / 2
                # Move both angles in the direction of the larger angle
                if adjusted_angles[i] < adjusted_angles[j]:
                    adjusted_angles[i] -= shift_amount
                    adjusted_angles[j] += shift_amount
                else:
                    adjusted_angles[i] += shift_amount
                    adjusted_angles[j] -= shift_amount

    # Now recheck the rest of the angles after the initial adjustment
    for i in range(len(adjusted_angles)):
        for j in range(i + 1, len(adjusted_angles)):
            # If the angles are too close now, only adjust the second one
            if abs(adjusted_angles[i] - adjusted_angles[j]) < min_diff:
                shift_amount = (min_diff - abs(adjusted_angles[i] - adjusted_angles[j])) / 2
                if adjusted_angles[i] < adjusted_angles[j]:
                    adjusted_angles[j] += shift_amount
                else:
                    adjusted_angles[j] -= shift_amount

    return adjusted_angles


# Apply the adjustment function to angles
adjusted_angles = adjust_angle(angles_in_degrees)

# Convert adjusted angles back to new scaled centroids
scale_factor = 10 * resultant_vector_length  #adjustable_number
scaled_centroids = [
    (
        global_center_x + np.cos(np.radians(angle)) * scale_factor,
        global_center_y + np.sin(np.radians(angle)) * scale_factor
    )
    for angle in adjusted_angles
]

# Print angles and adjusted angles for each word
for word, angle, adjusted_angle in zip(words, angles_in_degrees, adjusted_angles):
    print(f"Word: {word}")
    print(f"Original Angle: {angle:.2f} degrees")
    print(f"Adjusted Angle: {adjusted_angle:.2f} degrees")
    print("-" * 30)  # Separator for clarity


# Scaling function for standard deviations
def scale_std_devs(std_devs, scaling_factor):
    scaled_std_devs = np.power(std_devs, scaling_factor)
    scaled_std_devs = scaled_std_devs / max(scaled_std_devs) * max(std_devs)
    return scaled_std_devs

# Adjustable scaling factor
scaling_factor = #adjustable_number

# Apply scaling to std_dev_xs and std_dev_ys
scaled_std_dev_xs = scale_std_devs(std_dev_Xs, scaling_factor)
scaled_std_dev_ys = scale_std_devs(std_dev_Ys, scaling_factor)

# Prepare centroids and fog map
width, height = 1700, 2200
fog_map = np.zeros((height, width))

# Function to add "fog" (Gaussian density) to the heatmap for each word
def add_fog_to_map(fog_map, centroid, scaled_std_dev_x, scaled_std_dev_y, intensity):
    x_centroid, y_centroid = centroid
    y, x = np.indices(fog_map.shape)
    adjusted_std_dev_x = scaled_std_dev_x * 0.5
    adjusted_std_dev_y = scaled_std_dev_y * 0.5

    # Apply a damping factor to reduce intensity without changing radius
    damping_factor = 0.7  # Adjust this value; smaller = less intensity
    intensity *= damping_factor

    fog_density = intensity * np.exp(-((x - x_centroid) ** 2 / (2 * adjusted_std_dev_x ** 2) +
                                       (y - y_centroid) ** 2 / (2 * adjusted_std_dev_y ** 2)))
    fog_map += fog_density
    fog_map = np.clip(fog_map, 0, 1)
    return fog_map

# Normalize frequencies to get intensity
max_frequency = frequencies.max()

# Apply fog for each word using scaled standard deviations
for word, centroid, std_dev_x, std_dev_y, frequency in zip(words, scaled_centroids, scaled_std_dev_xs, scaled_std_dev_ys, frequencies):
    intensity = frequency / max_frequency
    fog_map = add_fog_to_map(fog_map, centroid, std_dev_x, std_dev_y, intensity)

# Apply gamma correction to enhance color range
gamma = 0.8  # Adjust gamma for contrast (0.5 = more range, 1.0 = no change)
frequency_fog_map = np.power(fog_map, gamma)

# Ensure the values in fog_map are between 0 and 1 (normalized)
fog_map_normalized = np.clip(frequency_fog_map, 0, 1)

# Display the fog map as a heatmap with explicit vmin and vmax
plt.imshow(fog_map_normalized, cmap="inferno", interpolation='bilinear', vmin=0, vmax=1)

# Add the words at their new centroid positions with a background
for word, (x, y) in zip(words, scaled_centroids):
    plt.text(
        x, y, word,
        color="white", fontsize=8, ha='center', va='center', alpha=0.8,
        bbox=dict(facecolor='black', edgecolor='none', boxstyle='round,pad=0.3', alpha=0.2)
    )

# Add titles to the axes
plt.xlabel("Width of the Book")
plt.ylabel("Height of the Book")

# Add a color bar to show the actual word frequencies
colorbar = plt.colorbar()
colorbar.set_label('Word Frequency')

# Set the color bar ticks to the range 0 to 3000 (mapped from the normalized range)
colorbar.set_ticks(np.linspace(0, 1, 10))  # Ticks for normalized values
colorbar.set_ticklabels(np.linspace(0, 3000, 10).astype(int))  # Adjust tick labels to reflect the 0-3000 range

# Add a title
plt.title("Scaled Word Fog Heatmap (Quran)")

# Show the plot
plt.show()
