import time
import windfreak
import random
import csv

# Define the frequency range
start_freq = 2.69e9  # 2.69 GHz
freq_step = 3.6e6  # 3.6 MHz step size
averages = 1
num_frequencies = 101

# Generate the list of frequencies
frequencies = [start_freq + i * freq_step for i in range(num_frequencies)]


def main():
    devpath = "/dev/ttyAMC0"
    frequency_matrix = []  # To store each shuffled frequency array
    time_tag_matrix = []
    currmeasmat = []

    synth = None
    try:
        # Initialize the SynthHD device
        synth = windfreak.SynthHD(devpath)
        print("Connected to SynthHD device.")
        synth.init()

        # Enable RF output and set initial parameters
        synth[1].enable = False
        synth[1].power = 0  # Power in dBm

        reference = time.time()

        # Loop through frequencies with averaging
        for _ in range(averages):
            # Shuffle frequencies for each iteration
            random.shuffle(frequencies)
            frequency_matrix.append(frequencies[:])  # Add the current shuffled array
            '''start_time = time.time()  # Record the start time
            example_command()         # Run the command
            end_time = time.time()    # Record the end time'''
            start_time_avg = time.time()

            for freq in frequencies:
                try:
                    # start_time_initial = time.time()
                    start_time = time.time()
                    meas_time = 0
                    meas_taken = True
                    while meas_time <= 1:
                        if meas_taken:
                            synth[1].enable = True
                            print(f"Setting frequency to {freq / 1e9:.3f} GHz")
                            synth[1].frequency = freq
                            meas_tag = time.time()
                            tag = meas_tag - reference
                            currmeasmat.append(tag)
                        meas_taken = False
                        end_time = time.time()
                        meas_time = end_time - start_time

                    meas_taken = True
                    meas_time = 0
                    start_time = time.time()
                    while meas_time <= 1:
                        if meas_taken:
                            synth[1].enable = False
                        end_time = time.time()
                        meas_time = end_time - start_time
                        meas_taken = False
                    # end_time_initial = time.time()
                    # one_meas = end_time_initial -start_time_initial
                    # print(f"One frequency measurement took {one_meas:.4f} seconds to complete.")
                except Exception as freq_error:
                    print(f"Failed to set frequency {freq / 1e9:.3f} GHz: {freq_error}")

            '''while elapsed_time <= 202.035:
                end_time_avg = time.time()
                elapsed_time = end_time_avg - start_time_avg
            print(f"The average time took {elapsed_time:.4f} seconds to complete.")
            print("starting next average")
            time.sleep(90)'''
            time_tag_matrix.append(currmeasmat[:])
            end_time_avg = time.time()
            elapsed_time = end_time_avg - start_time_avg

        print("Finished cycling through frequencies.")


        '''
            # Export frequency matrix to a CSV file
            output_file = "27225frequency_matrix5.csv"
            with open(output_file, mode="w", newline="") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([f"Freq {i+1} (Hz)" for i in range(num_frequencies)])
                writer.writerows(frequency_matrix)
            print(f"Frequency matrix saved to {output_file}")
    
            # Export time tag matrix to a CSV file
            output_file = "27225timetag5.csv"
            with open(output_file, mode="w", newline="") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([f"time {i + 1} (Hz)" for i in range(num_frequencies)])
                writer.writerows(time_tag_matrix)
            print(f"time tag saved to {output_file}")
        '''

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
# Ensure the device is properly closed and RF output is off
        if synth is not None:
            try:
                synth[1].enable = False  # Disable RF output
                synth[1].rf_on = False
                synth.close()
                print("SynthHD device disconnected.")
            except Exception as close_error:
                print(f"Error while closing device: {close_error}")

if __name__ == "__main__":
    main()

