import numpy as np
import pandas as pd

# Define waveform parameters
f1 = 200e3  # 200 kHz
f2 = 50e3   # 50 kHz
sampling_rate = 250e6  # 250 MSa/s (Agilent 33500B max)
T_waveform = 1 / np.gcd(int(f1), int(f2))  # Fundamental period
N_points = int(T_waveform * sampling_rate)  # Number of points for full waveform

# Generate time axis
t = np.linspace(0, T_waveform, N_points, endpoint=False)

# Generate waveform: sin(2π f1 t) * sin(2π f2 t)
waveform = np.sin(2 * np.pi * f1 * t) * np.sin(2 * np.pi * f2 * t)

# Normalize waveform to -1 to 1 range (required for AWG)
waveform = waveform / np.max(np.abs(waveform))

# Create a DataFrame and save as CSV
df = pd.DataFrame({"Time (s)": t, "Amplitude": waveform})
csv_filename = "sin_sin_waveform.csv"
df.to_csv(csv_filename, index=False)

print(f"CSV file saved as {csv_filename}")
