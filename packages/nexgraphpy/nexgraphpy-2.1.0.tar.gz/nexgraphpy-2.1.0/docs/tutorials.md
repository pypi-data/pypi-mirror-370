# Tutorials

## Installation:

`pip install nexgraphpy`

## Examples:

### Import the library:

`from nexgraph import NexGraph`

### Create a new instance:

`DFT_DEVICE = NexGraph()`

### Find and connect to a Nextech force gauge over USB serial port:

#### Nextech Force Gauges:

```
if DFT_DEVICE.find():
    if DFT_DEVICE.connect():
        print(DFT_DEVICE.get_info())
        DFT_DEVICE.disconnect()
        DFT_DEVICE = None
    else:
        print("Unable to connect")
        exit()
else:
    print("No device found.")
    exit()
```

#### Other force gauges using lower baud rate:
```
if FL_DEVICE.find():
    if FL_DEVICE.connect("low"):
    ...
```

### Connect to a Nextech force gauge directly:

```
# Initialize with device the path
DFT_DEVICE = NexGraph("COM3")

# Or set the device path after initializing
DFT_DEVICE.device_path = "COM3"

# Connect to device after setting the path
if DFT_DEVICE.connect():
    ...
```

### Basic device serial operations:

#### Returns boolean value
```
# Change device modes, peak and tracking
DFT_DEVICE.mode()

# Change the units on device
DFT_DEVICE.unit()

# Reset the current device value
DFT_DEVICE.reset()

# Zero (Tare) the value on device
DFT_DEVICE.zero()
```

#### Returns string value

##### Download data from device memory
```
# Get data with no formatting
DFT_DEVICE.download()

# Get data in CSV format
DFT_DEVICE.download("csv")

# Get data as CSV and generate a chart
DFT_DEVICE.download("csv", True)

# ** Chart is saved in the script directory as "memory-data-yyyymmdd-HHMMSS.png"
```

##### Read and print values from the device

```
# Print value
DFT_DEVICE.print_value()

# Peak compression value
DFT_DEVICE.peak_compression()

# Peak tension value
DFT_DEVICE.peak_tension()

# Different formatted values
DFT_DEVICE.long_output()
DFT_DEVICE.short_output()
DFT_DEVICE.mini_output()
```

### Output live data of 100 rows:

*Note: 
The output rate is roughly 10 data points per second.
100 data points is approximately 10 seconds of testing.*

```
i = 0
while True:
    print(DFT_DEVICE.long_output())
    i += 1
    if i >= 100:
        break
```

### Find and connect to a Nextech torque tester over USB serial port:
```
if DTT_DEVICE.connect(False):
    # Output unformatted data:
    print(DTT_DEVICE.read_torque_data())
     # Output data as CSV format
    print(DTT_DEVICE.read_torque_data("csv"))
     # Output unformatted data and generate a chart
    print(DTT_DEVICE.read_torque_data("raw",True))
    ...

# ** Chart is saved in the script directory as "torque-data-yyyymmdd-HHMMSS.png"
```