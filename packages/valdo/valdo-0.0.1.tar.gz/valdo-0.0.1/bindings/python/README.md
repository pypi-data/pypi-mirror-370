# Valdo Python Bindings

Python bindings for Valdo, a time series anomaly detection library.

## Installation

### Prerequisites

- Python 3.10+
- Rust toolchain (for building from source)

### Install from Source

```bash
# Clone the repository
git clone https://github.com/shenxiangzhuang/valdo.git
cd valdo/bindings/python

# Install with uv (recommended)
uv sync

# Run the example
uv run python example/valdo_demo.py

# Or install with pip for system-wide use
pip install maturin
maturin develop --release
```

## Quick Start

```python
from valdo import Detector, AnomalyStatus
import random

# Create a detector with window size 10
detector = Detector(window_size=10)

# Generate training data with timestamp-value pairs (normal behavior)
training_data = [(i, random.random()) for i in range(10000)]

# Train the detector
detector.train(training_data)

# Detect anomalies in new data points
status = detector.detect(timestamp=1000, value=1.0)
print(f"Status: {status}")  # Normal

status = detector.detect(timestamp=1001, value=10.0)  
print(f"Status: {status}")  # Anomaly
```

## API Reference

### `Detector`

The main class for anomaly detection.

#### Constructor

```python
Detector(window_size, quantile=None, level=None, max_excess=None)
```

**Parameters:**
- `window_size` (int): Size of the sliding window for processing (required)
- `quantile` (float, optional): Quantile parameter for SPOT detector (default: 0.0001)
- `level` (float, optional): Level parameter for SPOT detector (default: 0.998)  
- `max_excess` (int, optional): Maximum excess for SPOT detector (default: 200)

#### Methods

##### `train(data)`

Train the detector on historical data.

**Parameters:**
- `data` (List[Tuple[int, float]]): List of (timestamp, value) pairs

**Raises:**
- `ValueError`: If training fails

##### `detect(timestamp, value)`

Detect anomalies in a new data point.

**Parameters:**
- `timestamp` (int): Timestamp of the data point
- `value` (float): Value of the data point

**Returns:**
- `AnomalyStatus`: Either `AnomalyStatus.Normal` or `AnomalyStatus.Anomaly`

**Raises:**
- `ValueError`: If detection fails

### `AnomalyStatus`

Enum representing the detection result.

- `AnomalyStatus.Normal`: The data point is normal
- `AnomalyStatus.Anomaly`: The data point is an anomaly

## Examples

### Basic Usage

```python
from valdo import Detector, AnomalyStatus

# Create detector
detector = Detector(window_size=10)

# Train on normal data with timestamps
normal_data = [(i, val) for i, val in enumerate([1.0, 1.1, 0.9, 1.05, 0.95, 1.2, 0.8, 1.15, 0.85, 1.25] * 100)]
detector.train(normal_data)

# Test detection
test_points = [
    (1000, 1.0),   # Normal
    (1001, 5.0),   # Anomaly - significantly higher
    (1002, 1.1),   # Normal
]

for timestamp, value in test_points:
    status = detector.detect(timestamp, value)
    print(f"Point ({timestamp}, {value}): {status}")
```

### Custom Parameters

```python
from valdo import Detector

# Create detector with custom parameters
detector = Detector(
    window_size=5,      # Smaller window for faster response
    quantile=0.001,     # Less sensitive to small deviations
    level=0.99,         # Lower confidence level
    max_excess=100      # Limit excess tracking
)

# Create training data and use as normal
training_data = [(i, val) for i, val in enumerate(your_values)]
detector.train(training_data)
status = detector.detect(timestamp, value)
```

### Sine Wave Example

```python
import math
from valdo import Detector

# Create detector
detector = Detector(window_size=10)

# Generate sine wave training data with timestamps and noise
training_data = [
    (i, math.sin(i * 0.1) + random.gauss(0, 0.1)) 
    for i in range(1000)
]

# Train detector
detector.train(training_data)

# Test with normal and anomalous values
test_cases = [
    (2000, math.sin(200 * 0.1)),  # Normal sine value
    (2001, 5.0),                  # Clear anomaly
    (2002, math.sin(202 * 0.1)),  # Back to normal
]

for timestamp, value in test_cases:
    status = detector.detect(timestamp, value)
    print(f"Value {value:.3f}: {status}")
```

## How It Works

Valdo uses a cascaded smoothing approach for anomaly detection:

1. **Residual Calculation**: Uses EWMA (Exponentially Weighted Moving Average) to predict the next value and calculate residuals
2. **Fluctuation Estimation**: Uses standard deviation to estimate fluctuations in the residual values
3. **Anomaly Detection**: Uses SPOT (Streaming Peaks-Over-Threshold) to detect anomalies in fluctuation changes

The detector maintains sliding windows for real-time processing and only updates its internal state when normal points are detected, preventing anomalies from corrupting the model.

## Performance

The Python bindings provide excellent performance thanks to the underlying Rust implementation:

- Training on 1M points: ~150ms
- Real-time detection: <1ms per point
- Memory efficient sliding window approach
- Thread-safe for concurrent use

## Error Handling

The bindings raise `ValueError` exceptions for various error conditions:

```python
try:
    detector = Detector(window_size=10)
    detector.train(training_data)
    status = detector.detect(timestamp, value)
except ValueError as e:
    print(f"Error: {e}")
```

## Contributing

Contributions are welcome! Please see the main repository for contribution guidelines.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

