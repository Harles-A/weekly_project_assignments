from filefifo import Filefifo

def find_peaks(filename, sample_rate=250):
    data = Filefifo(10, name=filename)
    
    prev_value = data.get()
    current_value = data.get()
    
    if prev_value is None or current_value is None:
        print("Error: No data!")
        return
    
    peak_indices = []
    index = 1

    while True:
        next_value = data.get()
        if next_value is None:
            break

        print(f"Index {index}: prev={prev_value}, current={current_value}, next={next_value}")

        if prev_value < current_value > next_value:
            print(f"Peak detected at index {index}")
            peak_indices.append(index)

        prev_value = current_value
        current_value = next_value
        index += 1

    if len(peak_indices) < 3:
        print("Not enough peaks detected.")
        return

    intervals_samples = [peak_indices[i+1] - peak_indices[i] for i in range(len(peak_indices) - 1)]
    intervals_seconds = [interval / sample_rate for interval in intervals_samples]

    average_interval_seconds = sum(intervals_seconds) / len(intervals_seconds)
    frequency = 1 / average_interval_seconds if average_interval_seconds != 0 else 0

    print(f"Intervals (samples): {intervals_samples[:3]}, Intervals (seconds): {intervals_seconds[:3]}, Frequency: {frequency:.2f} Hz")

find_peaks('capture_250Hz_01.txt')
