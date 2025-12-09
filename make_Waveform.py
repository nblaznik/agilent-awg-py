import numpy as np
import matplotlib.pyplot as plt

# Parameters for the sawtooth wave
frequency = 10_000  # Frequency of the waveform in Hz
sample_rate = 1_000_000  # Sample rate in samples per second
duration = 1 / frequency  # Duration of one period (since f = 1 / T)
num_points = int(sample_rate * duration)  # Total points for one waveform cycle
min_value = 0.5  # Minimum voltage level
max_value = 0.9  # Maximum voltage level

# To create a symmetrical waveform, we'll make a triangular waveform, where the signal ramps up to the maximum value
# and then ramps down to the minimum in each cycle, giving it a symmetrical "sawtooth" appearance.
num_oscillations = 10

# Generate a single symmetric (triangular) waveform cycle
x_half = np.linspace(0, 1, num_points // 2, endpoint=False)  # Half cycle for ramp up
y_up = min_value + (max_value - min_value) * x_half  # Ramp up
y_down = max_value - (max_value - min_value) * x_half  # Ramp down

# Concatenate up and down ramps for a full symmetric cycle
y_symmetric = np.concatenate([y_up, y_down])

# Repeat the waveform to display 100 oscillations
y_repeated_symmetric = np.tile(y_symmetric, num_oscillations)
t_symmetric = np.linspace(0, num_oscillations * duration, num_oscillations * len(y_symmetric), endpoint=False)

# Plot the symmetric waveform
plt.figure(figsize=(12, 6))
plt.plot(t_symmetric, y_repeated_symmetric)
plt.title("Symmetrical Sawtooth (Triangular) Waveform (100 Oscillations)")
plt.xlabel("Time (s)")
plt.ylabel("Amplitude (V)")
plt.grid(True)
plt.show()

