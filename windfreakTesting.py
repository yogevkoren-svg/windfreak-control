"""
Windfreak SynthHD Control Script (Linux)

This script provides an interactive command-line interface to control
a Windfreak SynthHD RF signal generator on a Linux system.

Main features:
---------------
- Linux-compatible serial connection (/dev/ttyAMC0)
- User-selectable pulse sequence:
    1. Single pulse
    2. Pulse train
    3. Continuous wave (CW)
- User-defined number of repetitions
- Optional frequency sweep (min / max / step)
- User-defined RF ON and OFF durations

Typical use cases:
------------------
- NV-center ODMR experiments
- Cell viability RF exposure tests
- General pulsed or CW RF experiments

Requirements:
-------------
- windfreak Python package
- User must have permission to access /dev/ttyAMC0 (dialout group)

Author: Yogev Koren (with ChatGPT)
"""


import time
import windfreak


############################
# Device configuration
############################

# Linux serial device path for the SynthHD
DEVICE_PATH = "/dev/ttyAMC0"

# SynthHD channel to use (1 or 2)
CHANNEL = 1


############################
# User input helper functions
############################

def get_float(prompt):
    """
    Safely request a floating-point number from the user.

    Parameters
    ----------
    prompt : str
        Text shown to the user.

    Returns
    -------
    float
        User-provided numeric value.
    """
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("Invalid input. Please enter a number.")


def get_int(prompt):
    """
    Safely request an integer from the user.

    Parameters
    ----------
    prompt : str
        Text shown to the user.

    Returns
    -------
    int
        User-provided integer value.
    """
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("Invalid input. Please enter an integer.")


############################
# Frequency handling
############################

def generate_frequency_list():
    """
    Ask the user whether to perform a frequency sweep or use a fixed frequency.

    Returns
    -------
    list of float
        List of frequencies in Hz.
    """
    sweep = input("Sweep frequencies? (y/n): ").strip().lower()

    if sweep == "y":
        f_min = get_float("Min frequency (Hz): ")
        f_max = get_float("Max frequency (Hz): ")
        f_step = get_float("Frequency step (Hz): ")

        frequencies = []
        f = f_min
        while f <= f_max + 1e-12:
            frequencies.append(f)
            f += f_step

        return frequencies

    else:
        f = get_float("Fixed frequency (Hz): ")
        return [f]


############################
# Pulse sequence definitions
############################

def single_pulse(synth, frequency, on_time, off_time):
    """
    Apply a single RF pulse at a given frequency.

    RF is turned ON for on_time, then OFF for off_time.

    Parameters
    ----------
    synth : windfreak.SynthHD
        Initialized SynthHD object.
    frequency : float
        Frequency in Hz.
    on_time : float
        RF ON duration in seconds.
    off_time : float
        RF OFF duration in seconds.
    """
    synth[CHANNEL].frequency = frequency
    synth[CHANNEL].enable = True
    time.sleep(on_time)
    synth[CHANNEL].enable = False
    time.sleep(off_time)


def pulse_train(synth, frequency, on_time, off_time, repeats):
    """
    Apply a pulse train at a given frequency.

    Parameters
    ----------
    synth : windfreak.SynthHD
        Initialized SynthHD object.
    frequency : float
        Frequency in Hz.
    on_time : float
        RF ON duration in seconds.
    off_time : float
        RF OFF duration in seconds.
    repeats : int
        Number of pulses.
    """
    synth[CHANNEL].frequency = frequency

    for _ in range(repeats):
        synth[CHANNEL].enable = True
        time.sleep(on_time)
        synth[CHANNEL].enable = False
        time.sleep(off_time)


def continuous_wave(synth, frequency, duration):
    """
    Apply continuous-wave RF for a fixed duration.

    Parameters
    ----------
    synth : windfreak.SynthHD
        Initialized SynthHD object.
    frequency : float
        Frequency in Hz.
    duration : float
        CW duration in seconds.
    """
    synth[CHANNEL].frequency = frequency
    synth[CHANNEL].enable = True
    time.sleep(duration)
    synth[CHANNEL].enable = False


############################
# Main control logic
############################

def main():
    """
    Main entry point for the SynthHD control script.

    Handles:
    - User interaction
    - Device initialization
    - Execution of pulse sequences
    - Safe shutdown of RF output
    """

    print("\n=== Windfreak SynthHD Control (Linux) ===\n")

    # Pulse sequence selection
    print("Choose pulse sequence:")
    print("1 - Single pulse")
    print("2 - Pulse train")
    print("3 - Continuous wave (CW)")
    sequence = get_int("Selection: ")

    # Frequency selection
    frequencies = generate_frequency_list()

    # Timing parameters
    if sequence in (1, 2):
        on_time = get_float("RF ON time (seconds): ")
        off_time = get_float("RF OFF time (seconds): ")

    if sequence == 2:
        pulse_repeats = get_int("Pulses per frequency: ")

    if sequence == 3:
        cw_duration = get_float("CW duration per frequency (seconds): ")

    sequence_repeats = get_int("Number of full sequence repetitions: ")

    ############################
    # Device connection
    ############################

    synth = None
    try:
        synth = windfreak.SynthHD(DEVICE_PATH)
        synth.init()

        # Initial safe configuration
        synth[CHANNEL].power = 0     # dBm
        synth[CHANNEL].enable = False

        print("\nConnected to SynthHD.")
        print("Starting sequence...\n")

        for rep in range(sequence_repeats):
            print(f"--- Sequence {rep + 1}/{sequence_repeats} ---")

            for freq in frequencies:
                print(f"Frequency: {freq / 1e9:.6f} GHz")

                if sequence == 1:
                    single_pulse(synth, freq, on_time, off_time)

                elif sequence == 2:
                    pulse_train(synth, freq, on_time, off_time, pulse_repeats)

                elif sequence == 3:
                    continuous_wave(synth, freq, cw_duration)

        print("\nSequence complete.")

    except Exception as e:
        print(f"\nERROR: {e}")

    finally:
        # Always ensure RF output is OFF before exiting
        if synth is not None:
            try:
                synth[CHANNEL].enable = False
                synth.close()
                print("SynthHD disconnected safely.")
            except Exception as e:
                print(f"Shutdown error: {e}")


############################
# Script entry point
############################

if __name__ == "__main__":
    main()