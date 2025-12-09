import pyvisa
import numpy as np
import os 
import time
import matplotlib.pyplot as plt


import numpy as np

wv = 3

if wv == 1:
    f1 = 20e3  # 
    sampling_rate = 160e6  # 160 MSa/s - max
    amplitude = 1
    offset = 0.5
    pval = 20
    #######
    #######
    #######

    T_waveform = 1 / f1  # Fundamental period
    N_points = min(4000, int(T_waveform * sampling_rate))  # Reduce max to 4000 points
    # Generate time axis
    t = np.linspace(0, T_waveform, N_points, endpoint=False)
    waveform = np.sin(2 * np.pi * f1 * t) * abs( np.sin(2 * np.pi * f1 * t) )**pval
    waveform = waveform / np.max(np.abs(waveform)) # make sure it's normalized

    plt.figure()
    plt.plot(waveform)
    plt.show()

elif wv == 2:
    import numpy as np
    import matplotlib.pyplot as plt
    from scipy.signal import sawtooth

    # Parameters
    f1 = 20e3
    sampling_rate = 160e6
    amplitude = 1.0  # Peak amplitude of the sawtooth
    num_steps = 15   # Number of quantized amplitude levels
    offset = 3

    # Time vector for one period
    T_waveform = 1 / f1
    N_points = min(4000, int(T_waveform * sampling_rate))
    t = np.linspace(0, T_waveform, N_points, endpoint=False)
    wave_saw = (sawtooth(2 * np.pi * f1 * t, width=0.5))  
    min_val = wave_saw.min()  
    max_val = wave_saw.max() 

    step_size = (max_val - min_val) / (num_steps - 1)
    wave_saw_stepped = min_val + np.round((wave_saw - min_val) / step_size) * step_size

    np.save("wave_saw_stepped.npy", wave_saw_stepped)
    
    # Plot the results
    plt.figure()
    plt.plot(t, wave_saw, label='Continuous Sawtooth (0 to amplitude)')
    plt.plot(t, wave_saw_stepped, label='Stepped Sawtooth')

    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude')
    plt.legend()
    plt.show()

elif wv == 3:
    # -----------------
    # User Parameters
    # -----------------
    f1 = 20e3                     # Wave frequency
    sampling_rate = 160e6         # Samples per second
    T_waveform = 1 / f1           # One period
    N_points = int(T_waveform * sampling_rate)

    amp_min, amp_max = -1.0, 1.0  # Triangular wave goes from -1 to +1
    num_steps_rise = 200           # Number of segments in the rising half
    num_steps_fall = 200          # Number of segments in the falling half

    # This single parameter 'alpha' controls the "steepness" of the time distribution.
    # - alpha = 1 makes a linear taper from center to edges.
    # - alpha = 2 (parabolic) is sharper near the center, quicker drop near edges.
    # - alpha > 2 is even more "peaked" in the center.
    # - alpha < 1 flattens the distribution, etc.
    alpha = 0.00001

    # -----------------
    # A helper function to compute segment durations with a single 'alpha' parameter
    # -----------------
    def compute_weights(num_steps, alpha, half_period):
        """
        Return an array of length 'num_steps' giving the time duration
        of each segment. The durations are heavier near the middle index,
        controlled by 'alpha', and the sum of durations = half_period.
        """
        i_array = np.arange(num_steps)                # 0,1,2,...(num_steps-1)
        mid_idx = (num_steps - 1) / 2.0

        # A simple "peak in the center" weighting:
        #  w[i] = 1 - (|i-mid_idx|/mid_idx)^alpha
        # The higher alpha is, the faster it drops near edges, so the center is emphasized.
        w = 1.0 - (np.abs(i_array - mid_idx) / mid_idx) ** alpha

        # Clamp negatives to zero (just in case):
        w[w < 0] = 0

        # Scale so that the sum of w equals half_period:
        w *= half_period / np.sum(w)
        return w

    # -----------------
    # Build the Rising Half (amp_min -> amp_max)
    # -----------------
    w_rise = compute_weights(num_steps_rise, alpha, T_waveform / 2)
    rising_amps = np.linspace(amp_min, amp_max, num_steps_rise + 1)

    time_vals = []
    amp_vals  = []
    t_accum   = 0.0

    # Loop over each segment in the rising half
    for seg_idx in range(num_steps_rise):
        amp_segment = rising_amps[seg_idx + 1]  # next amplitude as the step level
        n_segment   = int(round(w_rise[seg_idx] * sampling_rate))
        t_segment   = np.linspace(t_accum, t_accum + w_rise[seg_idx], n_segment, endpoint=False)
        a_segment   = np.full(n_segment, amp_segment)
        
        time_vals.append(t_segment)
        amp_vals.append(a_segment)
        
        t_accum += w_rise[seg_idx]

    # -----------------
    # Build the Falling Half (amp_max -> amp_min)
    # -----------------
    w_fall = compute_weights(num_steps_fall, alpha, T_waveform / 2)
    falling_amps = np.linspace(amp_max, amp_min, num_steps_fall + 1)

    for seg_idx in range(num_steps_fall):
        amp_segment = falling_amps[seg_idx + 1]  
        n_segment   = int(round(w_fall[seg_idx] * sampling_rate))
        t_segment   = np.linspace(t_accum, t_accum + w_fall[seg_idx], n_segment, endpoint=False)
        a_segment   = np.full(n_segment, amp_segment)
        
        time_vals.append(t_segment)
        amp_vals.append(a_segment)
        
        t_accum += w_fall[seg_idx]

    # -----------------
    # Concatenate and Trim
    # -----------------
    time_vals = np.concatenate(time_vals)
    amp_vals  = np.concatenate(amp_vals)

    # Ensure exactly one period worth of points
    if len(time_vals) > N_points:
        time_vals = time_vals[:N_points]
        amp_vals  = amp_vals[:N_points]

    # -----------------
    # Plot the Result
    # -----------------
    plt.figure()
    plt.plot(time_vals, amp_vals, drawstyle='steps-post')
    plt.xlim(0, T_waveform)
    plt.ylim(amp_min - 0.1, amp_max + 0.1)
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude')
    plt.title(f'Triangular Wave with Center-Weighted Segments (alpha={alpha})')
    plt.show()

