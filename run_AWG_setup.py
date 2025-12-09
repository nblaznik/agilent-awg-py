import pyvisa as visa
import numpy as numpy
import argparse
import os
import sys 
import datetime

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


############################## 
# SETTINGS
amplitude = .3
offset = 0.7
frequency = 200_000
##############################


### 
# 0.7 offset + 200k freq + 0 amp + 0.9 cooling works well for a thin trap  
# 0.7 offset + 200k freq + 0.5 amp + 1 


last = latestRunToday()[1]

# Start Resources
rm = visa.ResourceManager()
awg = rm.open_resource('USB0::2391::9479::MY52100761::0::INSTR')
awg.write(f"SOURce1:FREQuency {frequency}")
awg.write(f"SOURce1:VOLTage:AMPLitude {amplitude}")
awg.write(f"SOURce1:VOLTage:OFFSet {offset}")

## Print and save setings
print("------------------------------------")
print(f"For shots {int(last)+1} and onwards")
print(f"Written voltage offset of      {offset} V")
print(f"Written voltage amplitude of   {amplitude} V")
print(f"Written frequency of           {frequency/1000} kHz")
print("----------")

date = datetime.datetime.now()
datestring = str(date.year) + str(date.month).zfill(2) + str(date.day).zfill(2)

with open(f"/storage/ODT_setuplog/{datestring}.txt", "a") as myfile:
    myfile.write("------------------------------------\n")
    myfile.write(f"For shots {int(last)+1} and onwards\n")
    myfile.write(f"Written voltage offset of      {offset} V\n")
    myfile.write(f"Written voltage amplitude of   {amplitude} V\n")
    myfile.write(f"Written frequency of           {frequency/1000} kHz\n")
    myfile.write("----------\n\n")

