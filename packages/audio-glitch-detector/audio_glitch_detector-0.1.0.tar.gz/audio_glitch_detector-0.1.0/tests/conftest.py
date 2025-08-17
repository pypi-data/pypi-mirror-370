from pathlib import Path

import numpy as np
import pytest


@pytest.fixture
def sample_rate():
    return 48000


@pytest.fixture
def test_files_dir():
    return Path(__file__).parent.parent / "test_files"


@pytest.fixture
def mono_sine_wave(sample_rate):
    duration = 1.0
    frequency = 440.0
    samples = int(sample_rate * duration)
    t = np.linspace(0, duration, samples, False)
    return np.sin(2 * np.pi * frequency * t)


@pytest.fixture
def stereo_sine_wave(mono_sine_wave):
    return np.vstack([mono_sine_wave, mono_sine_wave])


@pytest.fixture
def sine_with_discontinuity(mono_sine_wave):
    wave = mono_sine_wave.copy()
    discontinuity_point = len(wave) // 2
    wave[discontinuity_point] = 1.0
    return wave
