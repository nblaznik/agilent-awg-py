import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button

def generate_center_weighted_triangle(alpha=2.0, 
                                      num_steps_rise=1500, num_steps_fall=1500, 
                                      amp_min=-1.0, amp_max=1.0,
                                      f1=20e3, sampling_rate=160e6):
    """
    Builds a stepped triangular wave (amp_min -> amp_max -> amp_min) 
    in one period, with segment durations peaked near the center amplitude.
    alpha controls how sharply the time distribution is weighted.
    """
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

    return time_vals, amp_vals, T_waveform

def main():
    alpha_init = 2.0
    time_vals, amp_vals, T_waveform = generate_center_weighted_triangle(alpha=alpha_init)

    fig, ax = plt.subplots()
    plt.subplots_adjust(left=0.1, bottom=0.25)

    line, = ax.plot(time_vals, amp_vals, drawstyle='steps-post')
    ax.set_xlim(0, T_waveform)
    ax.set_ylim(-1.1, 1.1)
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Amplitude')
    ax.set_title(f'Center-Weighted Triangular Wave (alpha={alpha_init:.2f})')

    # Slider
    slider_ax = plt.axes([0.15, 0.1, 0.65, 0.03])
    alpha_slider = Slider(
        ax=slider_ax,
        label='Alpha',
        valmin=0.2,
        valmax=5.0,
        valinit=alpha_init,
        valstep=0.1,
        color='lightgoldenrodyellow'
    )

    def update_alpha(val):
        alpha_val = alpha_slider.val
        t_vals, a_vals, T_waveform2 = generate_center_weighted_triangle(alpha=alpha_val)
        line.set_xdata(t_vals)
        line.set_ydata(a_vals)
        ax.set_xlim(0, T_waveform2)
        ax.set_ylim(a_vals.min() - 0.1, a_vals.max() + 0.1)
        ax.set_title(f'Center-Weighted Triangular Wave (alpha={alpha_val:.2f})')
        fig.canvas.draw_idle()

    alpha_slider.on_changed(update_alpha)

    # Button to save data
    button_ax = plt.axes([0.83, 0.05, 0.1, 0.04])
    save_button = Button(button_ax, 'Save Wave', color='lightgoldenrodyellow', hovercolor='0.975')

    def save_wave(event):
        # Get current amplitude data
        y_data = line.get_ydata()
        # Also get the current alpha
        alpha_val = alpha_slider.val
        # Format the filename to include alpha
        filename = f"my_amp_vals_alpha_{alpha_val:.2f}.npy"
        np.save(filename, y_data)
        print(f"Wave saved to '{filename}'")

    save_button.on_clicked(save_wave)

    plt.show()

if __name__ == "__main__":
    main()
