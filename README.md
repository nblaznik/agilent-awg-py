# Agilent AWG Control

Small Python helper for communicating with an Agilent AWG used as the RF source for the AOM in the optical dipole trap. It provides simple calls for setting frequency, amplitude, and enabling the output. Communication uses SCPI over VISA.

## Setup

You'll need PyVISA to ensure a VISA backend is available:

    pip install pyvisa

## Notes

The code was written for routine control of the ODT AOM driver and includes only the functions needed for that task.
