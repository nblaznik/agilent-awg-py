import pyvisa
import numpy as np
import os 
import datetime
import time
# from scipy.signal import sawtooth


def latestRunToday():
    # Save the largest runID, to be used for comparison for the live update
    # Get today's date, formatted
    date = datetime.datetime.now()
    datestring = str(date.year) + str(date.month).zfill(2) + str(date.day).zfill(2)
    path = "/storage/data/" + datestring + "/"
    if os.path.exists(path):
        dirList = [x for x in os.listdir(path) if os.path.isdir(path + x)]
        if len(dirList) > 0:
            output = sorted(dirList)[-1]
        else:
            output = None
    else:
        output = None
    return datestring, output


# The functions should be generated -1 to +1 I believe, and offset and amplitude are set afterwards. 
def wavefront_spikysine(f1, sampling_rate, pval=20):
    T_waveform = 1 / f1  # Fundamental period
    N_points = min(4000, int(T_waveform * sampling_rate))  # Reduce max to 4000 points
    # Generate time axis
    t = np.linspace(0, T_waveform, N_points, endpoint=False)
    waveform = np.sin(2 * np.pi * f1 * t) * abs( np.sin(2 * np.pi * f1 * t) )**pval
    waveform = waveform / np.max(np.abs(waveform)) # make sure it's normalized
    return waveform, N_points, "SpikySine"

def wavefront_stepped_sawtooth(f1, sampling_rate):
    T_waveform = 1 / f1
    N_points = min(4000, int(T_waveform * sampling_rate))
    t = np.linspace(0, T_waveform, N_points, endpoint=False)

    # wave_saw_stepped = np.load("wave_saw_stepped.npy")
    wave_saw_stepped = np.load("my_amp_vals_alpha_1.40.npy")
    # wave_saw = (sawtooth(2 * np.pi * f1 * t, width=0.5))  
    # min_val = wave_saw.min()  
    # max_val = wave_saw.max() 

    # step_size = (max_val - min_val) / (num_steps - 1)
    # wave_saw_stepped = min_val + np.round((wave_saw - min_val) / step_size) * step_size
    return wave_saw_stepped, N_points, "wavefront_stepped_sawtooth"

def generate_center_weighted_triangle(f1, sampling_rate, alpha):

    """
    Builds a stepped triangular wave (amp_min -> amp_max -> amp_min) 
    in one period, with segment durations peaked near the center amplitude.
    alpha controls how sharply the time distribution is weighted.
    """

    num_steps_rise=900 
    num_steps_fall=900
    amp_min=-1.0
    amp_max=1.0 
    T_waveform = 1.0 / f1
    N_points   = int(T_waveform * sampling_rate)

    def compute_weights(num_steps, alpha_val, half_period):
        i_array = np.arange(num_steps)  # 0..(num_steps-1)
        mid_idx = (num_steps - 1) / 2.0
        w = 1.0 - (np.abs(i_array - mid_idx) / mid_idx) ** alpha_val
        w[w < 0] = 0
        w *= half_period / np.sum(w)
        return w

    # Rising half
    w_rise = compute_weights(num_steps_rise, alpha, T_waveform / 2)
    rising_amps = np.linspace(amp_min, amp_max, num_steps_rise + 1)

    time_vals = []
    amp_vals  = []
    t_accum   = 0.0

    for seg_idx in range(num_steps_rise):
        amp_segment = rising_amps[seg_idx]  
        n_segment   = int(round(w_rise[seg_idx] * sampling_rate))
        t_segment   = np.linspace(t_accum, t_accum + w_rise[seg_idx], n_segment, endpoint=False)
        a_segment   = np.full(n_segment, amp_segment)
        time_vals.append(t_segment)
        amp_vals.append(a_segment)
        t_accum += w_rise[seg_idx]

    # Falling half
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

    # Concatenate
    time_vals = np.concatenate(time_vals)
    amp_vals  = np.concatenate(amp_vals)

    # Trim if overshoot
    if len(time_vals) > N_points:
        time_vals = time_vals[:N_points]
        amp_vals  = amp_vals[:N_points]

    return amp_vals, N_points, "generate_center_weighted_triangle"

#######
#######
#######
#######
# Connect to the instrument
rm = pyvisa.ResourceManager()
awg = rm.open_resource('USB0::2391::9479::MY52100761::0::INSTR')

f1 = 100e3  
sampling_rate = 160e6   # 160 MSa/s - max
amplitude = 0.1
offset = 0.4
pval = 20               # for spiky sine functions
alpha = 0.001   # Lower alpha means less time at the peaks
#######
#######
#######

# waveform, N_points, f_name = wavefront_spikysine(f1, sampling_rate, pval=20)
# waveform,  N_points, f_name = wavefront_stepped_sawtooth(f1, sampling_rate)
waveform,  N_points, f_name = generate_center_weighted_triangle(f1, sampling_rate, alpha)




#### WRITE TO AWG and SAVE PARAMS. Don't touch 

# Clear volatile memory
awg.write("DATA:VOLATILE:CLEAR")
awg.write("*WAI")  # Wait for completion

# Convert to float values and send
waveform_str = ','.join(map(str, waveform.astype(np.float32)))
awg.write(f"DATA VOLATILE,{waveform_str}")

# Set function generator to use the uploaded waveform
awg.write("FUNC:ARB VOLATILE")
awg.write(f"FUNC:ARB:SRATE {sampling_rate}")  # Set correct sample rate

# f_name = "RegularSineWaveform"
# awg.write("FUNC SIN")  # STO a predefined sin function

awg.write(f"FREQ {sampling_rate / N_points}")  # Ensure correct output frequency
awg.write(f"VOLT {amplitude}")  # Set am5plitude (peak)
awg.write(f"VOLT:OFFS {offset}")  # Set offset
awg.write("OUTPUT ON")  # Enable output

print("Custom waveform uploaded and running!")
date = datetime.datetime.now()
datestring = str(date.year) + str(date.month).zfill(2) + str(date.day).zfill(2)
last = latestRunToday()[1] or 0
print("------------------------------------")
print("----written a custom arb waveform ----")
print(f"Type: {f_name}")
print(f"For shots {int(last)+1} and onwards")
print(f"Written voltage offset of      {offset} V")
print(f"Written voltage amplitude of   {amplitude} V")
print(f"Written frequency of           {f1/1000} kHz")
print(f"p-value of the function        {pval}")
print(f"alpha of the function          {alpha}")
print("----------")

with open(f"/storage/ODT_setuplog/{datestring}.txt", "a") as myfile:
    myfile.write("------------------------------------\n")
    myfile.write("----written a custom arb waveform ----\n")
    myfile.write(f"----Type: {f_name}  ----\n")
    myfile.write(f"For shots {int(last)+1} and onwards\n")
    myfile.write(f"Written voltage offset of      {offset} V\n")
    myfile.write(f"Written voltage amplitude of   {amplitude} V\n")
    myfile.write(f"Written frequency of           {f1/1000} kHz\n")
    myfile.write(f"p-value of the function        {pval}\n")
    myfile.write(f"alpha of the function          {alpha}\n")
    myfile.write("----------\n\n")


# Close connection
awg.close()
