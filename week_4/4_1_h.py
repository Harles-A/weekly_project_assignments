from filefifo import Filefifo 
import time 

SAMPLE_RATE = 250 
# Set a minimum interval between detected peaks. For example, if set to 60 samples,
# that means a minimum gap of 60/250 = 0.24 seconds between beats, allowing up to 250 BPM.
MIN_INTERVAL = 60
# OFFSET is the number of units above the calculated baseline that a peak must exceed
# to be considered a true heartbeat. (You may need to adjust this based on the signal amplitude.)
OFFSET = 10
NUM_BPM_VALUES = 20  

fifo = Filefifo(100, name="capture_250Hz_03.txt")

# We maintain a moving window of a fixed number of samples to calculate a dynamic baseline of the signal.
baseline_length = 250
baseline_buffer = []  # This list will store the most recent 250 samples.

prev_sample = None         # To store the previous sample for slope calculation.
last_peak_index = None     # The sample index where the last valid peak was detected (None means no peak yet).
bpm_values = []            # List to store calculated heart rate values (in BPM).
current_index = 0          # Counter for the total number of samples processed.

rising = False             # Indicates if the signal is currently rising.
peak_candidate = None      # Holds the highest value during a rising phase.
candidate_index = None     # Holds the sample index corresponding to the candidate peak.

while len(bpm_values) < NUM_BPM_VALUES:
    try:
        sample = fifo.get() 
    except:
        break  # If an error occurs (for example, end-of-file), exit the loop.

    current_index += 1  # Increment the sample counter.

    # Update the Baseline Buffer.
    # We use the last 'baseline_length' samples to compute a running average as our baseline.
    if len(baseline_buffer) < baseline_length:
        baseline_buffer.append(sample)
    else:
        baseline_buffer.pop(0)     # Remove the oldest sample.
        baseline_buffer.append(sample)  # Add the new sample.

    # Compute the baseline as the arithmetic mean of the buffer.
    baseline = sum(baseline_buffer) / len(baseline_buffer)
    # Set a dynamic threshold that is OFFSET units above the baseline.
    threshold = baseline + OFFSET

    # Slope Detection for Peak Detection.
    # If this is the first sample, initialize prev_sample and continue.
    if prev_sample is None:
        prev_sample = sample
        continue

    # Calculate the difference (slope) between the current sample and the previous sample.
    diff = sample - prev_sample

    if diff > 0:
        # When the difference is positive, the signal is rising.
        rising = True
        # Update the candidate peak: if no candidate yet or if the current sample is higher than the stored candidate.
        if peak_candidate is None or sample > peak_candidate:
            peak_candidate = sample
            candidate_index = current_index
    elif rising:
        # If we were in a rising phase, but now diff is ≤0, indicating a possible turning point (peak).
        # Check if the candidate (the highest point during the rising phase) qualifies as a valid peak.
        if peak_candidate is not None and peak_candidate > threshold:
            if last_peak_index is None:
                # First valid peak detected, just store the index without calculating BPM
                last_peak_index = candidate_index
                #debug info
#                 print("First peak detected at index:", candidate_index,
#                       "Baseline:", baseline,
#                       "Threshold:", threshold)
            elif (candidate_index - last_peak_index) >= MIN_INTERVAL:
                interval = candidate_index - last_peak_index  # Interval in samples between peaks.
                # Calculate BPM
                bpm = int(60 * SAMPLE_RATE / interval)
                bpm_values.append(bpm)  # Store the calculated BPM.
                # debug information:
#                 print("Peak detected at index:", candidate_index,
#                       "Interval (samples):", interval,
#                       "Calculated BPM:", bpm,
#                       "Baseline:", baseline,
#                       "Threshold:", threshold)
                # Update last_peak_index so that this peak won't be counted again.
                last_peak_index = candidate_index

        # Reset the rising phase state once the peak is processed.
        rising = False
        peak_candidate = None
        candidate_index = None

    # Prepare for next iteration.
    prev_sample = sample

print("Detected BPM values:", bpm_values)
