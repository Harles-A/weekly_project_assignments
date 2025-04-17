from machine import Pin, I2C 
from filefifo import Filefifo 
from ssd1306 import SSD1306_I2C  
import time    

OLED_WIDTH = 128  
OLED_HEIGHT = 64 
AVG_PER_PIXEL = 5
SAMPLES_PER_FRAME = OLED_WIDTH * AVG_PER_PIXEL 

i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000)
oled = SSD1306_I2C(OLED_WIDTH, OLED_HEIGHT, i2c)

SOURCE_FILE = "capture02_250Hz.txt" 
fifo = Filefifo(100, name=SOURCE_FILE)

def get_scaled_frame(fifo, samples_per_pixel, width):
    """
    Reads (samples_per_pixel * width) raw samples from the FIFO,
    computes the minimum and maximum values in that frame,
    calculates a scaling factor so that the full range maps onto the OLED's vertical pixels,
    averages samples in groups of 'samples_per_pixel', and returns a list of pixel
    y-values (one per horizontal pixel).
    """
    raw_samples = []  # List to store raw samples for the current frame.

    try:
        # Read (samples_per_pixel * width) samples.
        for _ in range(samples_per_pixel * width):
            raw_samples.append(fifo.get())
    except:
        return None  # In case of error, return None.

    # If not enough samples were read, return None.
    if len(raw_samples) < samples_per_pixel * width:
        return None

    # Determine the Scaling Range.
    # Find the minimum and maximum sample values in the frame.
    min_val = min(raw_samples)
    max_val = max(raw_samples)
    if max_val == min_val:
        max_val += 1  # Prevent division by zero if the signal is flat.
    # Calculate the scale factor so that the range [min_val, max_val] is mapped to [0, OLED_HEIGHT - 1].
    scale = (OLED_HEIGHT - 1) / (max_val - min_val)

    frame = []  # This will hold one y-coordinate per horizontal pixel.
    # Process the raw samples in groups of 'samples_per_pixel'.
    for i in range(0, len(raw_samples), samples_per_pixel):
        chunk = raw_samples[i:i + samples_per_pixel]  # Get the current group of samples.
        avg = sum(chunk) // len(chunk)  # Calculate the integer average of the group.
        # Map the average value to the OLED's vertical range:
        # Subtract min_val, multiply by the scale factor.
        y = int((avg - min_val) * scale)
        # Invert the y coordinate because OLED (0,0) is at the top-left and we want higher signal values (i.e., peaks) to appear at the top.
        y = OLED_HEIGHT - 1 - y
        # Ensure that the value lies within the display bounds.
        y = max(0, min(OLED_HEIGHT - 1, y))
        frame.append(y)  # Append the scaled value for this pixel.

    return frame

while True:
    # Get a frame (128 pixel values) from the FIFO.
    frame = get_scaled_frame(fifo, AVG_PER_PIXEL, OLED_WIDTH)
    if frame is None or len(frame) < OLED_WIDTH:
        # If not enough data: clear display and display a "No data" message.
        oled.fill(0)
        oled.text("No data", 30, 30)
        oled.show()
        time.sleep(1)  # Wait a second before retrying.
        continue

    # Clear the OLED before drawing the new frame.
    oled.fill(0)
    # Draw the waveform by connecting successive pixels with lines.
    for x in range(OLED_WIDTH - 1):
        y1 = frame[x]       # y-coordinate at the current x position.
        y2 = frame[x + 1]   # y-coordinate at the next x position.
        oled.line(x, y1, x + 1, y2, 1)  # Draw a line between the two points in white.
    
    oled.show()         # Refresh the OLED display to show the updated waveform.
    time.sleep(0.05)    # Wait a little before updating with the next frame.
