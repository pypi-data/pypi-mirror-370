# Audio Glitch Detector

[![PyPI version](https://badge.fury.io/py/audio-glitch-detector.svg)](https://badge.fury.io/py/audio-glitch-detector)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Detect audio glitches and discontinuities in sinusoidal audio signals by analyzing the signal derivative.

**Important:** This tool is will only work with sinusoidal audio signals.

### Limitations
The algorithm detects discontinuities, so glitches that does not directly produce discontinuities might not be picked up.
It can detect single sample errors in a sine wave. The test files in `test_files/` show cases where the algorithm works well.

## Installation

### From PyPI
```bash
pip install audio-glitch-detector
```

### From source with uv (development)
```bash
git clone https://github.com/kaspernyhus/audio-glitch-detector
cd audio-glitch-detector
uv sync --dev
```

## Quick Start

### Command Line Usage

Analyze a WAV file with automatic threshold:
```bash
audio-glitch-detector -f path/to/audio.wav
```

Monitor live audio stream:
```bash
audio-glitch-detector
```

Save glitch blocks for analysis:
```bash
audio-glitch-detector -f audio.wav --save-blocks
```

### Library Usage

see `examples/` for usage examples.


## Visual Analysis

When using `--save-blocks`, glitch blocks (max 50) are saved as .wav files and with waveform visualizations showing the derivative analysis:

![Glitch Block Visualization](docs/glitch_block_00183478_4160ms.png)

## Test Files

Validate the detector with test files with a known number of discontinuities:
```bash
audio-glitch-detector -f test_files/sine_discont_2_mono.wav
```

Expected output:
```
Number of discontinuities detected: 2
0:00:01.892857
0:00:03.288367
```


## How It Works

1. **Derivative Analysis**: Calculates the first derivative of audio samples
2. **Threshold Detection**: Uses 99.5th percentile of derivative distribution
3. **Peak Identification**: Finds samples exceeding the threshold


## Development

### Setup
```bash
uv sync --dev
```

### Run the application
```bash
uv run audio-glitch-detector --help
```

### Run tests
```bash
uv run pytest
```
