from filefifo import Filefifo

# The first parameter (10) is a dummy value to keep the interface consistent with the live version.
# The 'name' parameter specifies the filename from which data will be read. We use 'capture_250Hz_03.txt' because it is the best!
data_fifo = Filefifo(10, name='capture_250Hz_03.txt')

# Data is sampled at 250Hz, a.ka there are 250 data points (samples) per second.
sample_rate = 250

# Initialize an empty list to store the sample indices at which a positive peak is detected.
peaks = []

# Define the minimum number of samples that must pass between detected peaks.
# We use 0.2 seconds as the minimum interval( 0.2 seconds * 250 samples/sec = 50 samples). Could easily increase it but should be fine as is.
min_interval = int(0.2 * sample_rate)

# Initialize the index of the last detected peak.
# Setting this to a negative value (-min_interval) ensures the first peak detected will always pass the interval check.
last_peak_index = -min_interval

# This variable serves as a sample index.
sample_index = 0

# Start the sliding window for peak detection.
# Read the first sample from the Filefifo and store it as the previous sample.
previous_sample = data_fifo.get()

# Read the second sample from the Filefifo and store it as the current sample.
current_sample = data_fifo.get()

# Since we have read two samples, update the sample index by 2.
sample_index += 2

# Enter a loop to detect peaks.
# The loop will continue until we have detected at least 4 peaks.
while len(peaks) < 4:
    # Read the next sample from the Filefifo.
    # This sample will be used as the "next" sample in our sliding window.
    next_sample = data_fifo.get()

    # Increment the sample index to account for the new sample.
    sample_index += 1

    # Check for a positive peak in the current window of three samples.
    # A positive peak is identified when the current sample is greater than both its neighboring samples.
    if previous_sample <= current_sample > next_sample:
        # If a peak is detected, verify that enough samples have passed since the last detected peak.
        # This helps avoid detecting multiple peaks that are too close together due to noise.
        if (sample_index - 1 - last_peak_index) >= min_interval:
            # If the time interval check passes, record the index of the current sample as a peak.
            # (sample_index - 1) is the index of curr_sample.
            peaks.append(sample_index - 1)

            # Update last_peak_index to the current peak's index for future comparisons.
            last_peak_index = sample_index - 1

    # Slide the window forward:
    # The current sample becomes the previous sample.
    # The next sample becomes the current sample.
    previous_sample = current_sample
    current_sample = next_sample

# After the loop ends, we have detected at least 4 peaks.
# Now, calculate the intervals between successive peaks.

# Create a list of differences between consecutive peak indices.
# This list represents the number of samples between each pair of peaks.
intervals_samples = [peaks[i] - peaks[i - 1] for i in range(1, len(peaks))]

# Convert the peak-to-peak intervals from samples to seconds.
# Dividing each interval by the sample rate (250 samples per second) converts it into seconds.
intervals_seconds = [interval / sample_rate for interval in intervals_samples]

# Calculate the frequency of the signal based on the detected intervals.
if intervals_samples:
    # Compute the average interval (in samples) between peaks.
    avg_interval = sum(intervals_samples) / len(intervals_samples)

    # The frequency (in Hertz) is determined by dividing the sample rate by the average interval.
    # This works because the average interval represents the period (in samples) of one full cycle.
    frequency = sample_rate / avg_interval

# Print the intervals between peaks in number of samples.
print("Peak-to-peak intervals (samples):", intervals_samples)

# Print the intervals between peaks in seconds.
print("Peak-to-peak intervals (seconds):", intervals_seconds)

# Print the calculated frequency of the signal in Hertz.
print("Calculated Frequency (Hz):", frequency)

