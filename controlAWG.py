import pyvisa as visa
import os
from datetime import datetime
from time import sleep
import numpy as np

# os.system('clear')
# stimes = [0, 3, 5, 10, 15, 20, 25, 30, 40, 50, 100, 200]
# for sweep_time in stimes:
# # ------------------ SETTINGS -------------------#
# sweep_time = 65e-3
# start_freq = 4e6
# stop_freq = 2e6
# ampl = 190e-3 # last time with james we did it at 210   7.07V amplitude
# holdtime = 0 
# returntime = 0
# # -----------------------------------------------#

sweep_time = 20e-3
    
# ------------------ SETTINGS -------------------#
# sweep_time = 20e-3
start_freq = 2.5e6
stop_freq = 1e6
ampl = 90e-3 # 
holdtime = 0 #100e-3
returntime = 0 #80e-3 #80e-3
# -----------------------------------------------#

rm = visa.ResourceManager()

if len(rm.list_resources()) > 0:
    print("Found Device(s) at: ", rm.list_resources())

else:
    print("No devices found.")
    quit()

print(f"Setting the sweep time to {sweep_time*1000} ms")
print(f"Setting the sweep start frequency to {start_freq/1e6} MHz")
print(f"Setting the sweep stop frequency to {stop_freq/1e6} MHz")
print(f"Setting the amplitude to {ampl*1000} mVrms")
print(f"Setting the hold time to {holdtime*1000} ms")
print(f"Setting the return time to {returntime*1000} ms")


# cont = input("Press enter to continue, or q to abort.")
#
# if cont == "q":
#     print("Aborted.")
#     quit()


awg = rm.open_resource('USB0::2391::9479::MY52100652::0::INSTR')
awg.write(f'SOURce1:SWEep:TIME {sweep_time}')
awg.write(f'SOURce1:FREQuency:STARt {start_freq}')
awg.write(f'SOURce1:FREQuency:STOP {stop_freq}')
awg.write(f'SOURce1:VOLTage {ampl}')
awg.write(f'SOURce1:SWEep:HTIMe {holdtime}')
awg.write(f'SOURce1:SWEep:RTIMe {returntime}')


print("All correctly set, and saved.")

def latestRunToday():
    # Save the largest runID, to be used for comparison for the live update
    # Get today's date, formatted
    date = datetime.now()
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
    return output

## Save parameters.
now = datetime.now()
date = now.strftime("%Y%m%d")
time = now.strftime("%H:%M:%S")
last_run = latestRunToday()

# Appending to file
with open(f"/storage/spinflip_log/{date}", 'a') as file1:
    file1.write(f"Spinflip Params at {time}, setting for {str(int(last_run) + 1).zfill(4)} and onwards. \n")
    file1.write(f"Setting the sweep time to {sweep_time * 1000} ms\n")
    file1.write(f"Setting the sweep start frequency to {start_freq / 1e6} MHz\n")
    file1.write(f"Setting the sweep stop frequency to {stop_freq / 1e6} MHz\n")
    file1.write(f"Setting the amplitude to {ampl * 1000} mVrms\n")
    file1.write(f"Setting the hold time to {holdtime * 1000} ms\n")
    file1.write(f"Setting the return time to {returntime * 1000} ms\n")
    file1.write("-----------------------------------------------------------------------\n\n\n")

awg.close()
print()
print()