from filefifo import Filefifo

def scale_signal(filename, sample_rate=250, duration=10):
    data = Filefifo(10, name=filename)
    
    num_samples = 2 * sample_rate
    values = [data.get() for _ in range(num_samples)]
    
    min_val, max_val = min(values), max(values)
    print(f"Min: {min_val}, Max: {max_val}")
    
    num_samples = duration * sample_rate
    scaled_values = []
    
    for _ in range(num_samples):
        value = data.get()
        if value is None:
            break
        
        scaled_value = (value - min_val) / (max_val - min_val) * 100
        scaled_values.append(scaled_value)
        print(scaled_value)

scale_signal('capture_250Hz_01.txt')
