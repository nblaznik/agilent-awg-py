import pyvisa as visa
import numpy as numpy
import argparse
import os
import sys 
import datetime

parser = argparse.ArgumentParser()
parser.add_argument('-o', )
args, unknown = parser.parse_known_args(sys.argv[1:])

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



offset = args.o
last = latestRunToday()[1]

# Start Resources
rm = visa.ResourceManager()
awg = rm.open_resource('USB0::2391::9479::MY52100761::0::INSTR')


awg.write(f"SOURce1:FREQuency {offset}")

print(f"For shots {last}")
print(f"Written voltage offset of {offset}")
print("----------")


